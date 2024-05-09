import base64
import os
import uuid

from app.models.key_container import FullKeyContainer, KeyContainer


def generate(size: int) -> FullKeyContainer:
    return FullKeyContainer(
        key_container=KeyContainer(
            key_ID=str(uuid.uuid4()),
            key=base64.b64encode(
                os.urandom(size)
            ).decode('ascii')
        )
    )
