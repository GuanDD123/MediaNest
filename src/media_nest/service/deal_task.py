import subprocess
import json
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from functools import partial

from media_nest.core.constant import (THUMB_SIZE, THUMB_SAVE_PATH,
                                      IMAGE_WORKERS, VIDEO_WORKERS, HLS_MODE, LONG_VIDEO_MODE)
from media_nest.models.root_task_segment_info import TaskInfo, SegmentInfo
from media_nest.repository.repository import Repository


class DealTask:
    def __init__(self, repository: Repository):
        self.repository = repository

    def run(self) -> None:
        THUMB_SAVE_PATH.mkdir(exist_ok=True)

        image_update_list: list[tuple[tuple[int, int], int, int]] = []
        video_update_list: list[tuple[tuple[int, int], int, int, int]] = []

        image_tasks: list[TaskInfo] = []
        video_tasks: list[TaskInfo] = []
        for task in self.repository.task_select_all():
            if task.type_ == 'video':
                video_tasks.append(task)
            else:
                image_tasks.append(task)

        dev_ino_video_id_dict = self.repository.select_many_id_by_task_join_dev_ino()
        segment_insert_list: list[SegmentInfo] = []
        video_worker = partial(self._process_video, dev_ino_video_id_dict=dev_ino_video_id_dict)

        image_num = video_num = 0
        if image_tasks:
            with ThreadPoolExecutor(max_workers=IMAGE_WORKERS) as executor:
                for result in executor.map(self._process_image, image_tasks):
                    if result:
                        image_update_list.append(result)
                        image_num += 1
                    if image_num > 1000:
                        self.repository.update_many_image_specific_info_by_dev_ino(image_update_list)
                        image_update_list = []
                        image_num = 0
        if video_tasks:
            with ThreadPoolExecutor(max_workers=VIDEO_WORKERS) as executor:
                for result in executor.map(video_worker, video_tasks):
                    if result[0]:
                        video_update_list.append(result[0])
                        video_num += 1
                    if result[1]:
                        segment_insert_list.extend(result[1])
                    if video_num > 1000:
                        self.repository.update_many_video_specific_info_by_dev_ino(video_update_list)
                        video_update_list = []
                        video_num = 0
                    if len(segment_insert_list) > 1000:
                        self.repository.segment_insert_many(segment_insert_list)
                        segment_insert_list = []

        if video_update_list:
            self.repository.update_many_video_specific_info_by_dev_ino(video_update_list)
        if image_update_list:
            self.repository.update_many_image_specific_info_by_dev_ino(image_update_list)
        if segment_insert_list:
            self.repository.segment_insert_many(segment_insert_list)

        self.repository.task_delete_all()

    def _process_image(self, task: TaskInfo):
        try:
            with Image.open(task.path) as img:
                width = height = None
                if task.width_height_flag:
                    width, height = img.size
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                if task.thumb_flag:
                    img.draft('RGB', THUMB_SIZE)
                    img.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
                    img.save(THUMB_SAVE_PATH / f'{task.dev}_{task.ino}.jpg', 'JPEG', quality=85, optimize=True)
            if task.width_height_flag:
                return ((task.dev, task.ino), width, height)
        except Exception as e:
            if (file_size := task.path.stat().st_size) < 1024:
                print(f'[INFO] File is too small: {task.path.name} {file_size}B')
            else:
                print(f'[WARN] Failed to generate thumbnail for {task.path}: {e}')

    def _process_video(self, task: TaskInfo, dev_ino_video_id_dict):
        try:
            result = [None, None]
            if task.duration_ms_flag or not LONG_VIDEO_MODE:
                cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                       'stream=width,height,duration', '-of', 'json', str(task.path)]
                out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                stream = json.loads(out)['streams'][0]
                duration_ms = int(float(stream['duration']) * 1000)
                result[0] = ((task.dev, task.ino), int(stream['width']), int(stream['height']), duration_ms)
            else:
                duration_ms = 0
            if task.hls_flag:
                hls_dir_name = f'{task.dev}_{task.ino}'
                hls_dir = Path(f'{task.path.parent}/hls/{hls_dir_name}')
                self._build_hls(task.path, duration_ms, hls_dir)
                result[1] = self._parse_m3u8(hls_dir_name, hls_dir / 'index.m3u8', dev_ino_video_id_dict)
            return result
        except Exception as e:
            print(f'[WARN] Fail: {task.path}: {e}')

    def _build_hls(self, video_path: Path, video_duration_ms: int, hls_dir: Path):
        hls_dir.mkdir(parents=True, exist_ok=True)

        if HLS_MODE == 'fMP4':
            if LONG_VIDEO_MODE:
                hls_time = 8
                code = 'libx264'
            else:
                hls_time = 999999
                code = 'copy'
            cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(video_path),
                   '-c:v', code, '-preset', 'veryfast', '-crf', '18',
                   '-g', '48', '-keyint_min', '48', '-sc_threshold', '0', '-c:a', 'aac', '-b:a', '128k',
                   '-f', 'hls', '-hls_time', str(hls_time), '-hls_playlist_type', 'vod', '-hls_list_size', '0',
                   '-hls_flags', 'independent_segments',
                   '-hls_segment_type', 'fmp4', '-hls_fmp4_init_filename', 'init.mp4',
                   '-hls_segment_filename', str(hls_dir / 'seg_%05d.ts'), str(hls_dir / 'index.m3u8')]
        else:
            if LONG_VIDEO_MODE:
                cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(video_path),
                       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                       '-g', '48', '-keyint_min', '48', '-sc_threshold', '0', '-c:a', 'aac', '-b:a', '128k',
                       '-f', 'hls', '-hls_time', '8', '-hls_playlist_type', 'vod', '-hls_list_size', '0',
                       '-hls_flags', 'independent_segments',
                       '-hls_segment_type', 'mpegts',
                       '-hls_segment_filename', str(hls_dir / 'seg_%05d.ts'), str(hls_dir / 'index.m3u8')]
            else:
                cmd = [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video_path),
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', "-r", '30', "-vf", f"scale={1920}:{-2}",
                    "-c:a", 'aac', "-b:a", "128k",
                    "-f", "mpegts", str(hls_dir / 'video.ts')]
        subprocess.run(cmd, check=True)
        if not LONG_VIDEO_MODE and HLS_MODE == 'TS':
            lines = ['#EXTM3U',
                     '#EXT-X-VERSION:3',
                     '#EXT-X-PLAYLIST-TYPE:VOD',
                     f'#EXTINF:{video_duration_ms / 1000},',
                     'video.ts',
                     '#EXT-X-ENDLIST']
            (hls_dir / 'index.m3u8').write_text('\n'.join(lines))

    def _parse_m3u8(self, hls_dir_name: str, path: Path, dev_ino_video_id_dict: dict[str, int]):
        line_list = path.read_text().splitlines()

        segment_list = []
        line_num = 0
        order = 0

        while line_num < len(line_list):
            line = line_list[line_num]
            if line.startswith('#EXTINF'):
                duration_ms = int(float(line.split(':')[1].rstrip(',')) * 1000)
                segment_name = line_list[line_num + 1]
                segment_list.append(SegmentInfo(video_id=dev_ino_video_id_dict.get(hls_dir_name),
                                    segment_order=order, duration_ms=duration_ms, segment_name=segment_name))
                order += 1
                line_num += 2
            else:
                line_num += 1

        return segment_list
