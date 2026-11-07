from typing import Any
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart


#Создаём роутер и заставляем обрабатывать его сообщения в групповых чатах
main_r = Router()
main_r.message.filter(F.chat.type == 'supergroup')


@main_r.message(CommandStart())
async def cmd_start(message: Message) -> Any:
    await message.reply("Ебать ты клоун, конечно, но молодец, что воспользовался командой")