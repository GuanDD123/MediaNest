from pathlib import Path
import threading
from media_nest.core.db_manager import DataBaseManager
from media_nest.core.constant import NODE_KEY, ROOT_KEY, TASK_KEY, SEGMENT_KEY
from media_nest.models.node_info import FolderInfo, VideoInfo, ImageInfo
from media_nest.models.root_task_segment_info import RootInfo, TaskInfo, SegmentInfo
from media_nest.models.node_join_segment import NodeJoinSegment
from media_nest.repository.tool import model_to_row, row_to_model


class Repository:
    def __init__(self, database: DataBaseManager):
        self.database = database
        self.insert_placeholder = {'node': '(' + ','.join([f'{key}' for key in NODE_KEY[1:]]) + ')',
                                   'root': '(' + ','.join([f'{key}' for key in ROOT_KEY[1:]]) + ')',
                                   'task': '(' + ','.join([f'{key}' for key in TASK_KEY[1:]]) + ')',
                                   'segment': '(' + ','.join([f'{key}' for key in SEGMENT_KEY]) + ')'}
        self.values_placeholder = {'node': '(' + ','.join('?' * (len(NODE_KEY) - 1)) + ')',
                                   'root': '(' + ','.join('?' * (len(ROOT_KEY) - 1)) + ')',
                                   'task': '(' + ','.join('?' * (len(TASK_KEY) - 1)) + ')',
                                   'segment': '(' + ','.join('?' * len(SEGMENT_KEY)) + ')'}
        self.update_placeholder = {'node': ','.join([f'{key}=?' for key in NODE_KEY[1:]]),
                                   'root': ','.join([f'{key}=?' for key in ROOT_KEY[1:]])}

    def root_select_all(self) -> list[RootInfo]:
        return self._select_all(table='root')

    def task_select_all(self) -> list[TaskInfo]:
        return self._select_all(table='task')

    def select_all(self) -> list[FolderInfo | VideoInfo | ImageInfo]:
        return self._select_all(table='node')

    def _select_all(self, table: str):
        cursor = self.database.connection.execute(f'SELECT * FROM {table}')
        return [row_to_model(row, table=table) for row in cursor.fetchall() if row]

    def select_one_by_id(self, id: int) -> FolderInfo | VideoInfo | ImageInfo | None:
        return self._select(table='node', key_dict={'id': id}, select_one=True)

    def select_one_by_dev_ino(self, dev: int, ino: int) -> FolderInfo | VideoInfo | ImageInfo | None:
        return self._select(table='node', key_dict={'dev': dev, 'ino': ino}, select_one=True)

    def select_all_by_parent_path(self, parent_path: Path) -> list[FolderInfo | VideoInfo | ImageInfo]:
        return self._select(table='node', key_dict={'parent_path': str(parent_path)}, select_one=False)

    def _select(self, table: str, key_dict: dict[str, str | int], select_one: bool):
        sql = f'''SELECT * FROM {table} WHERE {' AND '.join([f'{key}=?' for key in key_dict])}'''
        cursor = self.database.connection.execute(sql, tuple(key_dict.values()))
        if select_one:
            row = cursor.fetchone()
            return row_to_model(row, table=table) if row else None
        else:
            return [row_to_model(row, table=table) for row in cursor.fetchall() if row]

    def select_many_in_id(self, id_list: list[int]) -> list[FolderInfo | VideoInfo | ImageInfo]:
        return self._select_many_in('node', ['id'], id_list, 1, len(id_list))

    def select_many_in_dev_ino(self, dev_ino_list: list[tuple[int, int]]) -> list[FolderInfo | VideoInfo | ImageInfo]:
        return self._select_many_in('node', ['dev', 'ino'], [param for dev_ino in dev_ino_list for param in dev_ino],
                                    2, len(dev_ino_list))

    def _select_many_in(self, table: str, key_name: list[str], param_list: list[str | int], key_len: int, value_item_len: int):
        placeholders = ','.join(
            ('(' + ','.join('?' * key_len) + ')') for _ in range(value_item_len))
        sql = f'''SELECT * FROM {table} WHERE ({', '.join(key_name)}) IN ({placeholders})'''
        cursor = self.database.connection.execute(sql, param_list)
        return [row_to_model(row, table=table) for row in cursor.fetchall() if row]

    def select_many_id_by_task_join_dev_ino(self) -> dict[str, int]:
        sql = '''SELECT task.dev, task.ino, node.id FROM task JOIN node
                ON node.dev = task.dev AND node.ino = task.ino WHERE task.hls_flag = 1'''
        cursor = self.database.connection.execute(sql)
        return {f'{row[0]}_{row[1]}': row[2] for row in cursor.fetchall()}

    def segments_select_many_join_video_id_by_parent_path(self, parent_path: Path) -> list[NodeJoinSegment]:
        sql = '''SELECT node.id, node.name, node.parent_path, node.dev, node.ino,
                        segment.segment_order, segment.segment_name, segment.duration_ms
                        FROM node JOIN segment ON segment.video_id = node.id
                        WHERE node.parent_path = ?
                        ORDER BY node.id, segment.segment_order'''
        cursor = self.database.connection.execute(sql, (str(parent_path),))
        return [NodeJoinSegment(video_id=row[0], video_name=row[1], video_parent_path=Path(row[2]),
                                video_dev=row[3], video_ino=row[4],
                                segment_order=row[5], segment_name=row[6], segment_duration_ms=row[7]
                                ) for row in cursor.fetchall() if row]

    def root_insert(self, info: RootInfo) -> bool:
        return self._insert(table='root', info=info)

    def task_insert_many(self, info_list: list[TaskInfo]) -> bool:
        return self._insert(table='task', info_list=info_list)

    def segment_insert_many(self, info_list: list[SegmentInfo]) -> bool:
        return self._insert(table='segment', info_list=info_list)

    def insert_one(self, info: FolderInfo | VideoInfo | ImageInfo) -> bool:
        return self._insert(table='node', info=info)

    def insert_many(self, info_list: list[FolderInfo | VideoInfo | ImageInfo]) -> bool:
        return self._insert(table='node', info_list=info_list)

    def _insert(self, table: str, info: FolderInfo | VideoInfo | ImageInfo | RootInfo | TaskInfo | SegmentInfo = None,
                info_list: list[FolderInfo | VideoInfo | ImageInfo | RootInfo | TaskInfo | SegmentInfo] = None):
        sql = f'INSERT INTO {table} {self.insert_placeholder[table]} VALUES {self.values_placeholder[table]}'
        with self.database.connection as connection:
            if info is not None:
                param_list = model_to_row(info, table=table)
                cursor = connection.execute(sql, param_list)
            else:
                param_list = ((model_to_row(info, table=table)) for info in info_list)
                cursor = connection.executemany(sql, param_list)
        return True if cursor.rowcount else False

    def root_update_by_id(self, id: int, info: RootInfo) -> bool:
        return self._update_by_id('root', id=id, info=info)

    def update_one_by_id(self, id: int, info: FolderInfo | VideoInfo | ImageInfo) -> bool:
        return self._update_by_id('node', id=id, info=info)

    def update_many_by_id(self, update_list: list[tuple[int, FolderInfo | VideoInfo | ImageInfo]]) -> bool:
        return self._update_by_id('node', update_list=update_list)

    def _update_by_id(self, table: str, id: int = None, info: FolderInfo | VideoInfo | ImageInfo | RootInfo = None,
                      update_list: list[tuple[int, FolderInfo | VideoInfo | ImageInfo | RootInfo]] = None):
        sql = f'UPDATE {table} SET {self.update_placeholder[table]} WHERE id = ?'
        with self.database.connection as connection:
            if id is not None:
                param_list = (*model_to_row(info, table=table), id)
                cursor = connection.execute(sql, param_list)
            else:
                param_list = ((*model_to_row(info, table=table), id) for id, info in update_list)
                cursor = connection.executemany(sql, param_list)
        return True if cursor.rowcount else False

    def update_many_image_specific_info_by_dev_ino(self, update_list: list[tuple[tuple[int, int], int, int]]) -> bool:
        sql = '''UPDATE node SET width = ?, height = ? WHERE dev = ? AND ino = ?'''
        with self.database.connection as connection:
            param_list = ((width, height, dev, ino) for (dev, ino), width, height in update_list)
            cursor = connection.executemany(sql, param_list)
        return True if cursor.rowcount else False

    def update_many_video_specific_info_by_dev_ino(self, update_list: list[tuple[tuple[int, int], int, int, int]]) -> bool:
        sql = '''UPDATE node SET width = ?, height = ?, duration_ms = ? WHERE dev = ? AND ino = ?'''
        with self.database.connection as connection:
            param_list = ((width, height, duration_ms, dev, ino)
                          for (dev, ino), width, height, duration_ms in update_list)
            cursor = connection.executemany(sql, param_list)
        return True if cursor.rowcount else False

    def root_delete_by_id(self, id: int) -> bool:
        return self._delete_by_id('root', id=id)

    def delete_one_by_id(self, id: int) -> bool:
        return self._delete_by_id('node', id=id)

    def _delete_by_id(self, table: str, id: int):
        sql = f'DELETE FROM {table} WHERE id = ?'
        with self.database.connection as connection:
            cursor = connection.execute(sql, (id,))
        return True if cursor.rowcount else False

    def delete_many_in_id(self, id_list: list[int]) -> bool:
        sql = f'''DELETE FROM node WHERE id IN ({','.join('?' * len(id_list))})'''
        with self.database.connection as connection:
            cursor = connection.execute(sql, id_list)
        return True if cursor.rowcount else False

    def task_delete_all(self) -> bool:
        return self._delete_all('task')

    def segment_delete_all(self) -> bool:
        return self._delete_all('segment')

    def delete_all(self) -> bool:
        return self._delete_all('node')

    def _delete_all(self, table: str):
        with self.database.connection as connection:
            cursor = connection.execute(f'DELETE FROM {table}')
        return True if cursor.rowcount else False
