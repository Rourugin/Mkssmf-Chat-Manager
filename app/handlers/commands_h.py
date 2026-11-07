import os
import logging
from typing import Any
from aiogram import Router, F
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest


import app.database.requests as rq


commands_r = Router()
commands_r.message.filter(F.chat.type == 'supergroup')


@commands_r.message(Command(commands=['random_post']))
async def cmd_random_post(message: Message) -> Any:
    post = await rq.get_random_post()
    if post is None:
        return None
    load_dotenv()
    channel_id = int(os.getenv('CHANNEL_ID'))

    try:
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=channel_id,
            message_id=post.post_id
        )
    except TelegramBadRequest as e:
        logging.error(f"Не удалось отправить пост #{post.post_id}: {e}")
        await message.answer("Этот пост был удалён или недоступен, попробуйте ещё раз.")