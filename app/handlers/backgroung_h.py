import os
from typing import Any
from aiogram import Router, F
from dotenv import load_dotenv
from aiogram.types import Message, ReactionTypeEmoji

import app.database.requests as rq


load_dotenv()
channel_id = int(os.getenv('CHANNEL_ID'))
background_r = Router()
background_r.message.filter(F.chat.type == 'supergroup')


@background_r.channel_post(F.chat.id == channel_id)
async def new_post(message: Message) -> Any:
    await rq.set_post(
        post_id=message.message_id,
        media_group_id=message.media_group_id
    )

@background_r.message(F.text.lower().contains("🤡") | F.text.lower().contains("клоун"))
async def clown(message: Message) -> Any:
    await message.react([ReactionTypeEmoji(emoji="🤡")], is_big=True)