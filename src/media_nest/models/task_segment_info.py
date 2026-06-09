from dataclasses import dataclass
from pathlib import Path

__all__ = ("TaskInfo", "SegmentInfo")


@dataclass(slots=True)
class TaskInfo:
    id: int
    type_: str
    path: Path
    dev: int
    ino: int
    duration_ms_flag: bool
    width_height_flag: bool
    hls_flag: bool
    thumb_flag: bool


@dataclass(slots=True)
class SegmentInfo:
    video_id: int
    order_: int
    duration_ms: int
    name: str
