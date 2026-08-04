import json
import shutil
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC
from datetime import datetime as Datetime
from pathlib import Path

from media_nest.core.constant import LAST_PLAYLIST, LAST_PROGRESS
from media_nest.core.settings import Settings
from media_nest.logs import logger
from media_nest.models import NodeInfo, RootInfo
from media_nest.repository import Repository

from .build_m3u import BuildM3u
from .deal_task import DealTask
from .scan_library import ScanLibrary

__all__ = ["Service"]


class Admin:
    repository: Repository
    settings: Settings
    executor: ThreadPoolExecutor
    scan_library: ScanLibrary
    deal_task: DealTask

    def add_root(self, path_str: str) -> None:
        logger.info(f"Add root: {path_str}")
        now_time = Datetime.now(UTC)
        self.repository.root_insert(
            RootInfo(id=None, path=Path(path_str), last_sync_time=now_time, size=0)
        )

    def delete_root(self, path_str: str) -> None:
        logger.info(f"Delete root: {path_str}")
        for root_info in self.repository.root_select_all():
            if str(root_info.path) == path_str:
                self.repository.root_delete_by_id(root_info.id)
                return

    def clear_root(self) -> None:
        logger.info("Clear all roots")
        self.repository.root_delete_all()

    def sync(self) -> bool:
        logger.info("Post sync request")
        if self.future and not self.future.done():
            return False
        self.future = self.executor.submit(self._sync)
        return True

    def _sync(self):
        logger.info("Starting sync process")

        try:
            self.scan_library.run()
        except Exception:  # noqa: BLE001
            self.scan_library.progress.status = "failed"
            logger.exception("Scan Library failed")
            return

        try:
            self.deal_task.run()
        except Exception:  # noqa: BLE001
            self.deal_task.progress.status = "failed"
            logger.exception("Deal Task failed")
            return

        logger.info("Sync completed successfully")

    def get_sync_progress(self):
        if self.scan_library.progress.status != "finished":
            return {
                "current_step": "Scan Library",
                "status": self.scan_library.progress.status,
                "root_folders_num": self.scan_library.progress.root_folders_num,
                "completed_root_folders_num": self.scan_library.progress.completed_root_folders_num,
                "current_root_folder": str(
                    self.scan_library.progress.current_root_folder
                ),
                "completed_scan_num": self.scan_library.progress.completed_scan_num,
            }
        else:
            return {
                "current_step": "Deal Task",
                "status": self.deal_task.progress.status,
                "task_num": self.deal_task.progress.task_num,
                "successed_task_num": self.deal_task.progress.successed_task_num,
                "failed_task_num": self.deal_task.progress.failed_task_num,
            }

    def clear_cache(self) -> None:
        logger.info("Clear cache")

        self.repository.node_delete_all()
        self.repository.task_delete_all()
        self.repository.segment_delete_all()
        if self.settings.thumb_dirpath.exists():
            shutil.rmtree(self.settings.thumb_dirpath)
        if self.settings.segment_dirpath.exists():
            shutil.rmtree(self.settings.segment_dirpath)

    def mark(self, id: int, marked: bool) -> None:
        self.repository.node_update_marked_by_id(id, marked)

    def delete_file(
        self, id: int, path_str: str, additional_path_list: list[str]
    ) -> None:
        logger.info(f"Delete file: {path_str}")
        Path(path_str).unlink(missing_ok=True)
        for additional_path in additional_path_list:
            logger.info(f"Delete additional file: {additional_path}")
            Path(additional_path).unlink(missing_ok=True)
        self.repository.node_delete_by_id(id)


class Playlist:
    repository: Repository
    settings: Settings

    def build_m3u(self, parent_str: str, shuffle_flag: bool = False) -> str:
        return BuildM3u(self.repository, self.settings).run(
            Path("/" + parent_str), shuffle_flag
        )


class Media:
    repository: Repository
    settings: Settings

    def get_all_root(self):
        return (
            [
                {
                    "type": "folder",
                    "parent_path": str(info.path.parent),
                    "name": info.path.name,
                    "size": info.size,
                }
                for info in self.repository.root_select_all()
            ],
            [],
        )

    def get_all_in_folder(
        self, path_str: str
    ) -> tuple[list[dict[str, str | int]], list[dict[str, str | int]]]:
        node_infos = self.repository.node_select_by_parent_path(path_str)
        folder_infos, media_infos = self._separate_folder_media(node_infos)
        return (
            self._node_infos_to_response(folder_infos),
            self._node_infos_to_response(media_infos),
        )

    def filter_marked(
        self,
    ) -> tuple[list[dict[str, str | int]], list[dict[str, str | int]]]:
        node_marked = self.repository.node_select_marked()
        folder_marked, media_marked = self._separate_folder_media(node_marked)
        return (
            self._node_infos_to_response(folder_marked),
            self._node_infos_to_response(media_marked),
        )

    def _separate_folder_media(self, node_infos: list[NodeInfo]):
        folder_infos: list[NodeInfo] = []
        media_infos: list[NodeInfo] = []
        for node_info in node_infos:
            if node_info.type_ == "folder":
                folder_infos.append(node_info)
            else:
                media_infos.append(node_info)
        return folder_infos, media_infos

    def _node_infos_to_response(self, node_infos: list[NodeInfo]):
        results: list[dict[str, str | int]] = []
        for info in node_infos:
            result = {
                "id": info.id,
                "type": info.type_,
                "parent_path": str(info.parent_path),
                "name": info.name,
                "size": info.size,
                "marked": info.marked,
            }
            if info.type_ != "folder":
                result["width"] = info.width
                result["height"] = info.height
                if info.type_ == "video":
                    result["duration"] = int(info.duration_ms / 1000)
                else:
                    result["thumb_path"] = (
                        f"{self.settings.thumb_dirpath}/{info.dev}_{info.ino}.jpg"
                    )
            results.append(result)
        return results

    @staticmethod
    def save_playlist(playlist: list[dict]) -> None:
        with open(LAST_PLAYLIST, "w", encoding="utf-8") as f:
            json.dump(playlist, f, indent=4, ensure_ascii=False)

    @staticmethod
    def save_progress(index: int) -> None:
        LAST_PROGRESS.write_text(str(index))

    @staticmethod
    def continue_last_play() -> tuple[list[dict[str, str | int]], int]:
        if not LAST_PLAYLIST.exists() or not LAST_PROGRESS.exists():
            return [], 0

        with open(LAST_PLAYLIST, "r", encoding="utf-8") as f:
            last_playlist = json.load(f)
        with open(LAST_PROGRESS, "r", encoding="utf-8") as f:
            index = int(f.read().strip())

        return (last_playlist, index)


class Service(Admin, Playlist, Media):
    def __init__(
        self, repository: Repository, settings: Settings, executor: ThreadPoolExecutor
    ):
        self.repository = repository
        self.settings = settings
        self.executor = executor
        self.future: Future | None = None
        self.scan_library = ScanLibrary(self.repository, self.settings)
        self.deal_task = DealTask(self.repository, self.settings)
