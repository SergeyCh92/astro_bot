from pydantic import BaseSettings, Field, SecretStr


class BotSettings(BaseSettings):
    telegram_token: SecretStr = Field(env="TELEGRAM_TOKEN")
    nasa_token: SecretStr = Field(env="NASA_TOKEN")
    connection_string: SecretStr = Field(env="CONNECTION_STRING")
