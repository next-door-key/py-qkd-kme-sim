from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import Settings
from app.dependencies import get_token_header, get_settings
from app.models.requests import PostEncryptionKeysRequest, GetEncryptionKeysRequest, GetDecryptionKeysRequest, \
    PostDecryptionKeysRequest

router = APIRouter(
    prefix='/keys',
    tags=['keys'],
    dependencies=[Depends(get_token_header)],
    responses={404: {'message': 'Not found'}}
)


@router.get('/{slave_sae_id}/status')
async def status(slave_sae_id: str, settings: Annotated[Settings, Depends(get_settings)]):
    return {'slave_sae_id': slave_sae_id, 'settings': settings.model_dump()}


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
