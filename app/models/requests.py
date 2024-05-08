from typing import Annotated

from fastapi import Path, Query
from pydantic import BaseModel

from app.dependencies import get_settings

settings = get_settings()


class GetEncryptionKeysRequest(BaseModel):
    number: Annotated[int, Query(ge=1)] = 1
    size: Annotated[
        int, Query(ge=settings.min_key_size, le=settings.max_key_size, multiple_of=8)] = settings.default_key_size


class PostEncryptionKeysRequest(BaseModel):
    number: Annotated[int, Path(ge=1)] = 1
    size: Annotated[
        int, Path(ge=settings.min_key_size, le=settings.max_key_size, multiple_of=8)] = settings.default_key_size
    additional_slave_SAE_IDs: list[str] = []
    extension_mandatory: list[dict] = []
    extension_optional: list[dict] = []
