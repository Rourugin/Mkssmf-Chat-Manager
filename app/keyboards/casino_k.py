from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


casino_default = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='додеп(50%)', callback_data='half_dep'),
     InlineKeyboardButton(text='деп(100%)', callback_data='max_dep')],
    [InlineKeyboardButton(text='слиться', callback_data='quit_dep')]
])

casino_bid = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='депать', callback_data='dep')],
    [InlineKeyboardButton(text='слиться', callback_data='quit_dep')]
])