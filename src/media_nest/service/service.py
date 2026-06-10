import shutil
from pathlib import Path
from urllib.parse import quote
from datetime import datetime as Datetime

from media_nest.models import RootInfo
from media_nest.repository import Repository
from media_nest.core.constant import THUMB_SAVE_PATH, SEGMENT_SAVE_PATH
from .sync_library import SyncLibrary
from .deal_task import DealTask
from .build_m3u import BuildM3u


__all__ = ["Service"]


class Service:
    def __init__(self, repository: Repository):
        self.repository = repository

    def add_root(self, path_str: str) -> None:
        self.repository.root_insert(
            RootInfo(id=None, path=Path(path_str), last_sync_time=Datetime.now(), size=0)
        )

    def delete_root(self, path_str: str) -> None:
        for root_info in self.repository.root_select_all():
            if str(root_info.path) == path_str:
                self.repository.root_delete_by_id(root_info.id)
                return

    def clear_root(self) -> None:
        for info in self.repository.root_select_all():
            self.repository.root_delete_by_id(info.id)

    def sync(self) -> None:
        SyncLibrary(self.repository).run()
        DealTask(self.repository).run()

    def clear_cache(self) -> None:
        self.repository.node_delete_all()
        self.repository.task_delete_all()
        self.repository.segment_delete_all()
        if THUMB_SAVE_PATH.exists():
            shutil.rmtree(THUMB_SAVE_PATH)
        if SEGMENT_SAVE_PATH.exists():
            shutil.rmtree(SEGMENT_SAVE_PATH)

    def get_all_root(self) -> list[dict[str, str]]:
        return [
            {"type": "folder", "path": quote(str(info.path)), "name": info.path.name, "size": info.size}
            for info in self.repository.root_select_all()
        ]

    def get_all_in_folder(self, path_str: str) -> list[dict[str, str | int]]:
        results: list[dict] = []
        for info in self.repository.node_select_by_parent_path(path_str):
            result = {
                "type": info.type_,
                "path": quote(str(info.parent_path / info.name)),
                "name": info.name,
                "size": info.size,
            }
            if info.type_ != "folder":
                result["width"] = info.width
                result["height"] = info.height
                if info.type_ == "video":
                    result["duration"] = int(info.duration_ms / 1000)
            results.append(result)
        return results

    def build_m3u(self, parent_str: str, shuffle_flag: bool = False) -> str:
        return BuildM3u(self.repository).run(Path("/" + parent_str), shuffle_flag)
