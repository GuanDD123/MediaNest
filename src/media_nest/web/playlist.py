from fastapi import APIRouter, Request, Response

router = APIRouter(prefix="/playlist")


@router.api_route("/{parent_path:path}", methods=["GET", "HEAD"])
def build_m3u(
    request: Request,
    parent_path: str,
    shuffle_flag: bool = False,
):
    m3u = request.app.state.service.build_m3u(parent_path, shuffle_flag)
    if request.method == "HEAD":
        return Response(headers={"Content-Type": "application/vnd.apple.mpegurl"})
    return Response(content=m3u, media_type="audio/x-mpegurl")
