import asyncio
from typing import Annotated

from fastapi import APIRouter, Body, Depends, WebSocket
from pydantic import BaseModel

from media_nest.logs import logger
from media_nest.service import Service

from .dependencies import get_service

router = APIRouter(prefix="/admin")


@router.post("/add_root")
def add_root(
    service: Annotated[Service, Depends(get_service)], path: Annotated[str, Body()]
):
    service.add_root(path)
    return {"success": True}


@router.post("/delete_root")
def delete_root(
    service: Annotated[Service, Depends(get_service)], path: Annotated[str, Body()]
):
    service.delete_root(path)
    return {"success": True}


@router.post("/clear_root")
def clear_root(service: Annotated[Service, Depends(get_service)]):
    service.clear_root()
    return {"success": True}


@router.post("/sync")
def sync(service: Annotated[Service, Depends(get_service)]):
    if not service.sync():
        return {"success": False, "message": "Sync is already in progress"}
    return {"success": True}


@router.websocket("/sync/progress")
async def sync_progress(ws: WebSocket):
    await ws.accept()
    service: Service = ws.app.state.service

    try:
        while True:
            await ws.send_json(service.get_sync_progress())

            if service.future is None or service.future.done():
                await ws.send_json(service.get_sync_progress())
                break

            await asyncio.sleep(0.2)
    except Exception:  # noqa: BLE001
        logger.exception("Error occurred while fetching sync progress")
    finally:
        await ws.close()


@router.post("/clear_cache")
def clear_cache(service: Annotated[Service, Depends(get_service)]):
    service.clear_cache()
    return {"success": True}


class MarkRequest(BaseModel):
    id: int
    marked: bool


@router.post("/mark")
def mark(service: Annotated[Service, Depends(get_service)], data: MarkRequest):
    service.mark(data.id, data.marked)
    return {"success": True}


class DeleteRequest(BaseModel):
    id: int
    path: str
    additional_path_list: list[str]


@router.post("/delete")
def delete_file(service: Annotated[Service, Depends(get_service)], data: DeleteRequest):
    service.delete_file(data.id, data.path, data.additional_path_list)
    return {"success": True}
