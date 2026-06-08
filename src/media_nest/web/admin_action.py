from fastapi import APIRouter, Depends, Body
from pathlib import Path
import datetime

from media_nest.models.root_task_info import RootInfo
from media_nest.repository.repository import Repository
from media_nest.service.service import Service
from media_nest.web.dependence import get_repository

router = APIRouter(prefix='/admin')


@router.post('/add_root')
def add_root(path: str = Body(...), repository: Repository = Depends(get_repository)):
    repository.root_insert(RootInfo(id=None, path=Path(path), last_sync_at=datetime.datetime.now()))
    return {'success': True}


@router.post('/delete_root')
def delete_root(path: str = Body(...), repository: Repository = Depends(get_repository)):
    for root_info in repository.root_select_all():
        if str(root_info.path) == path:
            repository.root_delete_by_id(root_info.id)
            return {'success': True}


@router.post('/clear_root')
def clear_root(repository: Repository = Depends(get_repository)):
    for info in repository.root_select_all():
        repository.root_delete_by_id(info.id)
    return {'success': True}


@router.post('/sync')
def sync(repository: Repository = Depends(get_repository)):
    Service(repository).sync()
    return {'success': True}


@router.post('/clear_cache')
def clear_cache(repository: Repository = Depends(get_repository)):
    Service(repository).clear_cache()
    return {'success': True}
