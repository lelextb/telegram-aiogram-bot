from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from bot.services.db import (
    get_or_create_user,
    log_command,
    create_trade,
    confirm_trade,
    create_temp_invite,
    verify_invite,
    log_moderation
)
from bot.services.redis_pubsub import publish_event
import asyncio

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    await log_command(message.from_user.id, "/start")
    await publish_event("bot_events", {"event": "user_start", "user_id": user.telegram_id})
    await message.answer(f"Hello {message.from_user.username}! Use /help for commands.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await log_command(message.from_user.id, "/help")
    await publish_event("bot_events", {"event": "help_used", "user_id": message.from_user.id})
    text = """
/start - Start bot
/trade - Initiate a trade (button based)
/timer - Start a one‑use timer button
/invite - Generate temporary invite link
    """
    await message.answer(text)

@router.message(Command("timer"))
async def cmd_timer(message: Message):
    await log_command(message.from_user.id, "/timer")
    await publish_event("bot_events", {"event": "timer_used", "user_id": message.from_user.id})
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Start 10s Timer", callback_data="timer_start")]
    ])
    await message.answer("Click the button to start timer (works only once)", reply_markup=keyboard)

@router.callback_query(F.data == "timer_start")
async def timer_callback(callback: CallbackQuery):
    await callback.answer("Timer started!")
    await callback.message.edit_reply_markup(reply_markup=None)
    await asyncio.sleep(10)
    await callback.message.answer("⏰ Timer finished!")
    # Optionally log callback usage
    await log_command(callback.from_user.id, "/timer_callback")

@router.message(Command("trade"))
async def cmd_trade(message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    await log_command(message.from_user.id, "/trade")
    await publish_event("bot_events", {"event": "trade_created", "user_id": user.telegram_id})
    trade = await create_trade(user.id, {"item": "Example item", "amount": 1})
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Accept Trade", callback_data=f"accept_trade:{trade.id}")]
    ])
    await message.answer(f"Trade #{trade.id} created. Another user can accept:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("accept_trade:"))
async def accept_trade(callback: CallbackQuery):
    trade_id = int(callback.data.split(":")[1])
    acceptor = await get_or_create_user(callback.from_user.id, callback.from_user.username)
    await confirm_trade(trade_id, acceptor.id)
    await log_command(callback.from_user.id, f"/accept_trade_{trade_id}")
    await publish_event("bot_events", {"event": "trade_accepted", "trade_id": trade_id, "acceptor_id": acceptor.telegram_id})
    await callback.answer("Trade accepted!")
    await callback.message.edit_text(f"Trade #{trade_id} confirmed by {callback.from_user.username}")

@router.message(Command("invite"))
async def cmd_invite(message: Message):
    await log_command(message.from_user.id, "/invite")
    await publish_event("bot_events", {"event": "invite_created", "user_id": message.from_user.id})
    code = await create_temp_invite(message.from_user.id, expires_minutes=10)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Copy invite link", url=f"https://t.me/your_bot?start=invite_{code}")]
    ])
    await message.answer(f"Temporary invite link (valid 10 min):\n`https://t.me/your_bot?start=invite_{code}`", reply_markup=keyboard, parse_mode="Markdown")

@router.message(F.text.startswith("/start invite_"))
async def process_invite(message: Message):
    code = message.text.split("_")[1]
    inviter_id = await verify_invite(code)
    await log_command(message.from_user.id, "/start_invite")
    if inviter_id:
        await publish_event("bot_events", {"event": "invite_used", "inviter_id": inviter_id, "new_user": message.from_user.id})
        await message.answer(f"You were invited by user {inviter_id}. Access granted.")
    else:
        await message.answer("Invalid or expired invite link.")