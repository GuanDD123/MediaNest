from pathlib import Path
from urllib.parse import quote
import random

from media_nest.core.constant import BASE_URL
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
                lines.append(f'#EXTINF:{int(video_info.duration_ms / 1000)}, v - {video_info.name}')
                lines.append(f'{BASE_URL}/media/video{quote(str(video_info.parent_path / video_info.name))}')

        return '\n'.join(lines)
