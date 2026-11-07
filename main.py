import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession

from app.database.models import async_main
from app.handlers.__init__ import setup_routers
from app.commands.commands_menu import set_commands
from app.utils.sync_posts import sync_channel_posts


async def main() -> None:
    await async_main()
    #Подключение бота и диспетчера по токену из .env
    load_dotenv()
    session = AiohttpSession(api=TelegramAPIServer.from_base(base=os.getenv('CLOUDFLARE_WORKER_URL')), timeout=15)
    bot = Bot(token=os.getenv('TOKEN'), session=session)
    dp = Dispatcher()
    channel_id = int(os.getenv('CHANNEL_ID'))
    admin_id = int(os.getenv('ADMIN_ID'))
    print("bot is working")

    sync_task = asyncio.create_task(sync_channel_posts(bot=bot, channel_id=channel_id, admin_id=admin_id))

    #Подключение роутеров к диспетчеру и вывод базовых команд
    dp.include_routers(setup_routers())
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot=bot)
    try:
        await dp.start_polling(bot, polling_timeout=10)
    finally:
        sync_task.cancel()
        await bot.session.close()
        print("bot was disabled")


if __name__ == '__main__':
    asyncio.run(main())