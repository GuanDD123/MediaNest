import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Literal

from PIL import Image

from media_nest.core.settings import Settings
from media_nest.logs import logger
from media_nest.models import SegmentInfo, TaskInfo
from media_nest.repository import Repository


@dataclass(slots=True)
class TaskResult:
    node_image_update_list: list[tuple[tuple[int, int], int, int]]
    node_video_update_list: list[tuple[tuple[int, int], int, int, int]]
    segment_insert_list: list[SegmentInfo]


@dataclass(slots=True)
class Progress:
    status: Literal["idle", "running", "finished", "failed"]
    task_num: int
    successed_task_num: int
    failed_task_num: int


class DealTask:
    def __init__(self, repository: Repository, settings: Settings):
        self.repository = repository
        self.settings = settings
        self.progress = Progress(
            status="idle", task_num=0, successed_task_num=0, failed_task_num=0
        )

    def run(self) -> None:
        logger.info("Starting task processing")

        self.progress.status = "running"
        self.progress.task_num = 0
        self.progress.successed_task_num = 0
        self.progress.failed_task_num = 0

        self.settings.thumb_dirpath.mkdir(parents=True, exist_ok=True)
        self.settings.segment_dirpath.mkdir(parents=True, exist_ok=True)

        task_result = TaskResult(
            node_image_update_list=[], node_video_update_list=[], segment_insert_list=[]
        )

        image_tasks: list[TaskInfo] = []
        video_tasks: list[TaskInfo] = []
        task_infos = self.repository.task_select_all()
        self.progress.task_num = len(task_infos)
        for task in task_infos:
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
        self.progress.status = "finished"

        logger.info(
            "Task processing completed: "
            f"{self.progress.successed_task_num} tasks processed, "
            f"{self.progress.failed_task_num} tasks failed"
        )

    def _deal_image_tasks(self, image_tasks: list[TaskInfo], task_result: TaskResult):
        image_num = 0
        with ThreadPoolExecutor(max_workers=self.settings.image_workers) as executor:
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

                if node_image_infos is False:
                    self.progress.failed_task_num += 1
                else:
                    self.progress.successed_task_num += 1

    def _process_image(self, task: TaskInfo):
        try:
            with Image.open(task.path) as img:
                width = height = None
                if task.width_height_flag:
                    width, height = img.size
                if task.thumb_flag:
                    if img.mode == "RGBA":
                        img = img.convert("RGB")
                    img.draft("RGB", self.settings.thumb_size)
                    img.thumbnail(self.settings.thumb_size, Image.Resampling.LANCZOS)
                    img.save(
                        self.settings.thumb_dirpath / f"{task.dev}_{task.ino}.jpg",
                        "JPEG",
                        quality=85,
                        optimize=True,
                    )
            if task.width_height_flag:
                return ((task.dev, task.ino), width, height)
        except Exception:  # noqa: BLE001
            logger.exception(f"Failed to process image for {task.path}")
            return False

    def _deal_video_tasks(self, video_tasks: list[TaskInfo], task_result: TaskResult):
        video_ids = self.repository.node_select_id_join_task_dev_ino_by_hlsflag()
        self.repository.segment_delete_in_video_id(list(video_ids.values()))
        video_worker = partial(self._process_video, video_ids=video_ids)

        video_num = 0
        with ThreadPoolExecutor(max_workers=self.settings.video_workers) as executor:
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

                if (node_video_infos is False) or (segment_insert_list is False):
                    self.progress.failed_task_num += 1
                else:
                    self.progress.successed_task_num += 1

    def _process_video(self, task: TaskInfo, video_ids: dict[str, int]):
        node_video_infos = segment_insert_list = None
        try:
            if task.duration_ms_flag:
                out = subprocess.check_output(
                    [
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
                    ],
                    stderr=subprocess.DEVNULL,
                )
                stream = json.loads(out)["streams"][0]
                node_video_infos = (
                    (task.dev, task.ino),
                    int(stream["width"]),
                    int(stream["height"]),
                    int(float(stream["duration"]) * 1000),
                )
        except Exception:  # noqa: BLE001
            node_video_infos = False
            logger.exception(f"Failed to get video info for {task.path}")

        try:
            if task.hls_flag:
                hls_dir_name = f"{task.dev}_{task.ino}"
                hls_dir = self.settings.segment_dirpath / hls_dir_name
                self._build_hls(task.path, hls_dir)
                segment_insert_list = self._parse_m3u8(
                    video_ids.get(hls_dir_name), hls_dir / "index.m3u8"
                )
        except Exception:  # noqa: BLE001
            segment_insert_list = False
            logger.exception(f"Failed to generate HLS for {task.path}")

        return node_video_infos, segment_insert_list

    def _build_hls(self, video_path: Path, hls_dir: Path):
        if hls_dir.exists():
            shutil.rmtree(hls_dir)
        hls_dir.mkdir()

        if self.settings.hls_mode == "fMP4":
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
        subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

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
