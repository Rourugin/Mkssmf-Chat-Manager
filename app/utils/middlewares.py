import os
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
            status = 0
        else:
            status = 1
        await rq.set_user(event.from_user.id, status)

        return await handler(event, data)