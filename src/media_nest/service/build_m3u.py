import random
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

from media_nest.core.settings import Settings
from media_nest.models import NodeInfo, VideoSegmentInfo
from media_nest.repository import Repository


class BuildM3u:
    def __init__(self, repository: Repository, settings: Settings):
        self.repository = repository
        self.settings = settings

    def run(self, parent_path: Path, shuffle_flag: bool) -> str:
        if not self.settings.hls_mode:
            return self._mp4(parent_path, shuffle_flag)
        else:
            return self._hls(parent_path, shuffle_flag)

    def _mp4(self, parent_path: Path, shuffle_flag: bool):
        video_infos: list[NodeInfo] = [
            video_info
            for video_info in self.repository.node_select_by_parent_path(
                str(parent_path)
            )
            if video_info.type_ == "video"
        ]

        if shuffle_flag:
            random.shuffle(video_infos)

        lines = ["#EXTM3U"]
        for index, video_info in enumerate(video_infos, start=1):
            lines.append(
                f"#EXTINF:{int(video_info.duration_ms / 1000)}, v - {video_info.name}"
            )
            lines.append(
                f"{self.settings.base_url}/media/video{quote(str(video_info.parent_path / video_info.name))}"
            )

            if index > self.settings.m3u_item_num_limit:
                break
        lines.append("#EXT-X-ENDLIST")

        return "\n".join(lines)

    def _hls(self, parent_path: Path, shuffle_flag: bool) -> str:
        video_segment_infos: list[VideoSegmentInfo] = (
            self.repository.segments_select_join_node_id_by_parent_path(
                str(parent_path)
            )
        )

        video_infos: dict[int, list[VideoSegmentInfo]] = defaultdict(list)
        for video_segment_info in video_segment_infos:
            video_infos[video_segment_info.video_id].append(video_segment_info)
        video_segment_infos_group = list(video_infos.values())

        if shuffle_flag:
            random.shuffle(video_segment_infos_group)

        if self.settings.hls_mode == "fMP4":
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
                self.settings.segment_dirpath
                / f"{first_segment.video_dev}_{first_segment.video_ino}"
            )
            if self.settings.hls_mode == "fMP4":
                init_url = (
                    self.settings.base_url
                    + "/media/video"
                    + quote(str(hls_base / "init.mp4"))
                )
                if not first_video:
                    lines.append("#EXT-X-DISCONTINUITY")
                lines.append(f'#EXT-X-MAP:URI="{init_url}"')

            for segment_info in video_segment_info_group:
                lines.append(
                    f"#EXTINF:{segment_info.segment_duration_ms / 1000}, {segment_info.video_name}"
                )
                url_path = str(hls_base / segment_info.segment_name)
                lines.append(self.settings.base_url + "/media/video" + quote(url_path))
                segment_num += 1

            if segment_num > self.settings.m3u_item_num_limit:
                break

            first_video = False

        lines.append("#EXT-X-ENDLIST")

        return "\n".join(lines)
