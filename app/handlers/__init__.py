from aiogram import Router

from app.handlers.main_h import main_r


#Создаём роутер, добавляем в него роутеры из ВСЕХ других файлов _h, и возвращаем этот роутер
def setup_routers()-> Router:
    router = Router()
    router.include_routers(main_r)
    return router