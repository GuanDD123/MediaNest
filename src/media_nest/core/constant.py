from pathlib import Path

THUMB_MODE = True
THUMB_SIZE = (256, 256)
THUMB_SAVE_PATH = Path("/Media/thumbnails")

IMAGE_WORKERS = 16
VIDEO_WORKERS = 4

ROOT_PATH = Path(__file__).resolve().parents[3]
DB_PATH = ROOT_PATH / "media_info.db"
STATIC_PATH = ROOT_PATH / "static"

NODE_KEY = (
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
)
ROOT_KEY = ("id", "path", "last_sync_at")
TASK_KEY = (
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
SEGMENT_KEY = ("video_id", "order_num", "duration_ms", "name")

BASE_URL = "http://192.168.0.110:8000"

HLS_MODE = False  # TS, fMP4, False
M3U_SEGMENT_NUM = 300
