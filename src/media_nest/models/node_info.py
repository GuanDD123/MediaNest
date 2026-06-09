from dataclasses import dataclass
from datetime import datetime as Datetime
from pathlib import Path

__all__ = ("FolderInfo", "VideoInfo", "ImageInfo")


@dataclass(slots=True)
class CommonInfo:
    id: int
    dev: int
    ino: int
    root_id: int
    parent_path: Path
    name: str
    type_: str
    size: int
    mtime: Datetime


@dataclass(slots=True)
class FolderInfo(CommonInfo):
    pass


@dataclass(slots=True)
class MediaInfo(CommonInfo):
    width: int | None
    height: int | None


@dataclass(slots=True)
class VideoInfo(MediaInfo):
    duration_ms: int | None


@dataclass(slots=True)
class ImageInfo(MediaInfo):
    pass
