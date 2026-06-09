from dataclasses import dataclass
from pathlib import Path

__all__ = ("VideoSegmentInfo",)


@dataclass(slots=True)
class VideoSegmentInfo:
    video_id: int
    video_parent_path: Path
    video_name: str
    video_dev: int
    video_ino: int
    segment_order: int
    segment_name: str
    segment_duration_ms: int
