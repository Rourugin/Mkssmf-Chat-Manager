from aiogram import Router

from app.handlers.main_h import main_r
from app.handlers.casino_h import casino_r
from app.handlers.commands_h import commands_r
from app.handlers.background_h import background_r


#Создаём роутер, добавляем в него роутеры из ВСЕХ других файлов _h, и возвращаем этот роутер
def setup_routers()-> Router:
    router = Router()
    router.include_routers(main_r)
    router.include_router(casino_r)
    router.include_routers(commands_r)
    router.include_routers(background_r)
    return router