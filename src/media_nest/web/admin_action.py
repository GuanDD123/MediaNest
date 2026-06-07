from fastapi import APIRouter, Depends

from media_nest.repository.repository import Repository
from media_nest.service.service import Service
from media_nest.web.dependence import get_repository

router = APIRouter(prefix='/admin')


@router.post("/sync")
def sync(repository: Repository = Depends(get_repository)):
    service = Service(repository)
    return service.sync()


@router.post("/clear_cache")
def clear_cache(repository: Repository = Depends(get_repository)):
    service = Service(repository)
    return service.clear_cache()
