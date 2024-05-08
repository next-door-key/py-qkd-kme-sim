from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.dependencies import get_settings
from app.internal.lifecycle import Lifecycle
from app.routers import keys


@asynccontextmanager
async def lifespan(api: FastAPI):
    settings = get_settings()
    lifecycle = Lifecycle(api, settings)

    api.lifecycle = lifecycle

    await lifecycle.before_start()
    yield
    await lifecycle.after_landing()


app = FastAPI(lifespan=lifespan)

app.include_router(router=keys.router, prefix='/api/v1')


@app.get('/')
async def index():
    return {'message': 'Hello, World!'}
