import sqlite3

import pytest

from media_nest.core.db_manager import DataBaseManager
from media_nest.core.settings import load_settings
from media_nest.repository import Repository


@pytest.fixture(scope="class", autouse=False)
def get_repository(request):
    database = DataBaseManager("")
    database.connection = sqlite3.connect(":memory:")
    database.init()

    request.cls.settings = load_settings()
    request.cls.repository = Repository(database)
    yield

    database.close()
