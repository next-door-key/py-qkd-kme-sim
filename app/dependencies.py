from functools import lru_cache
from typing import Union

from fastapi import HTTPException
from starlette.requests import Request

from app.config import Settings
from app.internal.lifecycle import Lifecycle
from app.models.kme_sae_ids import KmeSaeIds


def get_kme_and_sae_ids_from_slave_id(slave_sae_id: str) -> KmeSaeIds:
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


def get_kme_and_sae_ids_from_master_id(master_sae_id: str) -> KmeSaeIds:
    settings = get_settings()

    if master_sae_id == settings.linked_sae_id:
        master_kme_id = settings.linked_kme_id
        slave_kme_id = settings.kme_id

        slave_sae_id = settings.attached_sae_id
    elif master_sae_id == settings.attached_sae_id:
        master_kme_id = settings.kme_id
        slave_kme_id = settings.linked_kme_id

        slave_sae_id = settings.linked_sae_id
    else:
        raise HTTPException(status_code=400, detail=f'Linked KME with linked SAE ID {master_sae_id} is not found')

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
