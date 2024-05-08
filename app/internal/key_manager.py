import asyncio
import json
import logging

from aiormq.abc import DeliveredMessage

from app.config import Settings
from app.internal import key_generator
from app.internal.broker import Broker

logger = logging.getLogger('uvicorn.error')


class KeyManager:
    def __init__(self, settings: Settings, broker: Broker):
        self._is_master = settings.is_master
        self._broker = broker
        self._key_size = settings.default_key_size
        self._key_generate_timeout_in_seconds = settings.key_generation_timeout_in_seconds

        self._keys: list[dict] = []

    async def start_generating(self):
        if not self._is_master:
            self._broker.register_callback(self._listen_to_new_keys)
            return

        has_consumers = False

        while True:
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

    async def _broadcast_key(self, key: dict):
        await self._broker.send_message({
            'type': 'new_key',
            'data': key
        })

    async def _listen_to_new_keys(self, message: DeliveredMessage):
        json_message = json.loads(message.body.decode())

        if json_message['type'] == 'new_key':
            self._keys.append(json_message['data'])
