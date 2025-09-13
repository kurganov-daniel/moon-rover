import logging.config
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi_structlog.middleware import StructlogMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import application_settings
from app.logging import LOGGING


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


logging.config.dictConfig(LOGGING)

app = FastAPI(
    title=application_settings.api_title,
    description=application_settings.api_description,
    version=application_settings.api_version,
    lifespan=lifespan,
)

app.add_middleware(StructlogMiddleware)

instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)

if __name__ == '__main__':
    uvicorn.run(
        'app.main:app',
        host=application_settings.app_host,
        port=application_settings.app_port,
        reload=True,
    )
