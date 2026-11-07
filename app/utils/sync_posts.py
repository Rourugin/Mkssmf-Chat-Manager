import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

import app.database.requests as rq


async def sync_channel_posts(bot: Bot, channel_id: int, admin_id: int) -> None:
    if await rq.get_random_post() is not None:
        logging.info("В базе уже есть посты. Синхронизация не требуется")
        return

    logging.info("Таблица Post пуста. Запускаю автоматический сбор старых постов...")

    try:
        probe_msg = await bot.send_message(chat_id=channel_id, text='.')
        last_post_id = probe_msg.message_id
        await probe_msg.delete()
    except Exception as e:
        logging.error(f"Не удалось определить последний пост в канале: {e}")
        return

    saved_count = 0
    msg_id = 1
    retries = 0
    while msg_id < last_post_id:
        try:
            copied = await bot.copy_message(
                chat_id=admin_id,
                from_chat_id=channel_id,
                message_id=msg_id,
                disable_notification=True
            )
            await rq.set_post(post_id=msg_id, media_group_id=None)
            saved_count += 1
            logging.info(f"[{msg_id}/{last_post_id - 1}] Сохранён пост #{msg_id}")

            await bot.delete_message(chat_id=admin_id, message_id=copied.message_id)
            msg_id += 1
            retries = 0
            await asyncio.sleep(0.5)
        except TelegramRetryAfter as e:
            logging.warning(f"Флуд-лимит! Жду {e.retry_after} сек на посте #{msg_id}...")
            await asyncio.sleep(e.retry_after)
        except TelegramBadRequest as e:
            if "chat not found" in str(e).lower() or "bot was blocked" in str(e).lower():
                logging.error(f"Ошибка доступа к ADMIN_ID: {e}")
                return
            msg_id += 1
            retries = 0
        except Exception as e:
            retries += 1
            if retries >= 2:
                logging.warning(f"[{msg_id}/{last_post_id - 1}] Пропущен #{msg_id} после {retries} сбоев ({type(e).__name__}: {e})")
                msg_id += 1
                retries = 0
            else:
                logging.warning(f"Сбой на посте #{msg_id} ({type(e).__name__}: {e}), повтор через 2 сек...")
                await asyncio.sleep(2.0)

    logging.info(f"Синхронизация завершена! В базу добавлено постов: {saved_count}")