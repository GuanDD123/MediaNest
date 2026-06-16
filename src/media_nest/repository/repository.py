from pathlib import Path

from media_nest.core.db_manager import DataBaseManager
from media_nest.core.constant import NODE_KEYS, ROOT_KEYS, TASK_KEYS, SEGMENT_KEYS
from media_nest.models import (
    NodeInfo,
    RootInfo,
    TaskInfo,
    SegmentInfo,
    VideoSegmentInfo,
)
from .tool import row_to_model, model_to_row

__all__ = ["Repository"]


class Select:
    database: DataBaseManager

    def root_select_all(self) -> list[RootInfo]:
        cursor = self.database.connection.execute("SELECT * FROM root ORDER BY path")
        return [row_to_model("root", row) for row in cursor.fetchall() if row]

    def node_select_all(self) -> list[NodeInfo]:
        return self._select_all(table="node")

    def task_select_all(self) -> list[TaskInfo]:
        return self._select_all(table="task")

    def segment_select_all(self) -> list[SegmentInfo]:
        return self._select_all(table="segment")

    def _select_all(self, table: str):
        cursor = self.database.connection.execute(f"SELECT * FROM {table}")
        return [row_to_model(table, row) for row in cursor.fetchall() if row]

    def node_select_by_id(self, id: int) -> NodeInfo | None:
        sql = "SELECT * FROM node WHERE id = ?"
        cursor = self.database.connection.execute(sql, (id,))
        if info := cursor.fetchone():
            return row_to_model("node", info)
        return None

    def node_select_by_dev_ino(self, dev: int, ino: int) -> NodeInfo | None:
        sql = "SELECT * FROM node WHERE dev = ? AND ino = ?"
        cursor = self.database.connection.execute(sql, (dev, ino))
        if info := cursor.fetchone():
            return row_to_model("node", info)
        return None

    def node_select_by_parent_path(self, parent_path_str: str) -> list[NodeInfo]:
        sql = "SELECT * FROM node WHERE parent_path = ? ORDER BY name"
        cursor = self.database.connection.execute(sql, (parent_path_str,))
        return [row_to_model("node", row) for row in cursor.fetchall() if row]

    def node_select_marked(self) -> list[NodeInfo]:
        sql = "SELECT * FROM node WHERE marked = 1"
        cursor = self.database.connection.execute(sql)
        return [row_to_model("node", row) for row in cursor.fetchall() if row]

    def node_select_in_id(self, ids: list[int]) -> list[NodeInfo]:
        sql = f"SELECT * FROM node WHERE id IN ({','.join('?' * len(ids))})"
        cursor = self.database.connection.execute(sql, ids)
        return [row_to_model("node", row) for row in cursor.fetchall() if row]

    def node_select_in_dev_ino(
        self, dev_ino_list: list[tuple[int, int]]
    ) -> list[NodeInfo]:
        sql = f"SELECT * FROM node WHERE (dev, ino) IN ({','.join(('(?,?)' for _ in range(len(dev_ino_list))))})"
        params = [param for dev_ino in dev_ino_list for param in dev_ino]
        cursor = self.database.connection.execute(sql, params)
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
        sql = """SELECT s.order_, s.name, s.duration_ms, n.id, n.dev, n.ino, n.parent_path, n.name
                        FROM segment s JOIN node n ON s.video_id = n.id
                        WHERE n.parent_path = ?
                        ORDER BY n.id, s.order_"""
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
    database: DataBaseManager

    insert_placeholder = {
        "node": "(" + ",".join((key for key in NODE_KEYS[1:])) + ")",
        "root": "(" + ",".join((key for key in ROOT_KEYS[1:])) + ")",
        "task": "(" + ",".join((key for key in TASK_KEYS[1:])) + ")",
        "segment": "(" + ",".join((key for key in SEGMENT_KEYS)) + ")",
    }
    values_placeholder = {
        "node": "(" + ",".join("?" * (len(NODE_KEYS) - 1)) + ")",
        "root": "(" + ",".join("?" * (len(ROOT_KEYS) - 1)) + ")",
        "task": "(" + ",".join("?" * (len(TASK_KEYS) - 1)) + ")",
        "segment": "(" + ",".join("?" * len(SEGMENT_KEYS)) + ")",
    }

    def root_insert(self, info: RootInfo) -> bool:
        return self._insert("root", insert_many=False, info=info)

    def node_insert(self, info: NodeInfo) -> bool:
        return self._insert("node", insert_many=False, info=info)

    def task_insert(self, info: TaskInfo) -> bool:
        return self._insert("task", insert_many=False, info=info)

    def node_insert_many(self, infos: list[NodeInfo]) -> bool:
        return self._insert("node", insert_many=True, infos=infos)

    def task_insert_many(self, infos: list[TaskInfo]) -> bool:
        return self._insert("task", insert_many=True, infos=infos)

    def segment_insert_many(self, infos: list[SegmentInfo]) -> bool:
        return self._insert("segment", insert_many=True, infos=infos)

    def _insert(
        self,
        table: str,
        insert_many: bool,
        info: NodeInfo | RootInfo | TaskInfo | SegmentInfo = None,
        infos: list[NodeInfo | RootInfo | TaskInfo | SegmentInfo] = None,
    ):
        sql = f"INSERT INTO {table} {self.insert_placeholder[table]} VALUES {self.values_placeholder[table]}"
        with self.database.connection as connection:
            if insert_many:
                params_generator = ((model_to_row(table, info)) for info in infos)
                cursor = connection.executemany(sql, params_generator)
            else:
                params = model_to_row(table, info)
                cursor = connection.execute(sql, params)
        return True if cursor.rowcount else False


class Update:
    database: DataBaseManager

    update_placeholder = {
        "node": ",".join((f"{key}=?" for key in NODE_KEYS[1:])),
        "root": ",".join((f"{key}=?" for key in ROOT_KEYS[1:])),
        "task": ",".join((f"{key}=?" for key in TASK_KEYS[1:])),
        "segment": ",".join((f"{key}=?" for key in SEGMENT_KEYS)),
    }

    def root_update_by_id(self, id: int, info: RootInfo) -> bool:
        return self._update_by_id("root", id=id, info=info)

    def node_update_by_id(self, id: int, info: NodeInfo) -> bool:
        return self._update_by_id("node", id=id, info=info)

    def _update_by_id(
        self,
        table: str,
        id: int,
        info: NodeInfo | RootInfo | SegmentInfo,
    ):
        sql = f"UPDATE {table} SET {self.update_placeholder[table]} WHERE id = ?"
        with self.database.connection as connection:
            params = (*model_to_row(table, info), id)
            cursor = connection.execute(sql, params)
        return True if cursor.rowcount else False

    def node_update_marked_by_id(self, id: int, marked: bool) -> bool:
        sql = """UPDATE node SET marked = ? WHERE id = ?"""
        with self.database.connection as connection:
            cursor = connection.execute(sql, (int(marked), id))
        return True if cursor.rowcount else False

    def node_update_many_by_id(self, update_list: list[tuple[int, NodeInfo]]) -> bool:
        sql = f"UPDATE node SET {self.update_placeholder['node']} WHERE id = ?"
        with self.database.connection as connection:
            params_generator = (
                (*model_to_row("node", info), id) for id, info in update_list
            )
            cursor = connection.executemany(sql, params_generator)
        return True if cursor.rowcount else False

    def node_update_many_width_height_by_dev_ino(
        self, update_list: list[tuple[tuple[int, int], int, int]]
    ) -> bool:
        sql = """UPDATE node SET width = ?, height = ? WHERE dev = ? AND ino = ?"""
        with self.database.connection as connection:
            params_generator = (
                (width, height, dev, ino) for (dev, ino), width, height in update_list
            )
            cursor = connection.executemany(sql, params_generator)
        return True if cursor.rowcount else False

    def node_update_many_width_height_duration_by_dev_ino(
        self, update_list: list[tuple[tuple[int, int], int, int, int]]
    ) -> bool:
        sql = """UPDATE node SET width = ?, height = ?, duration_ms = ? WHERE dev = ? AND ino = ?"""
        with self.database.connection as connection:
            params_generator = (
                (width, height, duration_ms, dev, ino)
                for (dev, ino), width, height, duration_ms in update_list
            )
            cursor = connection.executemany(sql, params_generator)
        return True if cursor.rowcount else False


class Delete:
    database: DataBaseManager

    def root_delete_by_id(self, id: int) -> bool:
        return self._delete_by_id("root", id=id)

    def node_delete_by_id(self, id: int) -> bool:
        return self._delete_by_id("node", id=id)

    def _delete_by_id(self, table: str, id: int):
        sql = f"DELETE FROM {table} WHERE id = ?"
        with self.database.connection as connection:
            cursor = connection.execute(sql, (id,))
        return True if cursor.rowcount else False

    def node_delete_in_id(self, ids: list[int]) -> bool:
        return self._delete_in_one_key("node", key="id", values=ids)

    def segment_delete_in_video_id(self, ids: list[int]) -> bool:
        return self._delete_in_one_key("segment", key="video_id", values=ids)

    def _delete_in_one_key(self, table: str, key: str, values: list[int]) -> bool:
        sql = f"""DELETE FROM {table} WHERE {key} IN ({",".join("?" * len(values))})"""
        with self.database.connection as connection:
            cursor = connection.execute(sql, values)
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
