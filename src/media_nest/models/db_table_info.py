from dataclasses import dataclass
from datetime import datetime as Datetime
from pathlib import Path

__all__ = ("NodeInfo", "RootInfo", "SegmentInfo", "TaskInfo")


@dataclass(slots=True)
class NodeInfo:
    id: int
    dev: int
    ino: int
    root_id: int
    parent_path: Path
    name: str
    type_: str
    size: int
    mtime: Datetime
    width: int | None = None
    height: int | None = None
    duration_ms: int | None = None
    marked: bool = False


@dataclass(slots=True)
class RootInfo:
    id: int
    path: Path
    last_sync_time: Datetime
    size: int


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
