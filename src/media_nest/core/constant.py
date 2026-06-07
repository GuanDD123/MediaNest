from pathlib import Path

THUMB_SIZE = (256, 256)
THUMB_SAVE_PATH = Path('/Media/thumbnails')

IMAGE_WORKERS = 16
VIDEO_WORKERS = 4

DB_PATH = Path(__file__).resolve().parents[3] / 'media_info.db'

NODE_KEY = ('id', 'dev', 'ino', 'root_id', 'parent_path', 'name', 'type_', 'size', 'mtime', 'duration_ms', 'width', 'height')
ROOT_KEY = ('id', 'path', 'last_sync_at')
TASK_KEY = ('id', 'type_', 'path', 'dev', 'ino', 'duration_ms_flag', 'width_height_flag', 'thumb_flag')
