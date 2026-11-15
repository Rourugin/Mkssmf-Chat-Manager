import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession

from app.database.models import async_main
from app.handlers.__init__ import setup_routers
from app.utils.middlewares import NewUserMiddleware
from app.commands.commands_menu import set_commands
from app.utils.sync_posts import sync_all_channels


async def main() -> None:
    await async_main()
    #Подключение бота и диспетчера по токену из .env
    load_dotenv()
    session = AiohttpSession(api=TelegramAPIServer.from_base(base=os.getenv('CLOUDFLARE_WORKER_URL')), timeout=30)
    bot = Bot(token=os.getenv('TOKEN'), session=session)
    dp = Dispatcher()
    channel_ids_str = os.getenv('CHANNEL_IDS', '')
    channel_ids = [int(x.strip()) for x in channel_ids_str.split(',') if x.strip()]
    admin_id = int(os.getenv('ADMIN_ID'))
    print("bot is working")

    sync_task = asyncio.create_task(sync_all_channels(bot=bot, channel_ids=channel_ids, admin_id=admin_id))
    sync_task.add_done_callback(lambda t: logging.error("Ошибка в sync_task:", exc_info=t.exception()) if not t.cancelled() and t.exception() else None)
    dp.message.outer_middleware(NewUserMiddleware())

    #Подключение роутеров к диспетчеру и вывод базовых команд
    dp.include_routers(setup_routers())
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot=bot)
    try:
        await dp.start_polling(bot, polling_timeout=10)
    finally:
        sync_task.cancel()
        try:
            await sync_task
        except asyncio.CancelledError:
            pass
        await bot.session.close()
        print("bot was disabled")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass