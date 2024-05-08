from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings
from app.dependencies import get_token_header, get_settings, get_lifecycle
from app.internal.lifecycle import Lifecycle
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
    # Validate if we can find the given slave SAE's KME
    if slave_sae_id == settings.attached_sae_id:
        source_kme_id = settings.linked_kme_id
        target_kme_id = settings.kme_id

        master_sae_id = settings.linked_sae_id
    elif slave_sae_id == settings.linked_sae_id:
        source_kme_id = settings.kme_id
        target_kme_id = settings.linked_kme_id

        master_sae_id = settings.attached_sae_id
    else:
        raise HTTPException(status_code=400, detail=f'Linked KME with linked SAE ID {slave_sae_id} is not found')

    return {
        'source_KME_ID': source_kme_id,
        'target_KME_ID': target_kme_id,
        'master_SAE_ID': master_sae_id,
        'slave_SAE_ID': slave_sae_id,
        'key_size': settings.default_key_size,
        'stored_key_count': lifecycle.key_manager.get_key_count(),
        'max_key_count': settings.max_key_count,
        'max_key_per_request': settings.max_keys_per_request,
        'max_key_size': settings.max_key_size,
        'min_key_size': settings.min_key_size,
        'max_SAE_ID_count': 0,
    }


@router.get('/{slave_sae_id}/enc_keys')
async def get_encryption_keys(slave_sae_id: str, query: GetEncryptionKeysRequest = Depends()):
    return {'slave_sae_id': slave_sae_id, 'query': query.model_dump()}


@router.post('/{slave_sae_id}/enc_keys')
async def post_encryption_keys(slave_sae_id: str, data: PostEncryptionKeysRequest):
    return {'slave_sae_id': slave_sae_id, 'data': data.model_dump()}


@router.get('/{master_sae_id}/dec_keys')
async def get_decryption_keys(master_sae_id: str, query: GetDecryptionKeysRequest = Depends()):
    return {'master_sae_id': master_sae_id, 'query': query.model_dump()}


@router.post('/{master_sae_id}/dec_keys')
async def get_decryption_keys(master_sae_id: str, data: PostDecryptionKeysRequest):
    return {'master_sae_id': master_sae_id, 'data': data.model_dump()}
