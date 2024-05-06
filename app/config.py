from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kme_id: str
    attached_sae_id: str
    linked_to_kme: str
