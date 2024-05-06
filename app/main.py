from fastapi import FastAPI

from app.routers import keys

app = FastAPI()

app.include_router(keys.router)


@app.get('/')
async def index():
    return {'message': 'Hello, World!'}
