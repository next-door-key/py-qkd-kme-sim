import asyncio
from typing import Union

from fastapi import FastAPI

from app.config import Settings
from app.internal.broker import Broker
from app.internal.key_manager import KeyManager


class Lifecycle:
    broker: Union[Broker, None] = None
    key_manager: Union[KeyManager, None] = None

    def __init__(self, app: FastAPI, settings: Settings):
        self.app = app
        self.settings = settings

    async def before_start(self):
        self.broker = Broker(self.settings)
        await self.broker.connect()

        self.key_manager = KeyManager(self.settings, self.broker)

        # Do not await, otherwise it freezes the main thread
        # noinspection PyAsyncCall
        asyncio.create_task(self.key_manager.start_generating())

    async def after_landing(self):
        await self.broker.disconnect()
