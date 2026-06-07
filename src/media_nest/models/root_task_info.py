from dataclasses import dataclass
from datetime import datetime as Datetime
from pathlib import Path


@dataclass(slots=True)
class RootInfo:
    id: int
    path: Path
    last_sync_at: Datetime


@dataclass(slots=True)
class TaskInfo:
    id: int
    type_: str
    path: Path
    dev: int
    ino: int
    duration_ms_flag: bool
    width_height_flag: bool
    thumb_flag: bool
