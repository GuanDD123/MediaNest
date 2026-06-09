from pathlib import Path

from media_nest.core.db_manager import DataBaseManager
from media_nest.core.constant import NODE_KEY, ROOT_KEY, TASK_KEY, SEGMENT_KEY
from media_nest.models import (
    FolderInfo,
    VideoInfo,
    ImageInfo,
    RootInfo,
    TaskInfo,
    SegmentInfo,
    VideoSegmentInfo,
)
from .tool import row_to_model, model_to_row

__all__ = ["Repository"]


class Select:
    def root_select_all(self) -> list[RootInfo]:
        return self._select_all(table="root")

    def node_select_all(self) -> list[FolderInfo | VideoInfo | ImageInfo]:
        return self._select_all(table="node")

    def task_select_all(self) -> list[TaskInfo]:
        return self._select_all(table="task")

    def segment_select_all(self) -> list[SegmentInfo]:
        return self._select_all(table="segment")

    def _select_all(self, table: str):
        cursor = self.database.connection.execute(f"SELECT * FROM {table}")
        return [row_to_model(table, row) for row in cursor.fetchall() if row]

    def node_select_by_id(self, id: int) -> FolderInfo | VideoInfo | ImageInfo | None:
        sql = "SELECT * FROM node WHERE id = ?"
        cursor = self.database.connection.execute(sql, (id,))
        if info := cursor.fetchone():
            return row_to_model("node", info)
        return None

    def node_select_by_dev_ino(
        self, dev: int, ino: int
    ) -> FolderInfo | VideoInfo | ImageInfo | None:
        sql = "SELECT * FROM node WHERE dev = ? AND ino = ?"
        cursor = self.database.connection.execute(sql, (dev, ino))
        if info := cursor.fetchone():
            return row_to_model("node", info)
        return None

    def node_select_by_parent_path(
        self, parent_path_str: str
    ) -> list[FolderInfo | VideoInfo | ImageInfo]:
        sql = "SELECT * FROM node WHERE parent_path = ? ORDER BY name"
        cursor = self.database.connection.execute(sql, (parent_path_str,))
        return [row_to_model("node", row) for row in cursor.fetchall() if row]

    def node_select_in_id(
        self, id_list: list[int]
    ) -> list[FolderInfo | VideoInfo | ImageInfo]:
        sql = f"SELECT * FROM node WHERE id IN ({','.join('?' * len(id_list))})"
        cursor = self.database.connection.execute(sql, id_list)
        return [row_to_model("node", row) for row in cursor.fetchall() if row]

    def node_select_in_dev_ino(
        self, dev_ino_list: list[tuple[int, int]]
    ) -> list[FolderInfo | VideoInfo | ImageInfo]:
        sql = f"SELECT * FROM node WHERE (dev, ino) IN ({','.join(('(?,?)' for _ in range(len(dev_ino_list))))})"
        param_list = [param for dev_ino in dev_ino_list for param in dev_ino]
        cursor = self.database.connection.execute(sql, param_list)
        return [row_to_model("node", row) for row in cursor.fetchall() if row]

    def node_select_id_join_task_dev_ino_by_hlsflag(self) -> dict[str, int]:
        sql = """SELECT n.id, t.dev, t.ino FROM node n JOIN task t
                ON n.dev = t.dev AND n.ino = t.ino
                WHERE t.hls_flag = 1"""
        cursor = self.database.connection.execute(sql)
        return {f"{row[1]}_{row[2]}": row[0] for row in cursor.fetchall() if row}

    def segments_select_join_node_id_by_parent_path(
        self, parent_path_str: str
    ) -> list[VideoSegmentInfo]:
        sql = """SELECT s.order_num, s.name, s.duration_ms, n.id, n.dev, n.ino, n.parent_path, n.name
                        FROM segment s JOIN node n ON s.video_id = n.id
                        WHERE n.parent_path = ?
                        ORDER BY n.id, s.order_num"""
        cursor = self.database.connection.execute(sql, (parent_path_str,))
        return [
            VideoSegmentInfo(
                video_id=row[3],
                video_dev=row[4],
                video_ino=row[5],
                video_parent_path=Path(row[6]),
                video_name=row[7],
                segment_order=row[0],
                segment_name=row[1],
                segment_duration_ms=row[2],
            )
            for row in cursor.fetchall()
            if row
        ]


class Insert:
    insert_placeholder = {
        "node": "(" + ",".join((key for key in NODE_KEY[1:])) + ")",
        "root": "(" + ",".join((key for key in ROOT_KEY[1:])) + ")",
        "task": "(" + ",".join((key for key in TASK_KEY[1:])) + ")",
        "segment": "(" + ",".join((key for key in SEGMENT_KEY)) + ")",
    }
    values_placeholder = {
        "node": "(" + ",".join("?" * (len(NODE_KEY) - 1)) + ")",
        "root": "(" + ",".join("?" * (len(ROOT_KEY) - 1)) + ")",
        "task": "(" + ",".join("?" * (len(TASK_KEY) - 1)) + ")",
        "segment": "(" + ",".join("?" * len(SEGMENT_KEY)) + ")",
    }

    def root_insert(self, info: RootInfo) -> bool:
        return self._insert("root", info=info)

    def node_insert(self, info: FolderInfo | VideoInfo | ImageInfo) -> bool:
        return self._insert("node", info=info)

    def task_insert(self, info: TaskInfo) -> bool:
        return self._insert("task", info=info)

    def _insert(
        self,
        table: str,
        info: FolderInfo | VideoInfo | ImageInfo | RootInfo | TaskInfo | SegmentInfo,
    ):
        sql = f"INSERT INTO {table} {self.insert_placeholder[table]} VALUES {self.values_placeholder[table]}"
        with self.database.connection as connection:
            param_tuple = model_to_row(table, info)
            cursor = connection.execute(sql, param_tuple)
        return True if cursor.rowcount else False

    def node_insert_many(
        self, info_list: list[FolderInfo | VideoInfo | ImageInfo]
    ) -> bool:
        return self._insert_many("node", info_list=info_list)

    def task_insert_many(self, info_list: list[TaskInfo]) -> bool:
        return self._insert_many("task", info_list=info_list)

    def segment_insert_many(self, info_list: list[SegmentInfo]) -> bool:
        return self._insert_many("segment", info_list=info_list)

    def _insert_many(
        self,
        table: str,
        info_list: list[
            FolderInfo | VideoInfo | ImageInfo | RootInfo | TaskInfo | SegmentInfo
        ],
    ):
        sql = f"INSERT INTO {table} {self.insert_placeholder[table]} VALUES {self.values_placeholder[table]}"
        with self.database.connection as connection:
            param = ((model_to_row(table, info)) for info in info_list)
            cursor = connection.executemany(sql, param)
        return True if cursor.rowcount else False


class Update:
    update_placeholder = {
        "node": ",".join((f"{key}=?" for key in NODE_KEY[1:])),
        "root": ",".join((f"{key}=?" for key in ROOT_KEY[1:])),
        "task": ",".join((f"{key}=?" for key in TASK_KEY[1:])),
        "segment": ",".join((f"{key}=?" for key in SEGMENT_KEY)),
    }

    def root_update_by_id(self, id: int, info: RootInfo) -> bool:
        return self._update_by_id("root", id=id, info=info)

    def node_update_by_id(
        self, id: int, info: FolderInfo | VideoInfo | ImageInfo
    ) -> bool:
        return self._update_by_id("node", id=id, info=info)

    def _update_by_id(
        self,
        table: str,
        id: int,
        info: FolderInfo | VideoInfo | ImageInfo | RootInfo | SegmentInfo,
    ):
        sql = f"UPDATE {table} SET {self.update_placeholder[table]} WHERE id = ?"
        with self.database.connection as connection:
            param_tuple = (*model_to_row(table, info), id)
            cursor = connection.execute(sql, param_tuple)
        return True if cursor.rowcount else False

    def node_update_many_by_id(
        self, update_list: list[tuple[int, FolderInfo | VideoInfo | ImageInfo]]
    ) -> bool:
        sql = f"UPDATE node SET {self.update_placeholder['node']} WHERE id = ?"
        with self.database.connection as connection:
            param = ((*model_to_row("node", info), id) for id, info in update_list)
            cursor = connection.executemany(sql, param)
        return True if cursor.rowcount else False

    def node_update_many_width_height_by_dev_ino(
        self, update_list: list[tuple[tuple[int, int], int, int]]
    ) -> bool:
        sql = """UPDATE node SET width = ?, height = ? WHERE dev = ? AND ino = ?"""
        with self.database.connection as connection:
            param = (
                (width, height, dev, ino) for (dev, ino), width, height in update_list
            )
            cursor = connection.executemany(sql, param)
        return True if cursor.rowcount else False

    def node_update_many_width_height_duration_by_dev_ino(
        self, update_list: list[tuple[tuple[int, int], int, int, int]]
    ) -> bool:
        sql = """UPDATE node SET width = ?, height = ?, duration_ms = ? WHERE dev = ? AND ino = ?"""
        with self.database.connection as connection:
            param = (
                (width, height, duration_ms, dev, ino)
                for (dev, ino), width, height, duration_ms in update_list
            )
            cursor = connection.executemany(sql, param)
        return True if cursor.rowcount else False


class Delete:
    def root_delete_by_id(self, id: int) -> bool:
        return self._delete_by_id("root", id=id)

    def node_delete_by_id(self, id: int) -> bool:
        return self._delete_by_id("node", id=id)

    def _delete_by_id(self, table: str, id: int):
        sql = f"DELETE FROM {table} WHERE id = ?"
        with self.database.connection as connection:
            cursor = connection.execute(sql, (id,))
        return True if cursor.rowcount else False

    def node_delete_in_id(self, id_list: list[int]) -> bool:
        sql = f"""DELETE FROM node WHERE id IN ({",".join("?" * len(id_list))})"""
        with self.database.connection as connection:
            cursor = connection.execute(sql, id_list)
        return True if cursor.rowcount else False

    def task_delete_all(self) -> bool:
        return self._delete_all("task")

    def segment_delete_all(self) -> bool:
        return self._delete_all("segment")

    def node_delete_all(self) -> bool:
        return self._delete_all("node")

    def root_delete_all(self) -> bool:
        return self._delete_all("root")

    def _delete_all(self, table: str):
        with self.database.connection as connection:
            cursor = connection.execute(f"DELETE FROM {table}")
        return True if cursor.rowcount else False


class Repository(Select, Insert, Update, Delete):
    def __init__(self, database: DataBaseManager):
        self.database = database
