import base64
import os
import uuid
from datetime import datetime, timedelta


def generate(size: int, default_ttl_in_minutes: int = 15) -> dict:
    return {
        'key_container': {
            'key_ID': str(uuid.uuid4()),
            'key': base64.b64encode(
                os.urandom(size)
            ).decode('ascii')
        },
        'ttl': (datetime.now() + timedelta(minutes=default_ttl_in_minutes)).isoformat()
    }
