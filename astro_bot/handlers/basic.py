from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from astro_bot.database.db_client import DbClient
from astro_bot.injections.database_session import inject_db_session
from astro_bot.texts import TextStorage
from astro_bot.utils import create_inline_keyboard


async def start(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = create_inline_keyboard(
        ["Астрономическое изображение дня 🌌", "Инфорация о людях в космосе 👩‍🚀"],
        ["get_apod_date", "get_astronauts_info"],
    )
    await message.answer(text="Выберите интересующую вас опцию из списка ниже.", reply_markup=keyboard)


async def send_description(message: types.Message, state: FSMContext):
    await message.answer(TextStorage.DESCRIPTION)


async def cancel_newsletter(message: types.Message, state: FSMContext, session: AsyncSession = inject_db_session()):
    try:
        await DbClient.remove_user_from_newsletter(message.from_user.id, session)
        await message.answer(TextStorage.REMOVE_TO_MAILING_LIST)
    finally:
        session.close()
