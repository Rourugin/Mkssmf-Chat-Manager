import secrets
import asyncio
from aiogram import Router, F
from typing import Any, Sequence
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

import app.database.models as md
import app.database.requests as rq
import app.keyboards.casino_k as kb


casino_r = Router()
casino_r.message.filter(F.chat.type == 'supergroup')

SYMBOLS: list[str] = ['🫨', '👅', '🇬🇱', '🐒', '🎰', '🤡', '🔯']
REEL_CONFIG = [
    (0, 26, 0.35),
    (1, 24, 0.45),
    (2, 20, 0.65),
    (3, 13, 1.15),
    (4, 4,  4.20),
    (5, 7,  0.80), 
    (6, 6, -0.50),
]
POPULATION = [item[0] for item in REEL_CONFIG]
WEIGHTS = [item[1] for item in REEL_CONFIG]
ENERGY_MAP = [item[2] for item in REEL_CONFIG]


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


def get_weighted_symbol() -> int:
    total_weight = sum(WEIGHTS)
    roll = secrets.randbelow(total_weight)

    current = 0
    for symbol_idx, weight in zip(POPULATION, WEIGHTS):
        current += weight
        if roll < current:
            return symbol_idx
    return 0


def calculate_complex_payout(result: list[int], bet: int) -> tuple[int, str]:
    a, b, c = result
    unique = set(result)

    entropy_noise = 0.88 + (secrets.randbelow(25) / 100.0)
    raw_energy = ENERGY_MAP[a] + ENERGY_MAP[b] + ENERGY_MAP[c]
    monkey_count = result.count(3)
    if monkey_count > 0:
        raw_energy *= (1 + 0.25 * monkey_count)

    if a == b == c == 4:
        win = int(bet * 35 * entropy_noise)
        return win, "джекпот хуй те в рот"

    if a == b== c == 6:
        if secrets.randbelow(2) == 1:
            win = int(bet * 15 * entropy_noise)
            return win, "евреи взорвались и ты получил бананы"
        else:
            return -int(bet * 0.5), "злые евреи украли твои бананы"

    if len(unique) == 1:
        mult = (max(0.5, raw_energy) ** 1.4) * 1.8 * entropy_noise
        return int(bet * mult), "три в ряд, прямо как..."

    if len(unique) == 2 and 5 in unique and 6 not in unique:
        main_sym = next(x for x in result if x != 5)
        base_mult = (ENERGY_MAP[main_sym] * 3) ** 1.2
        win = int(bet * base_mult * 0.65 * entropy_noise)
        return win, "клоун собрал комбинацию и забрал часть кожурки"

    if a == c and a != 6:
        curse_pentaly = 0.5 if b == 6 else 1.0
        mult = (0.4 + ENERGY_MAP[a] * 0.65) * curse_pentaly * entropy_noise
        return int(bet * mult), "крайние отрожаются, прикольно"

    if 6 in result:
        return 0, "евреи опять всё испортили..."

    return 0, "ничегошеньки:3"


async def spin_casino(message: Message, bet: int) -> Any:
    if bet <= 0:
        await message.reply("ты молодец, что придумал абуз, но я тебе не дам этого сделать, плохиш (ставка должна быть > 0)")
        return

    async with md.async_session() as session:
        user = await rq.get_user(message.from_user.id)

        result = [get_weighted_symbol() for _ in range(3)]
        user.bananas -= int(bet)

        payout, status_text = calculate_complex_payout(result, int(bet))
        user.bananas += payout

        if user.bananas < 0:
            user.status = 0

        await session.merge(user)
        await session.commit()
        final_balance = user.bananas

        await spin_animation(message, result, payout, status_text, final_balance)


async def spin_animation(message: Message, result: Sequence[int], payout: int, status_text: str, final_balance: int) -> Message:
    FRAMES: int = 5
    DELAY: float = 0.75

    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    mention = user.mention_html(user.first_name)

    start_text = f"{mention} депает\n\n[ {{items}} ]"
    last_text = ""

    for frame in range(FRAMES):
        current_items = []
        for slot_idx in range(3):
            if (frame >= 2 and slot_idx == 0) or (frame >= 4 and slot_idx == 1):
                current_items.append(SYMBOLS[result[slot_idx]])
            else:
                current_items.append(secrets.choice(SYMBOLS))

        new_text = start_text.format(items=" | ".join(current_items))
        if new_text != last_text:
            try:
                await message.edit_text(new_text, parse_mode="HTML")
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except TelegramBadRequest:
                pass

        await asyncio.sleep(DELAY)

    final_symbols = [SYMBOLS[i] for i in result]

    if payout > 0:
        outcome_line = f"доход составил: {payout} бананчиков"
    elif payout < 0:
        outcome_line = f"проебал {payout} бананчиков"
    else:
        outcome_line = f"ставочка не сыграла"

    final_text = (
        f"{mention} депнул:\n\n"
        f"[ {' | '.join(final_symbols)} ]\n\n"
        f"<i>{status_text}</i>\n"
        f"{outcome_line}\n"
        f"Баланс: <b>{final_balance}</b>"
    )

    while True:
        try:
            await message.edit_text(final_text, parse_mode="HTML")
            break
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TelegramBadRequest:
            pass

    return message


