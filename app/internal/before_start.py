from fastapi import FastAPI

from app.config import Settings
from app.internal.broker.rabbitmq import RabbitMQ


def before_start(app: FastAPI, settings: Settings):
    RabbitMQ(settings).connect()
