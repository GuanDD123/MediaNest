import shutil
from pathlib import Path
import json
from datetime import datetime as Datetime
import random

from media_nest.models import RootInfo, VideoInfo, ImageInfo, FolderInfo
from media_nest.repository import Repository
from media_nest.core.constant import (
    THUMB_SAVE_PATH,
    SEGMENT_SAVE_PATH,
    LAST_PLAYLIST,
    LAST_PROGRESS,
)
from .sync_library import SyncLibrary
from .deal_task import DealTask
from .build_m3u import BuildM3u


__all__ = ["Service"]


class Admin:
    repository: Repository

    def add_root(self, path_str: str) -> None:
        self.repository.root_insert(
            RootInfo(
                id=None, path=Path(path_str), last_sync_time=Datetime.now(), size=0
            )
        )

    def delete_root(self, path_str: str) -> None:
        for root_info in self.repository.root_select_all():
            if str(root_info.path) == path_str:
                self.repository.root_delete_by_id(root_info.id)
                return

    def clear_root(self) -> None:
        self.repository.root_delete_all()

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

    def mark(self, id: int, marked: bool) -> None:
        self.repository.node_update_marked_by_id(id, marked)


class Playlist:
    repository: Repository

    def build_m3u(self, parent_str: str, shuffle_flag: bool = False) -> str:
        return BuildM3u(self.repository).run(Path("/" + parent_str), shuffle_flag)


class Media:
    repository: Repository

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

    def _separate_folder_media(
        self, node_infos: list[FolderInfo | VideoInfo | ImageInfo]
    ) -> tuple[list[FolderInfo], list[VideoInfo | ImageInfo]]:
        folder_infos = []
        media_infos = []
        for node_indo in node_infos:
            if node_indo.type_ == "folder":
                folder_infos.append(node_indo)
            else:
                media_infos.append(node_indo)
        return folder_infos, media_infos

    def _node_infos_to_response(
        self, node_infos: list[FolderInfo | VideoInfo | ImageInfo]
    ) -> list[dict[str, str | int]]:
        results: list[dict] = []
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
            results.append(result)
        return results

    @staticmethod
    def save_playlist(playlist: tuple[list[dict], list[dict]]) -> None:
        with open(LAST_PLAYLIST, "w", encoding="utf-8") as f:
            json.dump(playlist, f, indent=4, ensure_ascii=False)

    @staticmethod
    def save_progress(index: int) -> None:
        LAST_PROGRESS.write_text(str(index))

    @staticmethod
    def continue_last_play() -> tuple[
        tuple[list[dict[str, str | int]], list[dict[str, str | int]]], int
    ]:
        if not LAST_PLAYLIST.exists() or not LAST_PROGRESS.exists():
            return [], 0

        with open(LAST_PLAYLIST, "r", encoding="utf-8") as f:
            last_playlist = json.load(f)
        with open(LAST_PROGRESS, "r", encoding="utf-8") as f:
            index = int(f.read().strip())
        if index + 1 >= len(last_playlist[1]):
            return [], 0

        return (last_playlist, index)


class Service(Admin, Playlist, Media):
    def __init__(self, repository: Repository):
        self.repository = repository
