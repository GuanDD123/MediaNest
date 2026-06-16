from dataclasses import dataclass
from datetime import datetime as Datetime
from pathlib import Path

__all__ = ("NodeInfo",)


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
