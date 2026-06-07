from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from media_nest.repository.repository import Repository
from media_nest.service.service import Service
from media_nest.web.dependence import get_repository


router = APIRouter(prefix='/media')


@router.get('/root')
def get_all(repository: Repository = Depends(get_repository)):
    service = Service(repository)
    return service.get_all_root()


@router.get('/folder/{path:path}')
def get_in_folder(path: str, repository: Repository = Depends(get_repository)):
    service = Service(repository)
    return service.get_all_in_folder(Path('/' + path))


@router.get('/image/{path:path}')
@router.get('/video/{path:path}')
def get_media(path: str):
    return FileResponse('/' + path)
