import os
from pathlib import Path
from datetime import datetime as Datetime
from dataclasses import dataclass

from media_nest.core.constant import THUMB_SAVE_PATH, HLS_MODE, THUMB_MODE
from media_nest.models.node_info import FolderInfo, VideoInfo, ImageInfo
from media_nest.models.task_segment_info import TaskInfo
from media_nest.repository.repository import Repository


@dataclass(slots=True)
class ScanResult:
    db_info_dict: dict[tuple[int, int], FolderInfo | VideoInfo | ImageInfo]
    node_insert_list: list[FolderInfo | VideoInfo | ImageInfo]
    node_update_list: list[tuple[int, FolderInfo | VideoInfo | ImageInfo]]
    task_insert_list: list[TaskInfo]
    folder_size_dict: dict[tuple[int, int], int]


class SyncLibrary:
    def __init__(self, repository: Repository):
        self.repository = repository

    def run(self) -> None:
        scan_result = ScanResult(db_info_dict={(db_info.dev, db_info.ino): db_info
                                               for db_info in self.repository.select_all()},
                                 node_insert_list=[],
                                 node_update_list=[],
                                 task_insert_list=[],
                                 folder_size_dict={})

        insert_num, update_num = 0, 0
        for root_info in self.repository.root_select_all():
            for parent_path, path in self._walk_files(root_info.path, scan_result.folder_size_dict):
                flag = self._update_db_data(path, parent_path, root_info.id, scan_result)
                if flag == 0:
                    insert_num += 1
                elif flag == 1:
                    update_num += 1
                if insert_num > 1000:
                    self.repository.insert_many(scan_result.node_insert_list)
                    scan_result.node_insert_list = []
                    insert_num = 0
                if update_num > 1000:
                    self.repository.update_many_by_id(scan_result.node_update_list)
                    scan_result.node_update_list = []
                    update_num = 0

            root_info.last_sync_at = Datetime.now()
            self.repository.root_update_by_id(root_info.id, root_info)

        if (id_list := [db_info.id for db_info in scan_result.db_info_dict.values()]):
            self.repository.delete_many_in_id(id_list)
        if (update_list := scan_result.node_update_list):
            self.repository.update_many_by_id(update_list)
        if (insert_list := scan_result.node_insert_list):
            self.repository.insert_many(insert_list)
        self._update_db_data_folder_size(scan_result.folder_size_dict)

        if (task_list := scan_result.task_insert_list):
            self.repository.task_insert_many(task_list)

    @staticmethod
    def _walk_files(root_path: Path, folder_size_dict: dict[tuple[int, int], int]):
        for dirpath, dirnames, filenames in os.walk(root_path):
            folder = Path(dirpath)
            folder_stat = folder.stat()
            folder_size_dict[(folder_stat.st_dev, folder_stat.st_ino)] = len(filenames)

            for dirname in dirnames:
                yield folder, folder / dirname
            for filename in filenames:
                yield folder, folder / filename

    def _update_db_data(self, path: Path, parent_path: Path, root_id: int, scan_result: ScanResult):
        path_stat = path.stat()
        dev, ino = path_stat.st_dev, path_stat.st_ino

        db_info = scan_result.db_info_dict.pop((dev, ino), None)
        if not db_info:
            self._add_insert(scan_result, path, parent_path, root_id, path_stat, dev, ino)
            return 0
        else:
            flag = self._check_update(db_info, scan_result, path, parent_path, root_id, path_stat, dev, ino)
            if flag:
                return 1

    def _add_insert(self, scan_result: ScanResult, path: Path, parent_path: Path, root_id: int,
                    path_stat: os.stat_result, dev: int, ino: int):
        if path.is_dir():
            info = FolderInfo(id=None, dev=dev, ino=ino, root_id=root_id, parent_path=parent_path,
                              name=path.name, type_='folder', size=0,
                              mtime=Datetime.fromtimestamp(int(path_stat.st_mtime)))
        elif path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            info = ImageInfo(id=None, dev=dev, ino=ino, root_id=root_id, parent_path=parent_path,
                             name=path.name, type_='image', size=path_stat.st_size,
                             mtime=Datetime.fromtimestamp(int(path_stat.st_mtime)),
                             width=None, height=None)
            self._task_mark(scan_result.task_insert_list, path, 'image', dev, ino,
                            width_height_flag=True, thumb_flag=True if THUMB_MODE else False)
        elif path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
            info = VideoInfo(id=None, dev=dev, ino=ino, root_id=root_id, parent_path=parent_path,
                             name=path.name, type_='video', size=path_stat.st_size,
                             mtime=Datetime.fromtimestamp(path_stat.st_mtime),
                             duration_ms=None, width=None, height=None)
            self._task_mark(scan_result.task_insert_list, path, 'video', dev, ino,
                            duration_ms_flag=True, width_height_flag=True, hls_flag=True if HLS_MODE else False)
        else:
            return
        scan_result.node_insert_list.append(info)

    def _task_mark(self, task_insert_list: list, path: Path, type_: str, dev: int, ino: int,
                   duration_ms_flag: bool = False, width_height_flag: bool = False, hls_flag: bool = False,
                   thumb_flag: bool = False):
        task_insert_list.append(TaskInfo(id=None, type_=type_, path=path, dev=dev, ino=ino,
                                         duration_ms_flag=duration_ms_flag, width_height_flag=width_height_flag,
                                         hls_flag=hls_flag, thumb_flag=thumb_flag))

    def _check_update(self, db_info: FolderInfo | VideoInfo | ImageInfo, scan_result: ScanResult, path: Path,
                      parent_path: Path, root_id: int, path_stat: os.stat_result, dev: int, ino: int):
        local_modify_time = Datetime.fromtimestamp(int(path_stat.st_mtime))
        path_is_dir = True if path.is_dir() else False

        update_flag = False
        if db_info.parent_path != parent_path:
            db_info.root_id = root_id
            db_info.parent_path = parent_path
            update_flag = True
        if db_info.name != (path_name := path.name):
            db_info.name = path_name
            update_flag = True
        if path_is_dir:
            if db_info.mtime != local_modify_time:
                db_info.mtime = local_modify_time
                update_flag = True
        else:
            if db_info.mtime != local_modify_time or db_info.size != (path_size := path_stat.st_size):
                db_info.mtime = local_modify_time
                try:
                    db_info.size = path_size
                except NameError:
                    db_info.size = path_stat.st_size
                update_flag = True
                if db_info.type_ == 'video':
                    self._task_mark(scan_result.task_insert_list, path, 'video', dev, ino, duration_ms_flag=True,
                                    width_height_flag=True, hls_flag=True if HLS_MODE else False)
                else:  # image
                    self._task_mark(scan_result.task_insert_list, path, 'image', dev, ino, width_height_flag=True,
                                    thumb_flag=True if THUMB_MODE else False)
            else:
                if HLS_MODE and db_info.type_ == 'video' and (
                        not Path(f'{parent_path}/hls/{dev}_{ino}').exists()):
                    self._task_mark(scan_result.task_insert_list, path, 'video', dev, ino, duration_ms_flag=False,
                                    width_height_flag=False, hls_flag=True)
                if THUMB_MODE and db_info.type_ == 'image' and (
                        not Path(f'{THUMB_SAVE_PATH}/{dev}_{ino}.jpg').exists()):
                    self._task_mark(scan_result.task_insert_list, path, 'image', dev, ino, width_height_flag=False,
                                    thumb_flag=True)

        if update_flag:
            scan_result.node_update_list.append((db_info.id, db_info))
            return True

    def _update_db_data_folder_size(self, folder_size_dict: dict[tuple[int, int], int]):
        wait_to_update_list = self.repository.select_many_in_dev_ino(list(folder_size_dict.keys()))

        for wait_to_update in wait_to_update_list:
            wait_to_update.size = folder_size_dict[(wait_to_update.dev, wait_to_update.ino)]
        self.repository.update_many_by_id([(info.id, info) for info in wait_to_update_list])
