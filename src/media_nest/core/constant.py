from pathlib import Path

NODE_KEYS = (
    "id",
    "dev",
    "ino",
    "root_id",
    "parent_path",
    "name",
    "type_",
    "size",
    "mtime",
    "duration_ms",
    "width",
    "height",
    "marked",
)
ROOT_KEYS = ("id", "path", "last_sync_time", "size")
TASK_KEYS = (
    "id",
    "type_",
    "path",
    "dev",
    "ino",
    "duration_ms_flag",
    "width_height_flag",
    "hls_flag",
    "thumb_flag",
)
SEGMENT_KEYS = ("video_id", "order_", "duration_ms", "name")

ROOT_PATH = Path(__file__).resolve().parents[3]
STATIC_PATH = ROOT_PATH / "static"
DB_PATH = ROOT_PATH / "media_info.db"
LAST_PLAYLIST = ROOT_PATH / "last_playlist.json"
LAST_PROGRESS = ROOT_PATH / "progress.txt"
LOG_PATH = ROOT_PATH / "app.log"
