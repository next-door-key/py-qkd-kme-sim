from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings
from app.dependencies import get_token_header, get_settings, get_lifecycle, get_kme_and_sae_ids
from app.enums.initiated_by import InitiatedBy
from app.internal.lifecycle import Lifecycle
from app.models.key_container import KeyContainer
from app.models.requests import PostEncryptionKeysRequest, GetEncryptionKeysRequest, GetDecryptionKeysRequest, \
    PostDecryptionKeysRequest

router = APIRouter(
    prefix='/keys',
    tags=['keys'],
    dependencies=[Depends(get_token_header)],
    responses={404: {'message': 'Not found'}}
)


@router.get('/{slave_sae_id}/status')
async def status(
        slave_sae_id: str,
        settings: Annotated[Settings, Depends(get_settings)],
        lifecycle: Annotated[Lifecycle, Depends(get_lifecycle)]
):
    ids = get_kme_and_sae_ids(slave_sae_id)

    return {
        'source_KME_ID': ids.master_kme_id,
        'target_KME_ID': ids.slave_kme_id,
        'master_SAE_ID': ids.master_sae_id,
        'slave_SAE_ID': ids.slave_sae_id,
        'key_size': settings.default_key_size,
        'stored_key_count': lifecycle.key_manager.get_key_count(),
        'max_key_count': settings.max_key_count,
        'max_key_per_request': settings.max_keys_per_request,
        'max_key_size': settings.max_key_size,
        'min_key_size': settings.min_key_size,
        'max_SAE_ID_count': 0,
    }


@router.get('/{slave_sae_id}/enc_keys')
async def get_encryption_keys(
        slave_sae_id: str,
        settings: Annotated[Settings, Depends(get_settings)],
        lifecycle: Annotated[Lifecycle, Depends(get_lifecycle)],
        query: GetEncryptionKeysRequest = Depends()
):
    ids = get_kme_and_sae_ids(slave_sae_id)

    key_count = lifecycle.key_manager.get_key_count()

    if key_count <= 0:
        raise HTTPException(status_code=400, detail='Unable, because there are 0 keys remaining')

    if key_count - query.number <= 0:
        raise HTTPException(status_code=400, detail='Unable, because more keys are requested than available')

    keys: list[KeyContainer] = []

    for i in range(query.number):
        key = await lifecycle.key_manager.get_key(
            master_sae_id=ids.master_sae_id,
            slave_sae_id=ids.slave_sae_id,
            initiated_by=InitiatedBy.MASTER if settings.is_master else InitiatedBy.SLAVE
        )

        keys.append(key.key_container.key_container)

    return {'keys': keys}


@router.post('/{slave_sae_id}/enc_keys')
async def post_encryption_keys(slave_sae_id: str, data: PostEncryptionKeysRequest):
    return {'slave_sae_id': slave_sae_id, 'data': data.model_dump()}


@router.get('/{master_sae_id}/dec_keys')
async def get_decryption_keys(master_sae_id: str, query: GetDecryptionKeysRequest = Depends()):
    return {'master_sae_id': master_sae_id, 'query': query.model_dump()}


@router.post('/{master_sae_id}/dec_keys')
async def get_decryption_keys(master_sae_id: str, data: PostDecryptionKeysRequest):
    return {'master_sae_id': master_sae_id, 'data': data.model_dump()}
