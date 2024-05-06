from functools import lru_cache
from typing import Annotated

from fastapi import Header, HTTPException

from app.config import Settings


async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


@lru_cache
def get_settings():
    return Settings()
