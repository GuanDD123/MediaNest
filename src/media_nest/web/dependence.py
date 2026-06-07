from fastapi import Request

from media_nest.repository.repository import Repository


def get_repository(request: Request) -> Repository:
    return request.app.state.repository
