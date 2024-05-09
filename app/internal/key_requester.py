import requests

from app.config import Settings
from app.models.key_container import ActivatedKeyContainer


def ask_for_key(master_sae_id: str, slave_sae_id: str) -> ActivatedKeyContainer:
    kme_address = Settings()

    response = requests.post(f'{kme_address}/api/v1/internal/ask_for_key', json={
        'master_sae_id': master_sae_id,
        'slave_sae_id': slave_sae_id
    })

    return response.json()['data']


def ask_to_deactivate_key(activated_key: ActivatedKeyContainer):
    kme_address = Settings()

    response = requests.post(f'{kme_address}/api/v1/internal/deactivate_key', json={
        'activated_key': activated_key,
    })

    return response.json()['data']
