import asyncio
import base64
import sys
from typing import Any

import requests

# <KME URL>, <ATTACHED SAE ID>
KME_1 = {'url': 'http://localhost:8000', 'sae_id': 'foo-bar'}
KME_2 = {'url': 'http://localhost:9000', 'sae_id': 'bar-foo'}

KEY_SIZE = 256


def _get_request(url: str) -> Any:
    response = requests.get(url)

    if response.status_code != 200:
        print(response.json())

    response.raise_for_status()

    return response.json()


async def wait_for_ready_key_stores() -> int:
    for kme_url in [KME_1['url'], KME_2['url']]:
        while True:
            response = _get_request(f'{kme_url}/api/v1/internal/key_stores')

            if len(response['activated_keys']) != 0:
                print(f'ERR: There are already activated keys for KME {kme_url}, please clear')

                return 2

            if len(response['keys']) > 1:
                break

            await asyncio.sleep(2)

    return 0


async def test_sequence_from_kme_a_to_kme_b(kme_a_url: str, kme_a_sae_id: str,
                                            kme_b_url: str, kme_b_sae_id: str) -> int:
    assert await wait_for_ready_key_stores() == 0, 'The key store status returned an error'

    # Activate key
    response = _get_request(f'{kme_a_url}/api/v1/keys/{kme_b_sae_id}/enc_keys?size={KEY_SIZE}')
    key_id = response['keys'][0]['key_ID']

    # Check if key is now activated for both instances
    for i, kme_url in enumerate([kme_a_url, kme_b_url]):
        i = i + 1

        response = _get_request(f'{kme_url}/api/v1/internal/key_stores')

        assert len(response['activated_keys']) > 0, f'There are no activated keys for KME {i}'

        key_found = False

        for key in response['activated_keys']:
            if (
                    key['master_sae_id'] == kme_a_sae_id and
                    key['slave_sae_id'] == kme_b_sae_id and
                    key['key_ID'] == key_id and
                    key['size'] == KEY_SIZE and
                    len(base64.b64decode(key['key'])) == KEY_SIZE
            ):
                key_found = True

        assert key_found, f'The activated key was not found in the KME {i}'

    # Ask for decryption
    response = _get_request(f'{kme_b_url}/api/v1/keys/{kme_a_sae_id}/dec_keys?key_ID={key_id}')

    assert response['keys'][0]['key_ID'] == key_id, 'The decryption key does not match in the ID'

    # Check if key has been removed from both instances
    for i, kme_url in enumerate([kme_a_url, kme_b_url]):
        i = i + 1

        response = _get_request(f'{kme_url}/api/v1/internal/key_stores')

        assert len(response['activated_keys']) == 0, f'There should be 0 remaining activated keys for KME {i}'

    return 0


async def main():
    result = await test_sequence_from_kme_a_to_kme_b(
        kme_a_url=KME_1['url'],
        kme_a_sae_id=KME_1['sae_id'],
        kme_b_url=KME_2['url'],
        kme_b_sae_id=KME_2['sae_id']
    )

    if result != 0:
        print('ERR: Test sequence 1 -> 2, failed.')
        return result
    else:
        print('OK: Test sequence 1 -> 2, passed.')

    result = await test_sequence_from_kme_a_to_kme_b(
        kme_a_url=KME_2['url'],
        kme_a_sae_id=KME_2['sae_id'],
        kme_b_url=KME_1['url'],
        kme_b_sae_id=KME_1['sae_id']
    )

    if result != 0:
        print('ERR: Test sequence 2 -> 1, failed.')
        return result
    else:
        print('OK: Test sequence 2 -> 1, passed.')

    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
