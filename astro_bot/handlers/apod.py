import logging

from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from deep_translator import GoogleTranslator
from sqlalchemy.ext.asyncio import AsyncSession

from astro_bot.database.db_client import DbClient
from astro_bot.injections.database_session import inject_db_session
from astro_bot.settings import BotSettings
from astro_bot.texts import TextStorage
from astro_bot.utils import check_is_valid_date, create_inline_keyboard, get_content, make_get_request

settings = BotSettings()


class OrderApod(StatesGroup):
    WAITING_FOR_DATE = State()


async def request_apod_date(callback: types.CallbackQuery, state: FSMContext):
    keyboard = create_inline_keyboard(["Получить сегодняшнее изображение"], ["get_apod"])
    await callback.message.answer(TextStorage.APOD_DESCRIPTION, reply_markup=keyboard)
    await state.set_state(OrderApod.WAITING_FOR_DATE.state)
    await callback.answer()


async def get_apod_for_today_date(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession = inject_db_session()
):
    try:
        user_receives_apod = await DbClient.check_user_receives_apod(callback.from_user.id, session)
        if not user_receives_apod:
            caption_keyboard = create_inline_keyboard(
                ["Ежедневно получать новые изображения дня", "Перевести текст"],
                ["receive_apod_daily", "translate_caption_text"],
            )
        else:
            caption_keyboard = create_inline_keyboard(["Перевести текст"], ["translate_caption_text"])
        params = {"api_key": settings.nasa_token.get_secret_value()}
        text_keyboard = create_inline_keyboard(["Перевести текст"], ["translate_message_text"])

        data = await make_get_request("https://api.nasa.gov/planetary/apod", params)
        url_button = types.InlineKeyboardButton("Изображение в максимальном качестве", data["hdurl"])
        caption_keyboard.add(url_button)
        await callback.message.answer_photo(photo=data["url"], caption=data["title"], reply_markup=caption_keyboard)
        await callback.message.answer(text=data["explanation"], reply_markup=text_keyboard)
        logging.info("photo sent!")
        await callback.message.delete()
        await callback.answer()
    finally:
        await state.finish()
        await session.close()


async def add_user_to_newsletter(callback: types.CallbackQuery, session: AsyncSession = inject_db_session()):
    try:
        await DbClient.add_user_to_newsletter(callback.from_user.id, session)
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for button in callback.values["message"].reply_markup.inline_keyboard[1:]:
            keyboard.add(button[0])
        await callback.message.edit_reply_markup(keyboard)
        await callback.answer(TextStorage.ADDITION_TO_MAILING_LIST, show_alert=True)
    finally:
        await session.close()


async def get_apod_for_selected_date(
    message: types.Message, state: FSMContext, session: AsyncSession = inject_db_session()
):
    date_is_valid = check_is_valid_date(message.text)
    if not date_is_valid:
        await message.reply(TextStorage.IS_NOT_VALID_DATE)
        return
    try:
        user_receives_apod = await DbClient.check_user_receives_apod(message.from_user.id, session)
        if not user_receives_apod:
            caption_keyboard = create_inline_keyboard(
                ["Ежедневно получать новые изображения дня", "Перевести текст"],
                ["receive_apod_daily", "translate_caption_text"],
            )
        else:
            caption_keyboard = create_inline_keyboard(["Перевести текст"], ["translate_caption_text"])
        params = {"api_key": settings.nasa_token.get_secret_value(), "date": message.text}
        text_keyboard = create_inline_keyboard(["Перевести текст"], ["translate_message_text"])

        data = await make_get_request("https://api.nasa.gov/planetary/apod", params)
        if data["media_type"] != "image":
            await message.answer(
                "К сожалению за выбранную дату изображение отсутствует. Попробуйте выбрать другую дату."
            )
        else:
            url_button = types.InlineKeyboardButton("Изображение в максимальном качестве", data["hdurl"])
            caption_keyboard.add(url_button)
            await message.answer_photo(photo=data["url"], caption=data["title"], reply_markup=caption_keyboard)
            await message.answer(text=data["explanation"], reply_markup=text_keyboard)
            await message.delete()
            logging.info("photo sent!")
    finally:
        await state.finish()


async def translate_caption(callback: types.CallbackQuery, translator=GoogleTranslator(source="en", target="ru")):
    translated_text = translator.translate(callback.message.caption, src="en", dest="ru")
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    url_button = types.InlineKeyboardButton(
        "Изображение в максимальном качестве", callback.values["message"].reply_markup.inline_keyboard[-1][0].url
    )
    keyboard.add(url_button)
    if len(callback.values["message"].reply_markup.inline_keyboard) == 3:
        subscribe_button = types.InlineKeyboardButton(
            "Ежедневно получать новые изображения дня",
            callback_data=callback.values["message"].reply_markup.inline_keyboard[1][0].callback_data,
        )
        keyboard.add(subscribe_button)
    await callback.message.edit_caption(translated_text)
    await callback.message.edit_reply_markup(keyboard)
    await callback.answer()


async def translate_text(callback: types.CallbackQuery, translator=GoogleTranslator(source="en", target="ru")):
    translated_text = translator.translate(callback.message.text, src="en", dest="ru")
    await callback.message.edit_text(translated_text)
    await callback.answer()


async def send_apod_newsletter(bot: Bot, session: AsyncSession = inject_db_session()):
    try:
        user_ids = await DbClient.get_user_list_for_apod(session)
        if not user_ids:
            return
        caption_keyboard = create_inline_keyboard(["Перевести текст"], ["translate_caption_text"])
        params = {"api_key": settings.nasa_token.get_secret_value()}
        text_keyboard = create_inline_keyboard(["Перевести текст"], ["translate_message_text"])

        data = await make_get_request("https://api.nasa.gov/planetary/apod", params)
        url_button = types.InlineKeyboardButton("Изображение в максимальном качестве", data["hdurl"])
        caption_keyboard.add(url_button)
        for user_id in user_ids:
            await bot.send_photo(user_id, photo=data["url"], caption=data["title"], reply_markup=caption_keyboard)
            await bot.send_message(user_id, text=data["explanation"], reply_markup=text_keyboard)
    finally:
        await session.close()
