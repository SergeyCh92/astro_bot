from astro_bot.settings import BotSettings

from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    BotSettings().connection_string.get_secret_value(),
    pool_pre_ping=True,
    echo=False,
    enable_from_linting=False,
)
