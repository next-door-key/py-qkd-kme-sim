from fastapi import FastAPI

from app.config import Settings


def after_landing(app: FastAPI, settings: Settings):
    pass
