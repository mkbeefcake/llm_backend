import os
import sys
from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apis.route import api_router

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def start_application():
    app = FastAPI()
    app.include_router(api_router)
    return app


@pytest.fixture(scope="function")
def app() -> Generator[FastAPI, Any, None]:
    _app = start_application()
    yield _app


@pytest.fixture(scope="function")
def client(app: FastAPI) -> Generator[TestClient, Any, None]:
    with TestClient(app) as client:
        yield client
