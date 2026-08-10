from fastapi import Request

from media_nest.service import Service


def get_service(request: Request) -> Service:
    return request.app.state.service
