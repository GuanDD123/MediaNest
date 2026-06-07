import shutil
from pathlib import Path
from urllib.parse import quote

from media_nest.core.constant import THUMB_SAVE_PATH
from media_nest.repository.repository import Repository
from media_nest.service.sync_library import SyncLibrary
from media_nest.service.deal_task import DealTask


class Service:
    def __init__(self, repository: Repository):
        self.repository = repository

    def sync(self) -> bool:
        try:
            SyncLibrary(self.repository).run()
            DealTask(self.repository).run()
            return True
        except Exception as e:
            print(f'Error occurred while syncing: {e}')
            return False

    def clear_cache(self) -> bool:
        try:
            self.repository.delete_all()
            self.repository.task_delete_all()
            if THUMB_SAVE_PATH.exists():
                shutil.rmtree(THUMB_SAVE_PATH)
            return True
        except Exception as e:
            print(f'Error occurred while clearing cache: {e}')
            return False

    def get_all_root(self) -> list[dict[str, str]]:
        return [{'type': 'folder', 'path': quote(str(info.path)), 'name': info.path.name} for info in self.repository.root_select_all()]

    def get_all_in_folder(self, path: Path) -> list[dict[str, str]]:
        return [{'type': info.type_, 'path': quote(str(info.parent_path / info.name)), 'name': info.name}
                for info in self.repository.select_all_by_parent_path(path)]

    def delete_one(self, id: int) -> bool:
        return self.repository.delete_one_by_id(id)

    def delete_many(self, id_list: list[int]) -> bool:
        return self.repository.delete_many_in_id(id_list)
