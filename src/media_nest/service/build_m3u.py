from pathlib import Path
from urllib.parse import quote
import random
from collections import defaultdict

from media_nest.core.constant import BASE_URL, HLS_MODE
from media_nest.models.node_join_segment import NodeJoinSegment
from media_nest.repository.repository import Repository


class BuildM3u:
    def __init__(self, repository: Repository):
        self.repository = repository

    def run(self, parent_path: Path, shuffle_flag: bool) -> str:
        segment_video_info_list = self.repository.segments_select_many_join_video_id_by_parent_path(
            parent_path=parent_path)

        video_info_dict: dict[int, list[NodeJoinSegment]] = defaultdict(list)
        for segment_video_info in segment_video_info_list:
            video_info_dict[segment_video_info.video_id].append(segment_video_info)
        video_info_list = list(video_info_dict.values())

        if shuffle_flag:
            random.shuffle(video_info_list)

        if HLS_MODE == 'fMP4':
            lines = ["#EXTM3U", "#EXT-X-VERSION:7",
                     "#EXT-X-PLAYLIST-TYPE:VOD", "#EXT-X-INDEPENDENT-SEGMENTS",]
        else:
            lines = ['#EXTM3U', '#EXT-X-VERSION:3']
        first_video = True
        for segment_group in video_info_list:
            segment_group.sort(key=lambda x: x.segment_order)

            if HLS_MODE:
                first_segment = segment_group[0]
                hls_base = (f'{first_segment.video_parent_path}/hls/{first_segment.video_dev}_{first_segment.video_ino}')
                if HLS_MODE == 'fMP4':
                    init_url = BASE_URL + '/media/video/' + quote(f'{hls_base}/init.mp4')
                    if not first_video:
                        lines.append("#EXT-X-DISCONTINUITY")
                    lines.append(f'#EXT-X-MAP:URI="{init_url}"')

            for segment in segment_group:
                lines.append(f'#EXTINF:{segment.segment_duration_ms / 1000}, {segment.video_name}')
                if HLS_MODE:
                    url_path = (f'{hls_base}/{segment.segment_name}')
                else:
                    url_path = f'{segment.video_parent_path}/{segment.video_name}'
                lines.append(BASE_URL + '/media/video/' + quote(url_path))
                
            first_video = False
        lines.append('#EXT-X-ENDLIST')

        return '\n'.join(lines)
