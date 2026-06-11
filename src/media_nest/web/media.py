from fastapi import APIRouter, Depends, Body
from fastapi.responses import FileResponse

from media_nest.repository import Repository
from media_nest.service import Service
from media_nest.web.dependence import get_repository

router = APIRouter(prefix="/media")


@router.get("/root")
def get_all_root(repository: Repository = Depends(get_repository)):
    return Service(repository).get_all_root()


@router.get("/folder/{path:path}")
def get_all_in_folder(
    path: str,
    repository: Repository = Depends(get_repository),
):
    return Service(repository).get_all_in_folder("/" + path)


@router.get("/image/{path:path}")
@router.get("/video/{path:path}")
def get_media(path: str):
    return FileResponse("/" + path)


@router.get("/filter_marked")
def filter_marked(repository: Repository = Depends(get_repository)):
    return Service(repository).filter_marked()


@router.post("/playlist")
def save_playlist(playlist: list[list[dict], list[dict]] = Body(...)):
    Service.save_playlist(playlist)
    return {"success": True}


@router.post("/progress")
def save_progress(index: int = Body(...)):
    Service.save_progress(index)
    return {"success": True}


@router.get("/continue_last_play")
def continue_last_play(repository: Repository = Depends(get_repository)):
    return Service(repository).continue_last_play()
