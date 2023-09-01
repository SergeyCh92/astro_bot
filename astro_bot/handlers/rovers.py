import random

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from astro_bot.database.db_client import DbClient
from astro_bot.injections.database_session import inject_db_session
from astro_bot.models.rovers import Rover
from astro_bot.settings import BotSettings
from astro_bot.texts import TextStorage
from astro_bot.utils import create_inline_keyboard, get_content, make_get_request, validate_image

settings = BotSettings()


class OrderMarsPhoto(StatesGroup):
    WAITING_FOR_PHOTO = State()


async def choose_mars_rover(callback: types.CallbackQuery, state: FSMContext):
    keyboard = create_inline_keyboard(["Perseverance"], ["Perseverance"])
    await callback.message.answer(TextStorage.CHOOSER_ROVER, reply_markup=keyboard)
    await state.set_state(OrderMarsPhoto.WAITING_FOR_PHOTO.state)
    await callback.message.delete()
    await callback.answer()


async def get_rover_photo(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession = inject_db_session()
):
    try:
        row_rover_data = await DbClient.get_rover_data(callback.data, session)
        rover = Rover.from_orm(row_rover_data)
        empty_sols: set[int] = set()
        params = {"api_key": settings.nasa_token.get_secret_value()}
        actual_rovers_url = settings.rovers_url.replace("perseverance", callback.data)
        finish = False
        while True:
            if finish:
                break
            attempts_number = 0
            while True:
                sol = random.randint(0, rover.data.max_sol)
                if sol not in rover.data.empty_sols or attempts_number > 300:
                    break
                attempts_number += 1
            params["sol"] = sol
            # очень часто возвращается ответ, в котором отсутствуют какие-либо фотографии за выбранный сол
            # необходимо для каждого ровера писать данные о солах, за которые нет фотографий,
            # в базу и не запрашивать фото за эти солы
            response_data = await make_get_request(actual_rovers_url, params)
            if response_data["photos"] == []:
                empty_sols.add(sol)
            if not response_data.get("photos"):
                continue
            for photo_data in response_data["photos"]:
                image_url = photo_data["img_src"]
                image_data = await get_content(image_url)
                if await validate_image(image_data):
                    finish = True
                    break
        rover.data.empty_sols.extend(empty_sols)
        await DbClient.record_rover_data(rover, session)
        await callback.message.answer_photo(image_url)
        await callback.message.delete()
        await callback.answer()
    finally:
        await session.close()
