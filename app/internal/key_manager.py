import json

from aiormq.abc import DeliveredMessage

from app.config import Settings
from app.internal import key_generator
from app.internal.broker import Broker


class KeyManager:
    def __init__(self, settings: Settings, broker: Broker):
        self._is_master = settings.is_master
        self._broker = broker
        # TODO: Take from config and validate if is a multiple of 8 and is above minimum and below maximum key length
        self._key_size = 128
        self._keys: list[dict] = []

    async def start_generating(self):
        if not self._is_master:
            self._broker.register_callback(self._listen_to_new_keys)
            return

        # TODO: This causes an unbreakable infinite loop, only killable with SIGKILL.
        #   Need to verify how aio-pika works with the asyncio event loop, to prevent blocking of all threads
        await self._generate_key()
        # await asyncio.sleep(10)
        # await self.start_generating()

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
