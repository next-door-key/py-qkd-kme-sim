from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings
from app.dependencies import get_settings, get_lifecycle, get_kme_and_sae_ids_from_slave_id, \
    get_kme_and_sae_ids_from_master_id
from app.enums.initiated_by import InitiatedBy
from app.internal.lifecycle import Lifecycle
from app.models.key_container import KeyContainer
from app.models.requests import PostEncryptionKeysRequest, GetEncryptionKeysRequest, GetDecryptionKeysRequest, \
    PostDecryptionKeysRequest

router = APIRouter(
    prefix='/keys',
    tags=['keys'],
    responses={404: {'message': 'Not found'}}
)


@router.get('/{slave_sae_id}/status')
async def status(
        slave_sae_id: str,
        settings: Annotated[Settings, Depends(get_settings)],
        lifecycle: Annotated[Lifecycle, Depends(get_lifecycle)]
):
    ids = get_kme_and_sae_ids_from_slave_id(slave_sae_id)

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
    ids = get_kme_and_sae_ids_from_slave_id(slave_sae_id)

    if slave_sae_id == settings.attached_sae_id:
        raise HTTPException(status_code=400,
                            detail='Unable, because this endpoint should be called by the other KME with this SAE ID')

    key_count = lifecycle.key_manager.get_key_count()

    if key_count <= 0:
        raise HTTPException(status_code=400, detail='Unable, because there are 0 keys remaining')

    if key_count - query.number <= 0:
        raise HTTPException(status_code=400, detail='Unable, because more keys are requested than available')

    keys: list[KeyContainer] = []

    # TODO: Handle size
    for i in range(query.number):
        key = await lifecycle.key_manager.get_key(
            master_sae_id=ids.master_sae_id,
            slave_sae_id=ids.slave_sae_id,
        )

        keys.append(key.key_container.key_container)

    return {'keys': keys}


@router.post('/{slave_sae_id}/enc_keys')
async def post_encryption_keys(
        slave_sae_id: str,
        settings: Annotated[Settings, Depends(get_settings)],
        lifecycle: Annotated[Lifecycle, Depends(get_lifecycle)],
        data: PostEncryptionKeysRequest
):
    ids = get_kme_and_sae_ids_from_slave_id(slave_sae_id)

    if slave_sae_id == settings.attached_sae_id:
        raise HTTPException(status_code=400,
                            detail='Unable, because this endpoint should be called by the other KME with this SAE ID')

    key_count = lifecycle.key_manager.get_key_count()

    if key_count <= 0:
        raise HTTPException(status_code=400, detail='Unable, because there are 0 keys remaining')

    if key_count - data.number <= 0:
        raise HTTPException(status_code=400, detail='Unable, because more keys are requested than available')

    keys: list[KeyContainer] = []

    # TODO: Handle size
    # TODO: Throw error on usage of additional_SAE_ids and the usage of any of the extensions
    for i in range(data.number):
        key = await lifecycle.key_manager.get_key(
            master_sae_id=ids.master_sae_id,
            slave_sae_id=ids.slave_sae_id,
            initiated_by=InitiatedBy.MASTER if settings.is_master else InitiatedBy.SLAVE
        )

        keys.append(key.key_container.key_container)

    return {'keys': keys}


@router.get('/{master_sae_id}/dec_keys')
async def get_decryption_keys(
        master_sae_id: str,
        settings: Annotated[Settings, Depends(get_settings)],
        lifecycle: Annotated[Lifecycle, Depends(get_lifecycle)],
        query: GetDecryptionKeysRequest = Depends()
):
    ids = get_kme_and_sae_ids_from_master_id(master_sae_id)

    if master_sae_id == settings.attached_sae_id:
        raise HTTPException(status_code=400,
                            detail='Unable, because this endpoint should be called by the other KME with this SAE ID')

    key_count = lifecycle.key_manager.get_activated_key_count()

    if key_count <= 0:
        raise HTTPException(status_code=400, detail='Unable, because there are 0 activated keys remaining')

    activated_key = lifecycle.key_manager.get_activated_key_metadata(str(query.key_ID))

    if activated_key is None:
        raise HTTPException(status_code=400,
                            detail='Unable, the key was not found by id')

    if activated_key.master_sae_id != master_sae_id:
        raise HTTPException(status_code=400,
                            detail='Unable, because the master sae id doesnt match the keys master sae id')

    key = await lifecycle.key_manager.deactivate_key(
        key_id=str(query.key_ID),
    )

    return {'keys': [key.key_container.key_container]}


@router.post('/{master_sae_id}/dec_keys')
async def get_decryption_keys(master_sae_id: str, data: PostDecryptionKeysRequest):
    return {'master_sae_id': master_sae_id, 'data': data.model_dump()}
