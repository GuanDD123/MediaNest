from pathlib import Path
from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import FileResponse
from media_nest.repository.repository import Repository
from media_nest.service.service import Service
from media_nest.web.dependence import get_repository


router = APIRouter()


@router.get('/root')
def get_all(repository: Repository = Depends(get_repository)):
    service = Service(repository)
    return service.get_all_root()


@router.get('/folder/{path:path}')
def get_in_folder(path: str, repository: Repository = Depends(get_repository)):
    service = Service(repository)
    return service.get_all_in_folder(Path('/' + path))


@router.get('/image/{path:path}')
@router.api_route("/video/{path:path}", methods=["GET", "HEAD"])
def get_media(path: str):
    return FileResponse('/' + path)


@router.api_route('/playlist/{parent_path:path}', methods=["GET", "HEAD"])
def playlist(request: Request, parent_path: str, shuffle_flag: bool = False,
             repository: Repository = Depends(get_repository)):
    service = Service(repository)
    m3u = service.build_m3u(Path('/' + parent_path), shuffle_flag)
    if request.method == "HEAD":
        return Response(headers={
            "Content-Type": "application/vnd.apple.mpegurl"
        })
    return Response(content=m3u, media_type="audio/x-mpegurl")
