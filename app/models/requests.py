from typing import Annotated, Union
from uuid import UUID

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
    additional_slave_SAE_IDs: Union[list[str], None] = None
    extension_mandatory: Union[list[dict], None] = None
    extension_optional: Union[list[dict], None] = None


class GetDecryptionKeysRequest(BaseModel):
    key_ID: UUID


class KeyContainer(BaseModel):
    key_ID: UUID
    key_ID_extension: Union[dict, None] = None


class PostDecryptionKeysRequest(BaseModel):
    key_IDs: Annotated[list[KeyContainer], Path(min_length=1)]
    key_IDs_extension: Union[dict, None] = None