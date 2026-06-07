import subprocess
import json
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

from media_nest.core.constant import (THUMB_SIZE, THUMB_SAVE_PATH,
                                      IMAGE_WORKERS, VIDEO_WORKERS)
from media_nest.models.root_task_info import TaskInfo
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
                for result in executor.map(self._process_video, video_tasks):
                    if result:
                        video_update_list.append(result)
                        video_num += 1
                    if video_num > 1000:
                        self.repository.update_many_video_specific_info_by_dev_ino(video_update_list)
                        video_update_list = []
                        video_num = 0

        if video_update_list:
            self.repository.update_many_video_specific_info_by_dev_ino(video_update_list)
        if image_update_list:
            self.repository.update_many_image_specific_info_by_dev_ino(image_update_list)

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

    def _process_video(self, task: TaskInfo):
        try:
            cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                   'stream=width,height,duration', '-of', 'json', str(task.path)]
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            stream = json.loads(out)['streams'][0]
            return ((task.dev, task.ino), int(stream['width']), int(stream['height']), int(float(stream['duration']) * 1000))
        except Exception as e:
            print(f'[WARN] Failed to get video specific info for {task.path}: {e}')
