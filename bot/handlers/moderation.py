from aiogram import Router, F
from aiogram.types import Message
from bot.services.db import log_moderation

router = Router()
BAD_WORDS = ["badword1", "badword2", "spam"]

@router.message(F.text)
async def auto_moderate(message: Message):
    text = message.text.lower()
    for word in BAD_WORDS:
        if word in text:
            await message.delete()
            await message.answer("Inappropriate language.")
            await log_moderation(message.from_user.id, "delete_message", f"bad word: {word}")
            return