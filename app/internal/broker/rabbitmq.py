import logging

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from app.config import Settings

logger = logging.getLogger('uvicorn.error')


def callback(channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    logger.info('received message', channel, method, properties, body)


class RabbitMQ:
    connection: pika.BlockingConnection = None
    channel: BlockingChannel = None

    def __init__(self, settings: Settings):
        self.queue_name = settings.rabbitmq_shared_queue

        self.connection_parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
        )

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(self.queue_name)

        self.channel.basic_consume(
            queue=self.queue_name,
            auto_ack=True,
            on_message_callback=callback
        )

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body='Hello, World!'
        )

        logger.info('Published')

        # TODO: This doesn't work as it is blocking, we need async behaviour,
        #  but something that doesn't explode into many threads
        #  self.channel.start_consuming()

    def disconnect(self):
        self.connection.close()
