from fastapi import APIRouter, Request, Body, WebSocket
import asyncio

from media_nest.logs import logger

router = APIRouter(prefix="/admin")


@router.post("/add_root")
def add_root(request: Request, path: str = Body(...)):
    request.app.state.service.add_root(path)
    return {"success": True}


@router.post("/delete_root")
def delete_root(request: Request, path: str = Body(...)):
    request.app.state.service.delete_root(path)
    return {"success": True}


@router.post("/clear_root")
def clear_root(request: Request):
    request.app.state.service.clear_root()
    return {"success": True}


@router.post("/sync")
def sync(request: Request):
    if not request.app.state.service.sync():
        return {"success": False, "message": "Sync is already in progress"}
    return {"success": True}

@router.websocket("/sync/progress")
async def sync_progress(ws: WebSocket):
    await ws.accept()
    service = ws.app.state.service

    try:
        while True:
            await ws.send_json(service.get_sync_progress())

            if service.future is None or service.future.done():
                await ws.send_json(service.get_sync_progress())
                break

            await asyncio.sleep(0.2)
    except Exception:
        logger.exception("Error occurred while fetching sync progress")
    finally:
        await ws.close()


@router.post("/clear_cache")
def clear_cache(request: Request):
    request.app.state.service.clear_cache()
    return {"success": True}


@router.post("/mark")
def mark(request: Request, data: dict[str, int | bool] = Body(...)):
    request.app.state.service.mark(data["id"], data["marked"])
    return {"success": True}


@router.post("/delete")
def delete_file(request: Request, data: dict[str, int | str | list[str]] = Body(...)):
    request.app.state.service.delete_file(
        data["id"], data["path"], data["additional_path_list"]
    )
    return {"success": True}
