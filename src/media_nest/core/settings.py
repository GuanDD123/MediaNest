from dataclasses import dataclass
from pathlib import Path

from .constant import ROOT_PATH


@dataclass(slots=True)
class Settings:
    db_path: Path

    image_suffix: set
    video_suffix: set

    thumb_mode: bool
    thumb_size: tuple[int, int]
    thumb_dirpath: Path
    image_workers: int

    hls_mode: bool  # TS, fMP4, False
    segment_dirpath: Path
    video_workers: int

    base_url: str
    m3u_item_num_limit: int


def load_settings() -> Settings:
    return Settings(
        db_path=ROOT_PATH / "media_info.db",
        image_suffix={".jpg", ".jpeg", ".png", ".gif", ".webp"},
        video_suffix={".mp4", ".avi", ".mov", ".mkv"},
        thumb_mode=True,
        thumb_size=(256, 256),
        thumb_dirpath=Path("~/Pictures_thumbnails").expanduser(),
        image_workers=16,
        hls_mode=False,
        segment_dirpath=Path("~/Segments").expanduser(),
        video_workers=4,
        base_url="http://192.168.0.110:8000",
        m3u_item_num_limit=3000,
    )
