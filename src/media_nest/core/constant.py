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
LAST_PLAYLIST = ROOT_PATH / "last_playlist.json"
LAST_PROGRESS = ROOT_PATH / "progress.txt"


# 可选配置项
DB_PATH = ROOT_PATH / "media_info.db"

IMAGE_SUFFIX = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_SUFFIX = {".mp4", ".avi", ".mov", ".mkv"}

THUMB_MODE = True
THUMB_SIZE = (256, 256)
THUMB_SAVE_PATH = Path("~/Pictures_thumbnails").expanduser()
IMAGE_WORKERS = 16

HLS_MODE = False  # TS, fMP4, False
SEGMENT_SAVE_PATH = Path("~/Segments").expanduser()
VIDEO_WORKERS = 4

BASE_URL = "http://192.168.0.110:8000"
M3U_ITEM_NUM_LIMIT = 3000
