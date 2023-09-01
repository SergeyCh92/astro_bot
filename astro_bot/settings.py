from pydantic import BaseSettings, Field, SecretStr


class BotSettings(BaseSettings):
    telegram_token: SecretStr = Field(env="TELEGRAM_TOKEN")
    nasa_token: SecretStr = Field(env="NASA_TOKEN")
    connection_string: SecretStr = Field(env="CONNECTION_STRING")
    apod_url: str = Field(env="APOD_URL", default="https://api.nasa.gov/planetary/apod")
    rovers_url: str = Field(
        env="MARS_ROVERS_URL", default="https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/photos"
    )
