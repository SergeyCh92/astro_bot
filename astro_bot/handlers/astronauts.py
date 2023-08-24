from aiogram import types

from astro_bot.texts import TextStorage
from astro_bot.utils import make_get_request, get_info_about_astronauts


async def get_astronaut_names_in_space(callback: types.CallbackQuery):
    try:
        data = await make_get_request("http://api.open-notify.org/astros.json")
        if data["message"] != "success":
            callback.message.answer(TextStorage.ERROR_PEOPLE_SPACE)
        else:
            astronauts_info = get_info_about_astronauts(data)
            await callback.message.answer(astronauts_info)
    finally:
        await callback.answer()
