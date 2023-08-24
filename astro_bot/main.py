import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from astro_bot.registers import register_handlers_apod
from astro_bot.settings import BotSettings
from astro_bot.utils import configure_logging_params, create_scheduler, create_tables, set_commands


async def main():
    configure_logging_params()
    await create_tables()
    settings = BotSettings()
    bot = Bot(token=settings.telegram_token.get_secret_value())
    await set_commands(bot)

    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers_apod(dp)
    logging.info("bot started")
    return dp


async def on_startup(dp: Dispatcher):
    asyncio.create_task(create_scheduler(dp.bot))


if __name__ == "__main__":
    dp = asyncio.run(main())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, timeout=30, on_startup=on_startup)
