import os
from typing import Any
from aiogram import Router, F
from dotenv import load_dotenv
from aiogram.types import Message, ReactionTypeEmoji

import app.database.requests as rq


load_dotenv()
channel_ids_str = os.getenv('CHANNEL_IDS', '')
CHANNEL_IDS = [int(x.strip()) for x in channel_ids_str.split(',') if x.strip()]
background_r = Router()
background_r.message.filter(F.chat.type == 'supergroup')


@background_r.channel_post(F.chat.id.in_(CHANNEL_IDS))
async def new_post(message: Message) -> Any:
    await rq.set_post(
        channel_id=message.chat.id,
        post_id=message.message_id,
        media_group_id=message.media_group_id
    )

@background_r.message(F.text.lower().contains("🤡") | F.text.lower().contains("клоун"))
async def clown(message: Message) -> Any:
    await message.react([ReactionTypeEmoji(emoji="🤡")], is_big=True)