import redis.asyncio as redis
import json
from bot.config import REDIS_URL

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

async def publish_event(channel: str, data: dict):
    r = await get_redis()
    await r.publish(channel, json.dumps(data))