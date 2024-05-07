import json
import logging
from typing import Union, Callable

import aiormq
from aiormq.abc import AbstractConnection, AbstractChannel, DeliveredMessage

from app.config import Settings

logger = logging.getLogger('uvicorn.error')


class Broker:
    def __init__(self, settings: Settings):
        self._connection: Union[AbstractConnection, None] = None
        self._channel: Union[AbstractChannel, None] = None
        self._url = 'amqp://{}:{}@{}:{}/'.format(
            settings.mq_username,
            settings.mq_password,
            settings.mq_host,
            settings.mq_port
        )

        self._queue_name = settings.mq_shared_queue
        self._is_master = settings.is_master

        self.callbacks = []

    async def connect(self):
        logger.info('Connecting to broker...')

        self._connection = await aiormq.connect(self._url)
        self._channel = await self._connection.channel()

        logger.info('Connected to broker. Declaring queue...')

        await self._channel.queue_declare(self._queue_name)

        if not self._is_master:
            logger.info('Creating the broker listener because this instance is the master')
            await self._setup_listener()

    async def disconnect(self):
        logger.info('Closing broker connection')

        await self._connection.close()
        self._channel = None

    async def _setup_listener(self):
        await self._channel.basic_consume(
            queue=self._queue_name,
            consumer_callback=self._receive_message
        )

    async def _receive_message(self, message: DeliveredMessage):
        logger.info('Received new message from broker: %s', message.body)

        try:
            for callback in self.callbacks:
                await callback(message)

            await self._channel.basic_ack(message.delivery_tag)
        except Exception as e:
            await self._channel.basic_nack(message.delivery_tag)
            logging.exception(e)

    def register_callback(self, cb: Callable):
        self.callbacks.append(cb)

    async def send_message(self, routing_key: str, message: dict) -> None:
        if self._channel is None or self._channel.is_closed:
            logger.warning('Cannot send message because broker channel is closed')
            return

        await self._channel.basic_publish(routing_key=routing_key,
                                          body=json.dumps(message).encode())
