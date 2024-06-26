import base64
import os
import uuid

from app.models.key_container import FullKeyContainer, KeyPartsContainer


def _generate_key_part(size_bytes: int) -> str:
    return base64.b64encode(os.urandom(size_bytes)).decode('ascii')


def generate(min_size: int, max_size: int) -> FullKeyContainer:
    key_parts = []

    for i in range(8, max_size + 8, 8):
        key_parts.append(_generate_key_part(size_bytes=1))

    return FullKeyContainer(
        key_container=KeyPartsContainer(
            key_ID=str(uuid.uuid4()),
            key_parts=key_parts,
        )
    )
