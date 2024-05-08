import asyncio
import json
import logging

from aiormq.abc import DeliveredMessage

from app.config import Settings
from app.internal import key_generator
from app.internal.broker import Broker
from app.routers.key_container import FullKeyContainer

logger = logging.getLogger('uvicorn.error')


class KeyManager:
    def __init__(self, settings: Settings, broker: Broker):
        self._is_master = settings.is_master
        self._broker = broker

        self._key_size = settings.default_key_size
        self._key_generate_timeout_in_seconds = settings.key_generation_timeout_in_seconds
        self._max_key_count = settings.max_key_count

        self._keys: list[FullKeyContainer] = []

    async def start_generating(self):
        if not self._is_master:
            self._broker.register_callback(self._listen_to_new_keys)
            return

        has_consumers = False
        is_key_pool_full = False

        while True:
            if self.get_key_count() >= self._max_key_count:
                await asyncio.sleep(self._key_generate_timeout_in_seconds)

                if not is_key_pool_full:
                    logger.warning(
                        f'Key pool is full, not generating any more keys ({self.get_key_count()}/{self._max_key_count}).')

                    is_key_pool_full = True

                continue
            elif is_key_pool_full:
                is_key_pool_full = False

            if not await self._broker.has_consumers():
                logger.warning('Waiting 10 seconds for 2nd KME to come online...')
                await asyncio.sleep(10)

                continue

            if not has_consumers:
                logger.info('Found the 2nd KME, starting key generation.')
                has_consumers = True

            await asyncio.sleep(self._key_generate_timeout_in_seconds)
            await self._generate_key()

    async def _generate_key(self):
        key = key_generator.generate(self._key_size)

        self._keys.append(key)
        await self._broadcast_key(key)

    async def _broadcast_key(self, key: FullKeyContainer):
        await self._broker.send_message({
            'type': 'new_key',
            'data': key.json()
        })

    async def _broadcast_key_removal(self, key: FullKeyContainer):
        await self._broker.send_message({
            'type': 'remove_key',
            'data': key.json()
        })

    async def _listen_to_new_keys(self, message: DeliveredMessage):
        json_message = json.loads(message.body.decode())

        if json_message['type'] == 'new_key':
            self._keys.append(json_message['data'])

    def get_key_count(self):
        return len(self._keys)

    async def get_key(self, master_sae_id: str, slave_sae_id: str):
        # If master needs a key:
        #   1) take a key from the key pool
        #   2) put the key into the activated keys
        #   3) send message to activate key (key id, master, slave sae ids)
        #   4) return the key container
        # If a slave needs a key:
        #   1) ask master to give a key (send request id, master_sae_id, slave_sae_id)
        #       a) how can a slave ask the master? it is impossible, only way HTTP request, but that is slow and bad (maybe race conditions?)
        pass
