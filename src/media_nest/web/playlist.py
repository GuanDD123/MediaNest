from pathlib import Path
from fastapi import APIRouter, Depends, Response, Request

from media_nest.repository.repository import Repository
from media_nest.service.build_m3u import BuildM3u
from media_nest.web.dependence import get_repository


router = APIRouter(prefix='/playlist')


@router.api_route('/{parent_path:path}', methods=['GET', 'HEAD'])
def playlist(request: Request, parent_path: str, shuffle_flag: bool = False,
             repository: Repository = Depends(get_repository)):
    m3u = BuildM3u(repository).run(Path('/' + parent_path), shuffle_flag)
    print(m3u)
    if request.method == 'HEAD':
        return Response(headers={
            'Content-Type': 'application/vnd.apple.mpegurl'
        })
    return Response(content=m3u, media_type='audio/x-mpegurl')
