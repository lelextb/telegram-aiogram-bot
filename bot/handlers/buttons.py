from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio

router = Router()

# Timer button that disables after use
@router.message(Command("timer"))
async def cmd_timer(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Start 10s Timer", callback_data="timer_start")]
    ])
    await message.answer("Click the button to start timer (works only once)", reply_markup=keyboard)

@router.callback_query(F.data == "timer_start")
async def timer_callback(callback: CallbackQuery):
    # Disable button immediately
    await callback.answer("Timer started!")
    await callback.message.edit_reply_markup(reply_markup=None)  # remove button
    # Wait 10 seconds
    await asyncio.sleep(10)
    await callback.message.answer("⏰ Timer finished!")

# Additional generic button handler (example)
@router.callback_query(F.data.startswith("action_"))
async def generic_button(callback: CallbackQuery):
    await callback.answer("Button clicked")
    await callback.message.answer("Action executed")