from pathlib import Path
from urllib.parse import quote
import random

from media_nest.core.constant import BASE_URL, HLS_MODE
from media_nest.repository.repository import Repository


class BuildM3u:
    def __init__(self, repository: Repository):
        self.repository = repository

    def run(self, parent_path: Path, shuffle_flag: bool) -> str:
        video_info_list = self.repository.select_all_by_parent_path(parent_path=parent_path)

        if shuffle_flag:
            random.shuffle(video_info_list)

        lines = ['#EXTM3U']
        for video_info in video_info_list:
            if video_info.type_ == 'video':
                video_name = video_info.name
                if HLS_MODE:
                    url_path = f'{str(video_info.parent_path)}/hls/{video_info.dev}_{video_info.ino}/index.m3u8'
                else:
                    url_path = f'{str(video_info.parent_path)}/{video_name}'
                lines.append(f'#EXTINF:{int(video_info.duration_ms / 1000)}, v - {video_name}')
                lines.append(BASE_URL + '/media/video' + quote(url_path))

        return '\n'.join(lines)
