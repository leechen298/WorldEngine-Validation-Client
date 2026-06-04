from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .config import get_settings
from .db import init_db
from .routes import evidence, health, sessions, timelines, validation_runs


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    init_db(settings.database_path)
    yield


app = FastAPI(title="WorldEngine Validation Client", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(get_settings().allowed_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(timelines.router)
app.include_router(evidence.router)
app.include_router(validation_runs.router)
