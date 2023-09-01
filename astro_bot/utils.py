import datetime
import io
import logging

import aiohttp
from aiogram import Bot, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from PIL import Image

import astro_bot.handlers.apod as apod
from astro_bot.database.db_client import DbClient


def create_inline_keyboard(
    button_names: list[str], callback_data: list[str], row_width: int = 1
) -> types.InlineKeyboardMarkup:
    if len(button_names) != len(callback_data):
        raise Exception("the length of button_names is not equal to the length of callback_data")

    keyboard = types.InlineKeyboardMarkup(row_width=row_width)
    for button_name, data in zip(button_names, callback_data):
        button = types.InlineKeyboardButton(text=button_name, callback_data=data)
        keyboard.add(button)
    return keyboard


async def make_get_request(url: str, params: dict[str, str] = {}) -> dict[str, str | int]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            await raise_for_status(response)
            return await response.json()


async def get_content(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            await raise_for_status(response)
            content = await response.read()
        return content


async def raise_for_status(response: aiohttp.ClientResponse):
    if not response.ok:
        text = await response.text()
        raise Exception(f"an error occurred when accessing the NASA server: {text}")


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Вернуться к стартовому меню бота"),
        types.BotCommand(command="/help", description="Как пользоваться данным ботом"),
        types.BotCommand(
            command="/cancel_newsletter", description="Отменить ежедневное получение Астрономической картины дня"
        ),
    ]
    await bot.set_my_commands(commands)


def configure_logging_params():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s - %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def check_is_valid_date(str_date: str) -> bool:
    result = True
    try:
        date = datetime.datetime.strptime(str_date, "%Y-%m-%d")
        start_date = datetime.datetime(1995, 6, 16)
        current_date = datetime.datetime.combine(datetime.date.today(), datetime.time())
        if date < start_date or date > current_date:
            raise ValueError
    except ValueError:
        result = False
    return result


def get_info_about_astronauts(data: dict[str, str | int]) -> str:
    result = f"Всего людей в космосе по состоянию на {datetime.date.today()}: {data['number']}\n"
    for num, personal_data in enumerate(data["people"], start=1):
        result += f"{personal_data['name']}, космический корабль - {personal_data['craft']}"
        if num != len(data["people"]):
            result += "\n"
    return result


async def create_tables():
    try:
        await DbClient.create_tables()
    except Exception as er:
        logging.error(er)


async def create_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(apod.send_apod_newsletter, "cron", hour=21, minute=21, second=0, args=[bot])
    scheduler.start()


async def validate_image(image_bytes: bytes) -> bool:
    # валидными считаем изображения с относительно высоким разрешением
    image = Image.open(io.BytesIO(image_bytes))
    # return image.width + image.height >= 1400
    return image.width + image.height >= 1400
    # return image.width >= 1024 and image.height >= 1024
