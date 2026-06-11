from pathlib import Path

THUMB_MODE = True
THUMB_SIZE = (256, 256)
THUMB_SAVE_PATH = Path("/Media/thumbnails")

IMAGE_WORKERS = 16
VIDEO_WORKERS = 4

ROOT_PATH = Path(__file__).resolve().parents[3]
DB_PATH = ROOT_PATH / "media_info.db"
STATIC_PATH = ROOT_PATH / "static"
LAST_PLAYLIST = ROOT_PATH / "last_playlist.json"
LAST_PROGRESS = ROOT_PATH / "progress.txt"

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
    "marked"
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

BASE_URL = "http://192.168.0.110:8000"

HLS_MODE = False  # TS, fMP4, False
M3U_ITEM_NUM_LIMIT = 3000
SEGMENT_SAVE_PATH = Path("/Media/segments")

IMAGE_SUFFIX = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_SUFFIX = {".mp4", ".avi", ".mov", ".mkv"}
