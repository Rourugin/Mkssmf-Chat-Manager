import asyncio
import logging
from typing import Sequence
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

import app.database.requests as rq


async def sync_all_channels(bot: Bot, channel_ids: Sequence[int], admin_id: int) -> None:
    for ch_id in channel_ids:
        await sync_channel_posts(bot=bot, channel_id=ch_id, admin_id=admin_id)


async def sync_channel_posts(bot: Bot, channel_id: int, admin_id: int) -> None:
    if await rq.has_channel_posts(channel_id):
        return

    try:
        probe_msg = await bot.send_message(chat_id=channel_id, text='.')
        last_post_id = probe_msg.message_id
        await probe_msg.delete()
    except Exception as e:
        logging.error(f"[{channel_id}] Не удалось определить последний пост в канале: {e}")
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
            await rq.set_post(channel_id=channel_id, post_id=msg_id, media_group_id=None)
            saved_count += 1

            await bot.delete_message(chat_id=admin_id, message_id=copied.message_id)
            msg_id += 1
            retries = 0
            await asyncio.sleep(0.6)
        except TelegramRetryAfter as e:
            logging.warning(f"[{channel_id}] Флуд-лимит! Жду {e.retry_after} сек на посте #{msg_id}...")
            await asyncio.sleep(e.retry_after)
        except TelegramBadRequest as e:
            if "chat not found" in str(e).lower() or "bot was blocked" in str(e).lower():
                logging.error(f"[{channel_id}] Ошибка доступа к ADMIN_ID: {e}")
                return
            msg_id += 1
            retries = 0
        except Exception as e:
            retries += 1
            if retries >= 2:
                logging.warning(f"[{channel_id}] [{msg_id}/{last_post_id - 1}] Пропущен #{msg_id} после {retries} сбоев ({type(e).__name__}: {e})")
                msg_id += 1
                retries = 0
            else:
                logging.warning(f"[{channel_id}] Сбой на посте #{msg_id} ({type(e).__name__}: {e}), повтор через 2 сек...")
