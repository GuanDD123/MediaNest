import os
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime as Datetime
from pathlib import Path
from typing import Literal

from media_nest.core.settings import Settings
from media_nest.logs import logger
from media_nest.models import NodeInfo, TaskInfo
from media_nest.repository import Repository


@dataclass(slots=True)
class ScanResult:
    db_infos: dict[tuple[int, int], NodeInfo]
    node_insert_list: list[NodeInfo]
    node_update_list: list[tuple[int, NodeInfo]]
    task_insert_list: list[TaskInfo]
    folder_size_dict: dict[tuple[int, int], int]


@dataclass(slots=True)
class Progress:
    status: Literal["idle", "running", "finished", "failed"]
    root_folders_num: int
    current_root_folder: Path
    completed_root_folders_num: int
    completed_scan_num: int


class ScanLibrary:
    def __init__(self, repository: Repository, settings: Settings):
        self.repository = repository
        self.settings = settings
        self.progress: Progress = Progress(
            status="idle",
            root_folders_num=0,
            current_root_folder=None,
            completed_root_folders_num=0,
            completed_scan_num=0,
        )

    def run(self) -> None:
        logger.info("Starting scan process")

        self.progress.status = "running"
        self.progress.root_folders_num = 0
        self.progress.current_root_folder = None
        self.progress.completed_root_folders_num = 0
        self.progress.completed_scan_num = 0

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
        root_infos = self.repository.root_select_all()
        self.progress.root_folders_num = len(root_infos)
        for root_info in root_infos:
            self.progress.current_root_folder = root_info.path
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

                self.progress.completed_scan_num += 1

            root_info.last_sync_time = Datetime.now(UTC)
            root_info.size = scan_result.folder_size_dict.get(
                (root_info.path.stat().st_dev, root_info.path.stat().st_ino), -1
            )
            self.repository.root_update_by_id(root_info.id, root_info)

            self.progress.completed_root_folders_num += 1

        self._sync_to_db(scan_result)
        self.progress.status = "finished"

        logger.info(
            f"Scan completed successfully: {self.progress.completed_scan_num} files or folders scanned"
        )

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
            flag = self._check_update(
                db_info, scan_result, path, parent_path, root_id, path_stat, dev, ino
            )
            if flag:
                return 2
            if flag is False:
                scan_result.db_infos[(dev, ino)] = db_info

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
            info = NodeInfo(
                id=None,
                dev=dev,
                ino=ino,
                root_id=root_id,
                parent_path=parent_path,
                name=path.name,
                type_="folder",
                size=0,
                mtime=Datetime.fromtimestamp(int(path_stat.st_mtime), tz=UTC),
            )
        elif path.suffix.lower() in self.settings.image_suffix:
            info = NodeInfo(
                id=None,
                dev=dev,
                ino=ino,
                root_id=root_id,
                parent_path=parent_path,
                name=path.name,
                type_="image",
                size=path_stat.st_size,
                mtime=Datetime.fromtimestamp(int(path_stat.st_mtime), tz=UTC),
            )
            task_insert_flag = True
            type_ = "image"
            width_height_flag = True
            thumb_flag = bool(self.settings.thumb_mode)
        elif path.suffix.lower() in self.settings.video_suffix:
            info = NodeInfo(
                id=None,
                dev=dev,
                ino=ino,
                root_id=root_id,
                parent_path=parent_path,
                name=path.name,
                type_="video",
                size=path_stat.st_size,
                mtime=Datetime.fromtimestamp(int(path_stat.st_mtime), tz=UTC),
            )
            task_insert_flag = True
            type_ = "video"
            duration_ms_flag = True
            width_height_flag = True
            hls_flag = bool(self.settings.hls_mode)
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
        db_info: NodeInfo,
        scan_result: ScanResult,
        path: Path,
        parent_path: Path,
        root_id: int,
        path_stat: os.stat_result,
        dev: int,
        ino: int,
    ):
        local_modify_time = Datetime.fromtimestamp(int(path_stat.st_mtime), tz=UTC)

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
            if db_info.type_ != "folder":
                db_info.type_ = "folder"
                db_info.width = None
                db_info.height = None
                db_info.duration_ms = None
                db_info.marked = False
                node_update_flag = True
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

            if path.suffix.lower() in self.settings.video_suffix:
                if db_info.type_ != "video":
                    db_info.type_ = "video"
                    node_update_flag = True
                    task_insert_flag = True
                    modify_flag = True
                if modify_flag:
                    db_info.marked = False
                    duration_ms_flag = True
                    width_height_flag = True
                    hls_flag = bool(self.settings.hls_mode)
                elif (
                    self.settings.hls_mode
                    and not (self.settings.segment_dirpath / f"{dev}_{ino}").exists()
                ):
                    hls_flag = True
                    task_insert_flag = True
            elif path.suffix.lower() in self.settings.image_suffix:
                if db_info.type_ != "image":
                    db_info.type_ = "image"
                    db_info.duration_ms = None
                    node_update_flag = True
                    task_insert_flag = True
                    modify_flag = True
                if modify_flag:
                    db_info.marked = False
                    width_height_flag = True
                    thumb_flag = bool(self.settings.thumb_mode)
                elif (
                    self.settings.thumb_mode
                    and not (self.settings.thumb_dirpath / f"{dev}_{ino}.jpg").exists()
                ):
                    thumb_flag = True
                    task_insert_flag = True
            else:
                return False  # Unsupported file type, will delete

        if task_insert_flag:
            scan_result.task_insert_list.append(
                TaskInfo(
                    id=None,
                    type_=db_info.type_,
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
            for dev, ino in scan_result.db_infos:
                (self.settings.thumb_dirpath / f"{dev}_{ino}.jpg").unlink(
                    missing_ok=True
                )
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
