from typing import Union
from uuid import UUID

from pydantic import BaseModel


class KeyContainer(BaseModel):
    key_ID: UUID
    key: str


class FullKeyContainer(BaseModel):
    key_container: KeyContainer


class KeyIDContainer(BaseModel):
    key_ID: UUID
    key_ID_extension: Union[dict, None] = None
