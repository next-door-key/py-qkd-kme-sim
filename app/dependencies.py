from functools import lru_cache
from typing import Annotated, Union

from fastapi import Header, HTTPException
from starlette.requests import Request

from app.config import Settings
from app.internal.lifecycle import Lifecycle
from app.models.kme_sae_ids import KmeSaeIds


async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


def get_kme_and_sae_ids(slave_sae_id: str) -> KmeSaeIds:
    settings = get_settings()

    if slave_sae_id == settings.attached_sae_id:
        master_kme_id = settings.linked_kme_id
        slave_kme_id = settings.kme_id

        master_sae_id = settings.linked_sae_id
    elif slave_sae_id == settings.linked_sae_id:
        master_kme_id = settings.kme_id
        slave_kme_id = settings.linked_kme_id

        master_sae_id = settings.attached_sae_id
    else:
        raise HTTPException(status_code=400, detail=f'Linked KME with linked SAE ID {slave_sae_id} is not found')

    return KmeSaeIds(
        master_kme_id=master_kme_id,
        slave_kme_id=slave_kme_id,
        master_sae_id=master_sae_id,
        slave_sae_id=slave_sae_id
    )


@lru_cache
def get_settings():
    return Settings()


def get_lifecycle(request: Request) -> Union[Lifecycle, None]:
    return request.app.lifecycle
