import uvicorn
from fastapi import FastAPI, Response
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from media_nest.core.constant import DB_PATH
from media_nest.core.db_manager import DataBaseManager
from media_nest.repository.repository import Repository
from media_nest.web.media import router as media_router
from media_nest.web.admin_action import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = DataBaseManager(DB_PATH)
    database.connect()
    database.init()

    app.state.repository = Repository(database)

    yield

    database.close()

app = FastAPI(lifespan=lifespan)


@app.get('/favicon.ico')
async def favicon():
    return Response(status_code=204)

app.include_router(media_router)
app.include_router(admin_router)

app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('/')
@app.get('/index')
async def index():
    return FileResponse('static/index.html')


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
