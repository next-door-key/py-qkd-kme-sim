from fastapi import FastAPI

from app.config import Settings
from app.internal.broker import Broker


class Lifecycle:
    broker: Broker = None

    def __init__(self, app: FastAPI, settings: Settings):
        self.app = app
        self.settings = settings

    def before_start(self):
        self.broker = Broker(self.settings)
        self.broker.connect()

    def after_landing(self):
        self.broker.disconnect()
