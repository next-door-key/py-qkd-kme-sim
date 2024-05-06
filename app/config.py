from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kme_id: str
    attached_sae_id: str

    linked_to_kme: str
    linked_kme_id: str

    rabbitmq_host: str = 'localhost'
    rabbitmq_port: int = 5672
    rabbitmq_shared_queue: str
