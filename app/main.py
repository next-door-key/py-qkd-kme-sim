from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.dependencies import get_settings
from app.internal.after_landing import after_landing
from app.internal.before_start import before_start
from app.routers import keys


@asynccontextmanager
async def lifespan(api: FastAPI):
    settings = get_settings()

    before_start(api, settings)
    yield
    after_landing(api, settings)


app = FastAPI(lifespan=lifespan)

app.include_router(keys.router)


@app.get('/')
async def index():
    return {'message': 'Hello, World!'}
