from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.dependencies import get_settings
from app.internal.lifecycle import Lifecycle
from app.routers import keys, internal


@asynccontextmanager
async def lifespan(api: FastAPI):
    settings = get_settings()
    lifecycle = Lifecycle(api, settings)

    api.lifecycle = lifecycle

    await lifecycle.before_start()
    yield
    await lifecycle.after_landing()


app = FastAPI(lifespan=lifespan)
app.add_middleware(HTTPSRedirectMiddleware)

app.include_router(router=internal.router, prefix='/api/v1')
app.include_router(router=keys.router, prefix='/api/v1')


@app.get('/')
async def index():
    return {'message': 'Hello, World!'}
