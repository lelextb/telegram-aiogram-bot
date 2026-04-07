from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from bot.services.db import create_trade, confirm_trade, get_or_create_user

router = Router()

@router.message(Command("trade"))
async def cmd_trade(message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    trade = await create_trade(user.id, {"item": "Example item"})
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Accept Trade", callback_data=f"accept_trade:{trade.id}")]
    ])
    await message.answer(f"Trade #{trade.id} created. Another user can accept:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("accept_trade:"))
async def accept_trade(callback: CallbackQuery):
    trade_id = int(callback.data.split(":")[1])
    acceptor = await get_or_create_user(callback.from_user.id, callback.from_user.username)
    await confirm_trade(trade_id, acceptor.id)
    await callback.answer("Trade accepted!")
    await callback.message.edit_text(f"Trade #{trade_id} confirmed by {callback.from_user.username}")