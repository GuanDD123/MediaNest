from pathlib import Path
import sqlite3


class DataBaseManager:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.connection = None

    def connect(self) -> None:
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)

    def close(self) -> None:
        if self.connection:
            self.connection.close()

    def init(self) -> None:
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS root (id INTEGER PRIMARY KEY,
                                      path TEXT NOT NULL UNIQUE,
                                      last_sync_time INTEGER NOT NULL,
                                      size INTEGER NOT NULL
                                      );
            CREATE TABLE IF NOT EXISTS node (id INTEGER PRIMARY KEY,
                                dev INTEGER NOT NULL, ino INTEGER NOT NULL,
                                root_id INTEGER NOT NULL,
                                parent_path TEXT NOT NULL, name TEXT NOT NULL,
                                type_ TEXT NOT NULL CHECK(type_ IN ('folder', 'video', 'image')),
                                size INTEGER NOT NULL,
                                mtime INTEGER NOT NULL,
                                duration_ms INTEGER,
                                width INTEGER, height INTEGER,
                                marked INTEGER NOT NULL CHECK(marked IN (0, 1))
                                      );
            CREATE TABLE IF NOT EXISTS task (id INTEGER PRIMARY KEY,
                                type_ TEXT NOT NULL CHECK(type_ IN ('folder', 'video', 'image')),
                                path TEXT NOT NULL,
                                dev INTEGER NOT NULL, ino INTEGER NOT NULL,
                                duration_ms_flag INTEGER NOT NULL CHECK(duration_ms_flag IN (0, 1)),
                                width_height_flag INTEGER NOT NULL CHECK(width_height_flag IN (0, 1)),
                                hls_flag INTEGER NOT NULL CHECK(hls_flag IN (0, 1)),
                                thumb_flag INTEGER NOT NULL CHECK(thumb_flag IN (0, 1))
                                );
            CREATE TABLE IF NOT EXISTS segment (
                                      video_id INTEGER NOT NULL,
                                      order_ INTEGER NOT NULL,
                                      duration_ms INTEGER NOT NULL,
                                      name TEXT NOT NULL,
                                      PRIMARY KEY (video_id, order_),
                                      FOREIGN KEY(video_id) REFERENCES node(id) ON DELETE CASCADE
                                      );
            CREATE UNIQUE INDEX IF NOT EXISTS index_node_dev_ino ON node(dev, ino);
            CREATE INDEX IF NOT EXISTS index_node_parent_path ON node(parent_path);
            CREATE INDEX IF NOT EXISTS index_node_name ON node(name);
            CREATE INDEX IF NOT EXISTS index_segment_video_id ON segment(video_id);
            """)
