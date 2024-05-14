import requests

from app.config import Settings
from app.models.key_container import ActivatedKeyContainer


def ask_for_key(master_sae_id: str, slave_sae_id: str, size: int) -> ActivatedKeyContainer:
    kme_address = Settings().linked_to_kme

    response = requests.post(f'{kme_address}/api/v1/internal/ask_for_key', json={
        'master_sae_id': master_sae_id,
        'slave_sae_id': slave_sae_id,
        'size': size
    }).json()

    if 'detail' in response:
        raise RuntimeError(f'Something went wrong trying to deactivate a key, response: {response}')

    return ActivatedKeyContainer(
        **response['data']
    )


def ask_to_deactivate_key(activated_key: ActivatedKeyContainer):
    kme_address = Settings().linked_to_kme

    response = requests.post(f'{kme_address}/api/v1/internal/deactivate_key', json={
        'key_ID': str(activated_key.key_ID),
    }).json()

    if 'detail' in response:
        raise RuntimeError(f'Something went wrong trying to deactivate a key, response: {response}')

    return ActivatedKeyContainer(
        **response['data']
    )
