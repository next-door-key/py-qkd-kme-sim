import json
import logging
from typing import Union

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from app.config import Settings

logger = logging.getLogger('uvicorn.error')


def callback(channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    logger.info('received message', channel, method, properties, body)


class Broker:
    def __init__(self, settings: Settings):
        self.connection: Union[AsyncioConnection, None] = None
        self.channel = None

        self.exchange_name = ''
        self.queue_name = settings.rabbitmq_shared_queue

        self.connection_parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
        )

    def connect(self):
        logger.info('Connecting to broker, %s:%i', self.connection_parameters.host, self.connection_parameters.port)

        self.connection = AsyncioConnection(
            parameters=self.connection_parameters,
            on_open_callback=self.on_connection_opened,
            on_close_callback=self.on_connection_closed,
            on_open_error_callback=self.on_connection_error,
        )

    def disconnect(self):
        self.connection.close()

    def on_connection_opened(self, connection: AsyncioConnection):
        logger.info('Broker connection opened')
        self.connection = connection

        logger.debug('Creating a broker channel')
        self.connection.channel(on_open_callback=self.on_channel_opened)

    def on_connection_closed(self, connection: AsyncioConnection, reason: BaseException):
        logger.warning('Broker connection closed: %s', reason)

        self.channel = None

    def on_connection_error(self, connection: AsyncioConnection, error: BaseException):
        logger.error('Failed to open broker connection: %s', error)

    def on_channel_opened(self, _):
        logger.info('Broker channel opened')

        self.channel.add_on_close_callback(self.on_channel_closed)
        self.setup_queue()

    def on_channel_closed(self, channel, reason):
        logger.warning('Broker channel %i was closed: %s', channel, reason)

        self.channel = None
        self.connection.close()

    def setup_queue(self):
        logger.debug('Declaring broker queue: %s', self.queue_name)

        self.channel.queue_declare(queue=self.queue_name, callback=self.on_queue_declare)

    def on_queue_declare(self, _):
        self.channel.queue_bind(
            self.queue_name,
            self.exchange_name,
            routing_key=self.queue_name,
            callback=self.on_queue_bind
        )

    def on_queue_bind(self, _):
        logger.debug('Broker queue bound')

        self.start_queue_publishing()

    def start_queue_publishing(self):
        self.channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()

        logger.info('Received %s for delivery tag: %i', confirmation_type, method_frame.method.delivery_tag)

    def publish_message(self, message):
        if self.channel is None or not self.channel.is_open:
            return

        headers = {'a': 'b'}
        properties = pika.BasicProperties(
            app_id='example-publisher',
            content_type='application/json',
            headers=headers)

        self.channel.basic_publish(self.exchange_name, self.queue_name,
                                   json.dumps(message, ensure_ascii=False),
                                   properties)
        logger.info('Published message # %i', 1)
