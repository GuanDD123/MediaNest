from fastapi import Request

from media_nest.repository.repository import Repository


def get_repository(request: Request):
    database = request.app.state.database
    database.connect()
    try:
        yield Repository(database)
    finally:
        database.close()
