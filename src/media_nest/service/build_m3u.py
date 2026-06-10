from pathlib import Path
from urllib.parse import quote
import random
from collections import defaultdict

from media_nest.core.constant import (
    BASE_URL,
    HLS_MODE,
    M3U_ITEM_NUM_LIMIT,
    SEGMENT_SAVE_PATH,
)
from media_nest.models import VideoSegmentInfo, VideoInfo
from media_nest.repository.repository import Repository


class BuildM3u:
    def __init__(self, repository: Repository):
        self.repository = repository

    def run(self, parent_path: Path, shuffle_flag: bool) -> str:
        if not HLS_MODE:
            return self._mp4(parent_path, shuffle_flag)
        else:
            return self._hls(parent_path, shuffle_flag)

    def _mp4(self, parent_path: Path, shuffle_flag: bool):
        video_infos: list[VideoInfo] = [
            video_info
            for video_info in self.repository.node_select_by_parent_path(
                parent_path=str(parent_path)
            )
            if video_info.type_ == "video"
        ]

        if shuffle_flag:
            random.shuffle(video_infos)

        lines = ["#EXTM3U"]
        video_num = 0
        for video_info in video_infos:
            lines.append(
                f"#EXTINF:{int(video_info.duration_ms / 1000)}, v - {video_info.name}"
            )
            lines.append(
                f"{BASE_URL}/media/video{quote(str(video_info.parent_path / video_info.name))}"
            )
            video_num += 1

            if video_num > M3U_ITEM_NUM_LIMIT:
                break
        lines.append("#EXT-X-ENDLIST")

        return "\n".join(lines)

    def _hls(self, parent_path: Path, shuffle_flag: bool) -> str:
        video_segment_infos: list[VideoSegmentInfo] = (
            self.repository.segments_select_join_node_id_by_parent_path(
                parent_path=str(parent_path)
            )
        )

        video_infos: dict[int, list[VideoSegmentInfo]] = defaultdict(list)
        for video_segment_info in video_segment_infos:
            video_infos[video_segment_info.video_id].append(video_segment_info)
        video_segment_infos_group = list(video_infos.values())

        if shuffle_flag:
            random.shuffle(video_segment_infos_group)

        if HLS_MODE == "fMP4":
            lines = [
                "#EXTM3U",
                "#EXT-X-VERSION:7",
                "#EXT-X-PLAYLIST-TYPE:VOD",
                "#EXT-X-INDEPENDENT-SEGMENTS",
            ]
        else:
            lines = ["#EXTM3U", "#EXT-X-VERSION:3"]

        first_video = True
        segment_num = 0
        for video_segment_info_group in video_segment_infos_group:
            video_segment_info_group.sort(key=lambda x: x.segment_order)

            first_segment = video_segment_info_group[0]
            hls_base = (
                SEGMENT_SAVE_PATH
                / f"{first_segment.video_dev}_{first_segment.video_ino}"
            )
            if HLS_MODE == "fMP4":
                init_url = BASE_URL + "/media/video" + quote(str(hls_base / "init.mp4"))
                if not first_video:
                    lines.append("#EXT-X-DISCONTINUITY")
                lines.append(f'#EXT-X-MAP:URI="{init_url}"')

            for segment_info in video_segment_info_group:
                lines.append(
                    f"#EXTINF:{segment_info.segment_duration_ms / 1000}, {segment_info.video_name}"
                )
                url_path = str(hls_base / segment_info.segment_name)
                lines.append(BASE_URL + "/media/video" + quote(url_path))
                segment_num += 1

            if segment_num > M3U_ITEM_NUM_LIMIT:
                break

            first_video = False

        lines.append("#EXT-X-ENDLIST")

        return "\n".join(lines)
