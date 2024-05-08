from functools import lru_cache
from typing import Annotated, Union

from fastapi import Header, HTTPException
from starlette.requests import Request

from app.config import Settings
from app.internal.lifecycle import Lifecycle


async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


@lru_cache
def get_settings():
    return Settings()


def get_lifecycle(request: Request) -> Union[Lifecycle, None]:
    return request.app.lifecycle
