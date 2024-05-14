import asyncio
import ssl
from typing import Union

import urllib3
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

    def _verify_settings(self):
        if self.settings.min_key_size > self.settings.max_key_size:
            raise ValueError('Please define a correct range of min, max key sizes')

        if self.settings.min_key_size % 8 != 0:
            raise ValueError('Min key size must be a multiple of 8')

        if self.settings.default_key_size % 8 != 0:
            raise ValueError('Default key size must be a multiple of 8')

        if self.settings.max_key_size % 8 != 0:
            raise ValueError('Max key size must be a multiple of 8')

        if self.settings.default_key_size < self.settings.min_key_size or self.settings.default_key_size > self.settings.max_key_size:
            raise ValueError('Default key size must be in the range of min/max key sizes')

        if (
                self.settings.min_key_size <= 0 or
                self.settings.max_key_size <= 0 or
                self.settings.default_key_size <= 0 or
                self.settings.max_key_count <= 0 or
                self.settings.max_keys_per_request <= 0 or
                self.settings.key_generation_timeout_in_seconds <= 0
        ):
            raise ValueError('All numeric config values must be above 0')

    def _configure_tls(self):
        urllib3.disable_warnings()

        context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=self.settings.ca_file)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(certfile=self.settings.kme_cert, keyfile=self.settings.kme_key)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False

    async def before_start(self):
        self._verify_settings()
        self._configure_tls()

        self.broker = Broker(self.settings)
        await self.broker.connect()

        self.key_manager = KeyManager(self.settings, self.broker)

        # Do not await, otherwise it freezes the main thread
        # noinspection PyAsyncCall
        asyncio.create_task(self.key_manager.start_generating())

    async def after_landing(self):
        await self.broker.disconnect()
