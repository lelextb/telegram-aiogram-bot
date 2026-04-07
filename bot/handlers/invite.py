from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from bot.services.db import create_temp_invite, verify_invite

router = Router()

@router.message(Command("invite"))
async def cmd_invite(message: Message):
    code = await create_temp_invite(message.from_user.id, expires_minutes=10)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Copy invite link", url=f"https://t.me/your_bot?start=invite_{code}")]
    ])
    await message.answer(f"Temporary invite link (valid 10 min):\n`https://t.me/your_bot?start=invite_{code}`", reply_markup=keyboard, parse_mode="Markdown")

@router.message(F.text.startswith("/start invite_"))
async def process_invite(message: Message):
    code = message.text.split("_")[1]
    inviter_id = await verify_invite(code)
    if inviter_id:
        await message.answer(f"You were invited by user {inviter_id}. Access granted.")
    else:
        await message.answer("Invalid or expired invite link.")