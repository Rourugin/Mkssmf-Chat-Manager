import os
import secrets
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram import BaseMiddleware
from typing import Any, Callable, Dict, Awaitable

import app.database.requests as rq


class NewUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
            ):

        status = 0
        load_dotenv()
        if event.from_user.id == int(os.getenv('ADMIN_ID')):
            status = 100
        else:
            status = 1
        await rq.set_user(event.from_user.id, status)

        user = await rq.get_user(event.from_user.id)
        if user.status == 0:
            rand_event = secrets.randbelow(4)
            match rand_event:
                case 0:
                    await event.react([ReactionTypeEmoji(emoji="🤡")], is_big=True)
                case 1:
                    await event.reply("🤡")
                case 2:
                    await event.reply("позорник ебучий")
                case 3:
                    await event.reply("твоё мнение не учитывается бтв")

        return await handler(event, data)