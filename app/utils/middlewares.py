import os
import secrets
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram import BaseMiddleware
from typing import Any, Callable, Dict, Awaitable

import app.database.requests as rq


load_dotenv()

class NewUserMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:

        status = 0
        if event.from_user.id == int(os.getenv('ADMIN_ID')):
            status = 100
        else:
            status = 1
        await rq.set_user(event.from_user.id, status)

        return await handler(event, data)


class StatusMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) ->  Any:
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


class CommentMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
        if not event.reply_to_message:
            return await handler(event, data)
        
        if await rq.is_post_exist(event.reply_to_message.forward_from_message_id) or await rq.is_post_exist(event.reply_to_message.message_id):
            user = await rq.get_user(event.from_user.id)
            user.bananas += 10
            async with rq.async_session() as session:
                await session.merge(user)
                await session.commit()

        return await handler(event, data)