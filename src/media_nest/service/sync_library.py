import os
from pathlib import Path
from datetime import datetime as Datetime
from dataclasses import dataclass

from media_nest.core.constant import (
    THUMB_SAVE_PATH,
    HLS_MODE,
    SEGMENT_SAVE_PATH,
    THUMB_MODE,
    IMAGE_SUFFIX,
    VIDEO_SUFFIX,
)
from media_nest.models import FolderInfo, VideoInfo, ImageInfo, TaskInfo
from media_nest.repository import Repository


@dataclass(slots=True)
class ScanResult:
    db_infos: dict[tuple[int, int], FolderInfo | VideoInfo | ImageInfo]
    node_insert_list: list[FolderInfo | VideoInfo | ImageInfo]
    node_update_list: list[tuple[int, FolderInfo | VideoInfo | ImageInfo]]
    task_insert_list: list[TaskInfo]
    folder_size_dict: dict[tuple[int, int], int]


class SyncLibrary:
    def __init__(self, repository: Repository):
        self.repository = repository

    def run(self) -> None:
        scan_result = ScanResult(
            db_infos={
                (db_info.dev, db_info.ino): db_info
                for db_info in self.repository.node_select_all()
            },
            node_insert_list=[],
            node_update_list=[],
            task_insert_list=[],
            folder_size_dict={},
        )

        node_insert_num = node_update_num = 0
        for root_info in self.repository.root_select_all():
            for parent_path, path in self._walk_files(
                root_info.path, scan_result.folder_size_dict
            ):
                flag = self._node_insert_update(
                    path, parent_path, root_info.id, scan_result
                )
                if flag == 1:
                    node_insert_num += 1
                elif flag == 2:
                    node_update_num += 1
                if node_insert_num > 1000:
                    self.repository.node_insert_many(scan_result.node_insert_list)
                    scan_result.node_insert_list = []
                    node_insert_num = 0
                elif node_update_num > 1000:
                    self.repository.node_update_many_by_id(scan_result.node_update_list)
                    scan_result.node_update_list = []
                    node_update_num = 0

            root_info.last_sync_time = Datetime.now()
            root_info.size = scan_result.folder_size_dict.get((root_info.path.stat().st_dev, root_info.path.stat().st_ino), -1)
            self.repository.root_update_by_id(root_info.id, root_info)

        self._sync_to_db(scan_result)

    def _walk_files(
        self, root_path: Path, folder_size_dict: dict[tuple[int, int], int]
    ):
        for dirpath, dirnames, filenames in os.walk(root_path):
            folder = Path(dirpath)
            folder_stat = folder.stat()
            folder_size_dict[(folder_stat.st_dev, folder_stat.st_ino)] = len(filenames)

            for dirname in dirnames:
                yield folder, folder / dirname
            for filename in filenames:
                yield folder, folder / filename

    def _node_insert_update(
        self, path: Path, parent_path: Path, root_id: int, scan_result: ScanResult
    ):
        path_stat = path.stat()
        dev = path_stat.st_dev
        ino = path_stat.st_ino

        db_info = scan_result.db_infos.pop((dev, ino), None)
        if not db_info:
            self._node_insert(
                scan_result, path, parent_path, root_id, path_stat, dev, ino
            )
            return 1
        else:
            if self._check_update(
                db_info, scan_result, path, parent_path, root_id, path_stat, dev, ino
            ):
                return 2

    def _node_insert(
        self,
        scan_result: ScanResult,
        path: Path,
        parent_path: Path,
        root_id: int,
        path_stat: os.stat_result,
        dev: int,
        ino: int,
    ):
        task_insert_flag = False
        width_height_flag = duration_ms_flag = thumb_flag = hls_flag = False
        if path.is_dir():
            info = FolderInfo(
                id=None,
                dev=dev,
                ino=ino,
                root_id=root_id,
                parent_path=parent_path,
                name=path.name,
                type_="folder",
                size=0,
                mtime=Datetime.fromtimestamp(int(path_stat.st_mtime)),
            )
        elif path.suffix.lower() in IMAGE_SUFFIX:
            info = ImageInfo(
                id=None,
                dev=dev,
                ino=ino,
                root_id=root_id,
                parent_path=parent_path,
                name=path.name,
                type_="image",
                size=path_stat.st_size,
                mtime=Datetime.fromtimestamp(int(path_stat.st_mtime)),
            )
            task_insert_flag = True
            type_ = "image"
            width_height_flag = True
            thumb_flag = True if THUMB_MODE else False
        elif path.suffix.lower() in VIDEO_SUFFIX:
            info = VideoInfo(
                id=None,
                dev=dev,
                ino=ino,
                root_id=root_id,
                parent_path=parent_path,
                name=path.name,
                type_="video",
                size=path_stat.st_size,
                mtime=Datetime.fromtimestamp(int(path_stat.st_mtime)),
            )
            task_insert_flag = True
            type_ = "video"
            duration_ms_flag = True
            width_height_flag = True
            hls_flag = True if HLS_MODE else False
        else:
            return
        scan_result.node_insert_list.append(info)
        if task_insert_flag:
            scan_result.task_insert_list.append(
                TaskInfo(
                    id=None,
                    type_=type_,
                    path=path,
                    dev=dev,
                    ino=ino,
                    duration_ms_flag=duration_ms_flag,
                    width_height_flag=width_height_flag,
                    hls_flag=hls_flag,
                    thumb_flag=thumb_flag,
                )
            )

    def _check_update(
        self,
        db_info: FolderInfo | VideoInfo | ImageInfo,
        scan_result: ScanResult,
        path: Path,
        parent_path: Path,
        root_id: int,
        path_stat: os.stat_result,
        dev: int,
        ino: int,
    ):
        local_modify_time = Datetime.fromtimestamp(int(path_stat.st_mtime))

        node_update_flag = False
        task_insert_flag = False
        if db_info.parent_path != parent_path:
            db_info.root_id = root_id
            db_info.parent_path = parent_path
            node_update_flag = True
        if db_info.name != path.name:
            db_info.name = path.name
            node_update_flag = True
        if path.is_dir():
            if db_info.mtime != local_modify_time:
                db_info.mtime = local_modify_time
                node_update_flag = True
        else:
            modify_flag = False
            width_height_flag = duration_ms_flag = thumb_flag = hls_flag = False
            if db_info.mtime != local_modify_time or db_info.size != path_stat.st_size:
                db_info.mtime = local_modify_time
                db_info.size = path_stat.st_size
                node_update_flag = True
                task_insert_flag = True
                modify_flag = True

            if db_info.type_ == "video":
                type_ = "video"
                if modify_flag:
                    duration_ms_flag = True
                    width_height_flag = True
                    hls_flag = True if HLS_MODE else False
                elif HLS_MODE and not (SEGMENT_SAVE_PATH / f"{dev}_{ino}").exists():
                    hls_flag = True
                    task_insert_flag = True
            else:  # image
                type_ = "image"
                if modify_flag:
                    width_height_flag = True
                    thumb_flag = True if THUMB_MODE else False
                elif THUMB_MODE and not (THUMB_SAVE_PATH / f"{dev}_{ino}.jpg").exists():
                    thumb_flag = True
                    task_insert_flag = True

        if task_insert_flag:
            scan_result.task_insert_list.append(
                TaskInfo(
                    id=None,
                    type_=type_,
                    path=path,
                    dev=dev,
                    ino=ino,
                    duration_ms_flag=duration_ms_flag,
                    width_height_flag=width_height_flag,
                    hls_flag=hls_flag,
                    thumb_flag=thumb_flag,
                )
            )
        if node_update_flag:
            scan_result.node_update_list.append((db_info.id, db_info))
            return True

    def _sync_to_db(self, scan_result: ScanResult):
        if ids := [db_info.id for db_info in scan_result.db_infos.values()]:
            self.repository.node_delete_in_id(ids)
        if update_list := scan_result.node_update_list:
            self.repository.node_update_many_by_id(update_list)
        if insert_list := scan_result.node_insert_list:
            self.repository.node_insert_many(insert_list)
        if folder_size_dict := scan_result.folder_size_dict:
            wait_to_update_list = self.repository.node_select_in_dev_ino(
                list(folder_size_dict.keys())
            )
            for wait_to_update in wait_to_update_list:
                wait_to_update.size = folder_size_dict[
                    (wait_to_update.dev, wait_to_update.ino)
                ]
            self.repository.node_update_many_by_id(
                [(info.id, info) for info in wait_to_update_list]
            )

        if task_list := scan_result.task_insert_list:
            self.repository.task_insert_many(task_list)
