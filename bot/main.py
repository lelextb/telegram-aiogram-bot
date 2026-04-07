import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from bot.config import BOT_TOKEN, USE_WEBHOOK, WEBHOOK_URL, WEBHOOK_SECRET
from bot.handlers import commands, moderation
from bot.models.sqlalchemy_models import init_db   # <-- changed
from bot.services.redis_pubsub import get_redis

logging.basicConfig(level=logging.INFO)

async def on_startup(bot: Bot):
    await init_db()
    await get_redis()
    if USE_WEBHOOK:
        await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)
        logging.info("Webhook set")
    else:
        logging.info("Long polling mode – no webhook")

async def on_shutdown(bot: Bot):
    if USE_WEBHOOK:
        await bot.delete_webhook()

def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(commands.router, moderation.router)

    if USE_WEBHOOK:
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET)
        webhook_requests_handler.register(app, path="/webhook")
        setup_application(app, dp, bot=bot)
        app.on_startup.append(lambda _: on_startup(bot))
        app.on_shutdown.append(lambda _: on_shutdown(bot))
        web.run_app(app, host="0.0.0.0", port=8080)
    else:
        async def async_main():
            await on_startup(bot)
            await dp.start_polling(bot)
        asyncio.run(async_main())

if __name__ == "__main__":
    main()