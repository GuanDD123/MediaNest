import subprocess
import json
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from functools import partial
from dataclasses import dataclass
import shutil

from media_nest.core.constant import (
    THUMB_SIZE,
    THUMB_SAVE_PATH,
    IMAGE_WORKERS,
    VIDEO_WORKERS,
    HLS_MODE,
    SEGMENT_SAVE_PATH,
)
from media_nest.models import TaskInfo, SegmentInfo
from media_nest.repository import Repository


@dataclass(slots=True)
class TaskResult:
    node_image_update_list: list[tuple[tuple[int, int], int, int]]
    node_video_update_list: list[tuple[tuple[int, int], int, int, int]]
    segment_insert_list: list[SegmentInfo]


class DealTask:
    def __init__(self, repository: Repository):
        self.repository = repository

    def run(self) -> None:
        THUMB_SAVE_PATH.mkdir(parents=True, exist_ok=True)
        SEGMENT_SAVE_PATH.mkdir(parents=True, exist_ok=True)

        task_result = TaskResult(
            node_image_update_list=[], node_video_update_list=[], segment_insert_list=[]
        )

        image_tasks: list[TaskInfo] = []
        video_tasks: list[TaskInfo] = []
        for task in self.repository.task_select_all():
            if task.type_ == "video":
                video_tasks.append(task)
            else:
                image_tasks.append(task)

        if image_tasks:
            self._deal_image_tasks(image_tasks, task_result)
        if video_tasks:
            self._deal_video_tasks(video_tasks, task_result)
        self._sync_to_db(task_result)

        self.repository.task_delete_all()

    def _deal_image_tasks(self, image_tasks: list[TaskInfo], task_result: TaskResult):
        image_num = 0
        with ThreadPoolExecutor(max_workers=IMAGE_WORKERS) as executor:
            for node_image_infos in executor.map(self._process_image, image_tasks):
                if node_image_infos:
                    task_result.node_image_update_list.append(node_image_infos)
                    image_num += 1
                if image_num > 1000:
                    self.repository.node_update_many_width_height_by_dev_ino(
                        task_result.node_image_update_list
                    )
                    task_result.node_image_update_list = []
                    image_num = 0

    def _process_image(self, task: TaskInfo):
        try:
            with Image.open(task.path) as img:
                width = height = None
                if task.width_height_flag:
                    width, height = img.size
                if task.thumb_flag:
                    if img.mode == "RGBA":
                        img = img.convert("RGB")
                    img.draft("RGB", THUMB_SIZE)
                    img.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
                    img.save(
                        THUMB_SAVE_PATH / f"{task.dev}_{task.ino}.jpg",
                        "JPEG",
                        quality=85,
                        optimize=True,
                    )
            if task.width_height_flag:
                return ((task.dev, task.ino), width, height)
        except Exception as e:
            if (file_size := task.path.stat().st_size) < 1024:
                print(f"[INFO] File is too small: {task.path.name} {file_size}B")
            else:
                print(f"[WARN] Failed to generate thumbnail for {task.path}: {e}")

    def _deal_video_tasks(self, video_tasks: list[TaskInfo], task_result: TaskResult):
        video_ids = self.repository.node_select_id_join_task_dev_ino_by_hlsflag()
        self.repository.segment_delete_in_video_id(list(video_ids.values()))
        video_worker = partial(self._process_video, video_ids=video_ids)

        video_num = 0
        with ThreadPoolExecutor(max_workers=VIDEO_WORKERS) as executor:
            for node_video_infos, segment_insert_list in executor.map(
                video_worker, video_tasks
            ):
                if node_video_infos:
                    task_result.node_video_update_list.append(node_video_infos)
                    video_num += 1
                if segment_insert_list:
                    task_result.segment_insert_list.extend(segment_insert_list)
                if video_num > 1000:
                    self.repository.node_update_many_width_height_duration_by_dev_ino(
                        task_result.node_video_update_list
                    )
                    task_result.node_video_update_list = []
                    video_num = 0
                if len(task_result.segment_insert_list) > 1000:
                    self.repository.segment_insert_many(task_result.segment_insert_list)
                    task_result.segment_insert_list = []

    def _process_video(self, task: TaskInfo, video_ids: dict[str, int]):
        node_video_infos = segment_insert_list = None
        try:
            if task.duration_ms_flag:
                cmd = [
                    "ffprobe",
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=width,height,duration",
                    "-of",
                    "json",
                    str(task.path),
                ]
                out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                stream = json.loads(out)["streams"][0]
                node_video_infos = (
                    (task.dev, task.ino),
                    int(stream["width"]),
                    int(stream["height"]),
                    int(float(stream["duration"]) * 1000),
                )
            if task.hls_flag:
                hls_dir_name = f"{task.dev}_{task.ino}"
                hls_dir = SEGMENT_SAVE_PATH / hls_dir_name
                self._build_hls(task.path, hls_dir)
                segment_insert_list = self._parse_m3u8(
                    video_ids.get(hls_dir_name), hls_dir / "index.m3u8"
                )
        except Exception as e:
            print(f"[WARN] Fail: {task.path}: {e}")
        finally:
            return node_video_infos, segment_insert_list

    def _build_hls(self, video_path: Path, hls_dir: Path):
        if hls_dir.exists():
            shutil.rmtree(hls_dir)
        hls_dir.mkdir()

        if HLS_MODE == "fMP4":
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(video_path),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "18",
                "-g",
                "48",
                "-keyint_min",
                "48",
                "-sc_threshold",
                "0",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-f",
                "hls",
                "-hls_time",
                "8",
                "-hls_playlist_type",
                "vod",
                "-hls_list_size",
                "0",
                "-hls_flags",
                "independent_segments",
                "-hls_segment_type",
                "fmp4",
                "-hls_fmp4_init_filename",
                "init.mp4",
                "-hls_segment_filename",
                str(hls_dir / "seg_%05d.m4s"),
                str(hls_dir / "index.m3u8"),
            ]
        else:  # TS
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(video_path),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "18",
                "-g",
                "48",
                "-keyint_min",
                "48",
                "-sc_threshold",
                "0",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-f",
                "hls",
                "-hls_time",
                "8",
                "-hls_playlist_type",
                "vod",
                "-hls_list_size",
                "0",
                "-hls_flags",
                "independent_segments",
                "-hls_segment_type",
                "mpegts",
                "-hls_segment_filename",
                str(hls_dir / "seg_%05d.ts"),
                str(hls_dir / "index.m3u8"),
            ]
        subprocess.run(cmd, check=True)

    def _parse_m3u8(self, video_id: int, path: Path):
        line_list = path.read_text().splitlines()

        segment_list: list[SegmentInfo] = []
        line_num = order = 0

        while line_num < len(line_list):
            line = line_list[line_num]
            if line.startswith("#EXTINF"):
                duration_ms = int(float(line.split(":")[1].rstrip(",")) * 1000)
                segment_name = line_list[line_num + 1]
                segment_list.append(
                    SegmentInfo(
                        video_id=video_id,
                        order_=order,
                        duration_ms=duration_ms,
                        name=segment_name,
                    )
                )
                order += 1
                line_num += 2
            else:
                line_num += 1

        return segment_list

    def _sync_to_db(self, task_result: TaskResult):
        if task_result.node_video_update_list:
            self.repository.node_update_many_width_height_duration_by_dev_ino(
                task_result.node_video_update_list
            )
        if task_result.node_image_update_list:
            self.repository.node_update_many_width_height_by_dev_ino(
                task_result.node_image_update_list
            )

        if task_result.segment_insert_list:
            self.repository.segment_insert_many(task_result.segment_insert_list)
