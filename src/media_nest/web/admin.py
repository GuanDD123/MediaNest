from fastapi import APIRouter, Depends, Body

from media_nest.repository import Repository
from media_nest.service import Service
from media_nest.web.dependence import get_repository

router = APIRouter(prefix="/admin")


@router.post("/add_root")
def add_root(path: str = Body(...), repository: Repository = Depends(get_repository)):
    Service(repository).add_root(path)
    return {"success": True}


@router.post("/delete_root")
def delete_root(
    path: str = Body(...), repository: Repository = Depends(get_repository)
):
    Service(repository).delete_root(path)
    return {"success": True}


@router.post("/clear_root")
def clear_root(repository: Repository = Depends(get_repository)):
    Service(repository).clear_root()
    return {"success": True}


@router.post("/sync")
def sync(repository: Repository = Depends(get_repository)):
    Service(repository).sync()
    return {"success": True}


@router.post("/clear_cache")
def clear_cache(repository: Repository = Depends(get_repository)):
    Service(repository).clear_cache()
    return {"success": True}


@router.post("/mark")
def mark(
    data: dict[str, int | bool] = Body(...),
    repository: Repository = Depends(get_repository),
):
    Service(repository).mark(data["id"], data["marked"])
    return {"success": True}


@router.post("/delete")
def delete_file(
    data: dict[str, int | str] = Body(...),
    repository: Repository = Depends(get_repository),
):
    Service(repository).delete_file(data["id"], data["path"])
    return {"success": True}
