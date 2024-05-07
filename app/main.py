from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.dependencies import get_settings
from app.internal.lifecycle import Lifecycle
from app.routers import keys

lifecycle = None


@asynccontextmanager
async def lifespan(api: FastAPI):
    global lifecycle

    settings = get_settings()
    lifecycle = Lifecycle(api, settings)

    await lifecycle.before_start()
    yield
    await lifecycle.after_landing()


app = FastAPI(lifespan=lifespan)

app.include_router(keys.router, prefix='/api/v1')


@app.get('/')
async def index():
    return {'message': 'Hello, World!'}
