from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    is_master: bool = False

    kme_id: str
    attached_sae_id: str

    linked_to_kme: str
    linked_kme_id: str

    mq_host: str = 'localhost'
    mq_port: int = 5672
    mq_username: str = 'guest'
    mq_password: str = 'guest'
    mq_shared_queue: str
