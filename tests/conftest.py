import sqlite3
import pytest

from media_nest.core.db_manager import DataBaseManager
from media_nest.repository.repository import Repository


@pytest.fixture
def database():
    database = DataBaseManager('')
    database.connection = sqlite3.connect(':memory:')
    database.init()
    yield database
    database.close()


@pytest.fixture
def repository(database):
    return Repository(database)
