import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession

from app.handlers.__init__ import setup_routers


async def main() -> None:
    #Подключение бота и диспетчера по токену из .env
    load_dotenv()
    session = AiohttpSession(api=TelegramAPIServer.from_base(base=os.getenv('CLOUDFLARE_WORKER_URL')))
    bot = Bot(token=os.getenv('TOKEN'), session=session)
    dp = Dispatcher()
    print("bot is working")

    #Подключение роутеров к диспетчеру и вывод базовых команд
    dp.include_routers(setup_routers())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot was disabled")