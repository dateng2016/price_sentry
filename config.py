from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import time
import requests
from typing import Optional


class Settings(BaseSettings):

    # DB
    db_host: str
    db_user: str
    db_passwd: str
    db_name: str
    # jwt secret
    secret: str
    # email
    email_from: str
    app_password: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    # print("#########settings", Settings())
    return Settings()


if __name__ == "__main__":
    print("#########settings", get_settings())
