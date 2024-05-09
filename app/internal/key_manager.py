import asyncio
import json
import logging

from aiormq.abc import DeliveredMessage

from app.config import Settings
from app.enums.initiated_by import InitiatedBy
from app.internal import key_generator, key_requester
from app.internal.broker import Broker
from app.models.key_container import FullKeyContainer, ActivatedKeyContainer

logger = logging.getLogger('uvicorn.error')


class KeyManager:
    def __init__(self, settings: Settings, broker: Broker):
        self._is_master = settings.is_master
        self._broker = broker

        self._key_size = settings.default_key_size
        self._key_generate_timeout_in_seconds = settings.key_generation_timeout_in_seconds
        self._max_key_count = settings.max_key_count

        self._keys: list[FullKeyContainer] = []
        self._activated_keys: list[ActivatedKeyContainer] = []

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

    async def _broadcast_activated_key(self, key: ActivatedKeyContainer):
        await self._broker.send_message({
            'type': 'activated_key',
            'data': key.json()
        })

    async def _broadcast_deactivated_key(self, key: ActivatedKeyContainer):
        await self._broker.send_message({
            'type': 'deactivated_key',
            'data': key.json()
        })

    async def _listen_to_new_keys(self, message: DeliveredMessage):
        json_message = json.loads(message.body.decode())

        data = json_message['data']

        if json_message['type'] == 'new_key':
            self._keys.append(data)
        elif json_message['type'] == 'remove_key':
            self._keys.remove(data)
        elif json_message['type'] == 'activate_key':
            self._activated_keys.append(data)
        elif json_message['type'] == 'deactivate_key':
            self._activated_keys.remove(data)

    def get_key_count(self):
        return len(self._keys)

    def _get_single_key(self) -> FullKeyContainer:
        return self._keys.pop()

    def _activate_key(self, key: FullKeyContainer, master_sae_id: str, slave_sae_id: str) -> ActivatedKeyContainer:
        activated_key = ActivatedKeyContainer(
            key_container=key,
            master_sae_id=master_sae_id,
            slave_sae_id=slave_sae_id
        )

        self._activated_keys.append(activated_key)

        return activated_key

    async def get_key(self, master_sae_id: str, slave_sae_id: str, initiated_by: InitiatedBy) -> ActivatedKeyContainer:
        activated_key: ActivatedKeyContainer

        if initiated_by.MASTER:
            activated_key = self._activate_key(self._get_single_key(), master_sae_id, slave_sae_id)

            await self._broadcast_activated_key(activated_key)
        else:
            activated_key = key_requester.ask_for_key(master_sae_id, slave_sae_id)

            self._activated_keys.append(activated_key)

        return activated_key

    async def deactivate_key(self, activated_key: ActivatedKeyContainer, initiated_by: InitiatedBy):
        if initiated_by.MASTER:
            self._activated_keys.remove(activated_key)

            await self._broadcast_deactivated_key(activated_key)
        else:
            activated_key = key_requester.ask_to_deactivate_key(activated_key)

            self._activated_keys.remove(activated_key)
