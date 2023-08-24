from aiogram import Dispatcher

from astro_bot.handlers.apod import (
    OrderApod,
    add_user_to_newsletter,
    get_apod_for_selected_date,
    get_apod_for_today_date,
    request_apod_date,
    translate_caption,
    translate_text,
)
from astro_bot.handlers.astronauts import get_astronaut_names_in_space
from astro_bot.handlers.basic import send_description, start, cancel_newsletter


def register_handlers_apod(dp: Dispatcher):
    dp.register_message_handler(start, commands="start", state="*")
    dp.register_message_handler(send_description, commands="help", state="*")
    dp.register_message_handler(cancel_newsletter, commands="cancel_newsletter", state="*")
    dp.register_callback_query_handler(request_apod_date, text="get_apod_date", state="*")
    dp.register_callback_query_handler(translate_caption, text="translate_caption_text", state="*")
    dp.register_callback_query_handler(translate_text, text="translate_message_text", state="*")
    dp.register_callback_query_handler(get_apod_for_today_date, text="get_apod", state=OrderApod.WAITING_FOR_DATE)
    dp.register_message_handler(get_apod_for_selected_date, state=OrderApod.WAITING_FOR_DATE)
    dp.register_callback_query_handler(get_astronaut_names_in_space, text="get_astronauts_info")
    dp.register_callback_query_handler(add_user_to_newsletter, text="receive_apod_daily")
