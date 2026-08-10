from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from media_nest.service.service import Service

from .dependencies import get_service

router = APIRouter(prefix="/playlist")


@router.api_route("/", methods=["GET", "HEAD"])
def build_m3u(
    request: Request,
    service: Annotated[Service, Depends(get_service)],
    parent_path: str,
    shuffle_flag: bool = False,
):
    m3u = service.build_m3u(parent_path, shuffle_flag)
    if request.method == "HEAD":
        return Response(headers={"Content-Type": "application/vnd.apple.mpegurl"})
    return Response(content=m3u, media_type="audio/x-mpegurl")
