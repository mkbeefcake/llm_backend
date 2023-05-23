import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from core.config import settings
from apis.route import api_router

def include_router(app):
    app.include_router(api_router)

def application_start():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)
    return app

app = application_start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)