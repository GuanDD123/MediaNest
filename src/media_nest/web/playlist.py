from fastapi import APIRouter, Depends, Response, Request

from media_nest.repository import Repository
from media_nest.service import Service
from media_nest.web.dependence import get_repository

router = APIRouter(prefix="/playlist")


@router.api_route("/{parent_path:path}", methods=["GET", "HEAD"])
def playlist(
    request: Request,
    parent_path: str,
    shuffle_flag: bool = False,
    repository: Repository = Depends(get_repository),
):
    m3u = Service(repository).build_m3u(parent_path, shuffle_flag)
    if request.method == "HEAD":
        return Response(headers={"Content-Type": "application/vnd.apple.mpegurl"})
    return Response(content=m3u, media_type="audio/x-mpegurl")
