import os
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import FileResponse

from media_nest.service import Service

from .dependencies import get_service

router = APIRouter(prefix="/media")


@router.get("/image")
@router.get("/video")
def get_media(path: str):
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {path}",
        )
    return FileResponse(path, headers={"cache-control": "public, max-age=86400"})


@router.get("/thumb")
def get_thumb(path: str):
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {path}",
        )
    return FileResponse(path, headers={"cache-control": "public, max-age=2592000"})


@router.get("/root")
def get_all_root(service: Annotated[Service, Depends(get_service)]):
    return service.get_all_root()


@router.get("/folder")
def get_all_in_folder(service: Annotated[Service, Depends(get_service)], path: str):
    return service.get_all_in_folder(path)


@router.get("/filter_marked")
def filter_marked(service: Annotated[Service, Depends(get_service)]):
    return service.filter_marked()


@router.post("/playlist")
def save_playlist(playlist: Annotated[list[dict], Body()]):
    Service.save_playlist(playlist)
    return {"success": True}


@router.post("/progress")
def save_progress(index: Annotated[int, Body()]):
    Service.save_progress(index)
    return {"success": True}


@router.get("/continue_last_play")
def continue_last_play():
    return Service.continue_last_play()
