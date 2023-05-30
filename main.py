import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from core.config import settings
from apis.route import api_router
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware


def include_router(app):
    app.include_router(api_router)


def add_middleware(app):
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def application_start():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)
    add_middleware(app)
    return app


app = application_start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
