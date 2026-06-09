from pathlib import Path
from urllib.parse import quote
import random
from collections import defaultdict

from media_nest.core.constant import BASE_URL, HLS_MODE, M3U_SEGMENT_NUM
from media_nest.models.video_segment_info import VideoSegmentInfo
from media_nest.repository.repository import Repository


class BuildM3u:
    def __init__(self, repository: Repository):
        self.repository = repository

    def run(self, parent_path: Path, shuffle_flag: bool) -> str:
        if HLS_MODE:
            return self._hls(parent_path, shuffle_flag)
        else:
            return self._mp4(parent_path, shuffle_flag)

    def _mp4(self, parent_path: Path, shuffle_flag: bool):
        video_info_list = self.repository.select_all_by_parent_path(parent_path=parent_path)

        if shuffle_flag:
            random.shuffle(video_info_list)

        lines = ['#EXTM3U']
        for video_info in video_info_list:
            if video_info.type_ == 'video':
                lines.append(f'#EXTINF:{int(video_info.duration_ms / 1000)}, v - {video_info.name}')
                lines.append(f'{BASE_URL}/media/video{quote(str(video_info.parent_path / video_info.name))}')

        return '\n'.join(lines)

    def _hls(self, parent_path: Path, shuffle_flag: bool) -> str:
        if HLS_MODE:
            segment_video_info_list = self.repository.segments_select_many_join_video_id_by_parent_path(
                parent_path=parent_path)

        video_info_dict: dict[int, list[VideoSegmentInfo]] = defaultdict(list)
        for segment_video_info in segment_video_info_list:
            video_info_dict[segment_video_info.video_id].append(segment_video_info)
        video_info_list = list(video_info_dict.values())

        if shuffle_flag:
            random.shuffle(video_info_list)

        if HLS_MODE == 'fMP4':
            lines = ["#EXTM3U", "#EXT-X-VERSION:7",
                     "#EXT-X-PLAYLIST-TYPE:VOD", "#EXT-X-INDEPENDENT-SEGMENTS",]
        elif HLS_MODE:
            lines = ['#EXTM3U', '#EXT-X-VERSION:3']
        first_video = True
        segment_num = 0
        for segment_group in video_info_list:
            segment_group.sort(key=lambda x: x.segment_order)

            if HLS_MODE:
                first_segment = segment_group[0]
                hls_base = (f'{first_segment.video_parent_path}/hls/{first_segment.video_dev}_{first_segment.video_ino}')
                if HLS_MODE == 'fMP4':
                    init_url = BASE_URL + '/media/video' + quote(f'{hls_base}/init.mp4')
                    if not first_video:
                        lines.append("#EXT-X-DISCONTINUITY")
                    lines.append(f'#EXT-X-MAP:URI="{init_url}"')

            for segment in segment_group:
                lines.append(f'#EXTINF:{segment.segment_duration_ms / 1000}, {segment.video_name}')
                url_path = (f'{hls_base}/{segment.segment_name}')
                lines.append(BASE_URL + '/media/video' + quote(url_path))
                segment_num += 1

            if segment_num > M3U_SEGMENT_NUM:
                break

            first_video = False
        lines.append('#EXT-X-ENDLIST')

        return '\n'.join(lines)
