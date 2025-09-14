import logging.config
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi_structlog.middleware import StructlogMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import application_settings
from app.infrastructure.db.engine import dispose_db_engine
from app.logging import LOGGING
from app.presentation import routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await dispose_db_engine()


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

app.include_router(routes.router)

if __name__ == '__main__':
    uvicorn.run(
        'app.main:app',
        host=application_settings.app_host,
        port=application_settings.app_port,
        reload=True,
    )
