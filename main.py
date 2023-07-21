import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from apis.route import api_router
from core.config import settings
from products.pinecone import pinecone_service


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


description = f"""
<i>{settings.PROJECT_NAME}</i> API helps you understand the system and makes you easier to consume the service.
<i>{settings.PROJECT_NAME}</i> system will automate the communication by using AI models.<br>
This connects with GMail, Replica providers and will add more 3rd party providers in future.<br>

Here are some terms to make you understand the system.<br><br>
<i>provider</i> : the service which the system supports for communication by using AI models.<br>
<i>end-user</i> : the user which signs in the system.<br>
<i>account</i>  : the end-user can have multiple accounts which provided by provider system.<br>
<i>user</i>     : the user which the account communicates on the provider system.<br>
"""


def application_start():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=description,
        version=settings.PROJECT_VERSION,
    )
    include_router(app)
    add_middleware(app)
    return app


app = application_start()


@app.get("/probe")
async def probe():
    return {"message": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
