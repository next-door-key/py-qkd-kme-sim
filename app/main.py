from contextlib import asynccontextmanager
from typing import Union

from fastapi import FastAPI

from app.dependencies import get_settings
from app.internal.lifecycle import Lifecycle
from app.routers import keys

LIFECYCLE: Union[Lifecycle, None] = None


@asynccontextmanager
async def lifespan(api: FastAPI):
    global LIFECYCLE

    settings = get_settings()
    LIFECYCLE = Lifecycle(api, settings)

    await LIFECYCLE.before_start()
    yield
    await LIFECYCLE.after_landing()


app = FastAPI(lifespan=lifespan)

app.include_router(keys.router, prefix='/api/v1')


@app.get('/')
async def index():
    return {'message': 'Hello, World!'}
