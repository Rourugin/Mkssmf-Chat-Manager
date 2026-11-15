import random
import asyncio
from aiogram import Router, F
from typing import Any, Sequence
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramNetworkError

import app.database.models as md
import app.database.requests as rq
import app.keyboards.casino_k as kb


casino_r = Router()
casino_r.message.filter(F.chat.type == 'supergroup')


@casino_r.message(Command(commands=['casino']))
async def cmd_casino(message: Message) -> Any:
    user = await rq.get_user(message.from_user.id)
    text = f"Гой хочет прогреться\n\nВаш баланс: {user.bananas}"
    parts = message.text.split()
    if len(parts) == 1:
        text += "\n\nЕсли хочешь другую ставку, напиши /casino [ставка] (без сксобок, урод)"
        await message.reply(text=text, reply_markup=kb.casino_default)
    elif len(parts) > 1:
        await message.reply(text=text, reply_markup=kb.casino_bid)


@casino_r.callback_query(F.data == 'half_dep')
async def half_dep_casino(callback: CallbackQuery) -> Any:
    reply = callback.message.reply_to_message
    if reply.from_user.id == callback.from_user.id:
        user = await rq.get_user(callback.from_user.id)
        await spin_casino(callback.message, int(user.bananas/2))
    elif reply.from_user.id != callback.from_user.id:
        await callback.answer("не твоя кнопка педик")
    await callback.answer()


@casino_r.callback_query(F.data == 'max_dep')
async def max_dep(callback: CallbackQuery) -> Any:
    reply = callback.message.reply_to_message
    if reply.from_user.id == callback.from_user.id:
        user = await rq.get_user(callback.from_user.id)
        await spin_casino(callback.message, int(user.bananas))
    elif reply.from_user.id != callback.from_user.id:
        await callback.answer("не твоя кнопка педик")
    await callback.answer()


@casino_r.callback_query(F.data == 'dep')
async def default_dep(callback: CallbackQuery) -> Any:
    reply = callback.message.reply_to_message
    if reply.from_user.id == callback.from_user.id:
        bet = reply.text.split()[1]
        await spin_casino(callback.message, int(bet))
    elif reply.from_user.id != callback.from_user.id:
        await callback.answer("не твоя кнопка педик")
    await callback.answer()


@casino_r.callback_query(F.data == 'quit_dep')
async def quit_casino(callback: CallbackQuery) -> Any:
    reply = callback.message.reply_to_message
    if reply.from_user.id == callback.from_user.id:
        await callback.message.edit_reply_markup(reply_markup=None)
        user = await rq.get_user(callback.from_user.id)
        user.respect -= 5
        async with md.async_session() as session:
            await session.merge(user)
            await session.commit()
        await reply.reply("лох, слился блять")
    elif reply.from_user.id != callback.from_user.id:
        await callback.answer("не твоя кнопка педик")
    await callback.answer()


async def spin_casino(message: Message, bet: int) -> Any:
    result = [
        random.randint(0, 6),
        random.randint(0, 6),
        random.randint(0, 6)
    ]

    await spin_animation(message, result)


async def spin_animation(message: Message, result: Sequence[int]) -> Message:
    SYMBOLS: list[str] = ['🫨', '👅', '🇬🇱', '🐒', '🎰', '🤡', '🔯']
    FRAMES: int = 5
    DELAY: float = 0.8

    player = message.reply_to_message.from_user
    mention = player.mention_html(player.first_name)
    start_text = f'{mention} депает...\n\n{{items}}'
    current_items = random.choices(SYMBOLS, k=3)
    last_text = start_text.format(items=" | ".join(current_items))
    await message.edit_text(last_text, parse_mode='HTML')

    for _ in range(FRAMES):
        await asyncio.sleep(DELAY)

        new_text = last_text
        while new_text == last_text:
            current_items = random.choices(SYMBOLS, k = 3)
            new_text = start_text.format(items=" | ".join(current_items))

        try:
            await message.edit_text(new_text, parse_mode="HTML")
            last_text = new_text
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TelegramBadRequest:
            pass

    await asyncio.sleep(DELAY)
    final_symbols = [SYMBOLS[i] for i in result]
    final_text = f"Результаты депа {mention}\n\n{{items}}".format(items=" | ".join(final_symbols))
    while True:
        try:
            await message.edit_text(final_text, parse_mode="HTML")
            break
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (TelegramBadRequest, TelegramNetworkError):
            break

    return message
