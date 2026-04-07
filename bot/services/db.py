from sqlalchemy import select, update
from bot.models.sqlalchemy_models import AsyncSessionLocal, User, CommandLog, Trade, TempInvite, ModerationLog
from datetime import datetime, timedelta
import secrets

async def get_or_create_user(telegram_id: int, username: str = None):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            await session.commit()
        return user

async def log_command(user_id: int, command: str):
    async with AsyncSessionLocal() as session:
        log = CommandLog(user_id=user_id, command=command, timestamp=datetime.utcnow())
        session.add(log)
        await session.commit()

async def create_trade(initiator_id: int, data: dict):
    async with AsyncSessionLocal() as session:
        trade = Trade(initiator_id=initiator_id, data=data)
        session.add(trade)
        await session.commit()
        return trade

async def confirm_trade(trade_id: int, acceptor_id: int):
    async with AsyncSessionLocal() as session:
        stmt = update(Trade).where(Trade.id == trade_id).values(status="confirmed", acceptor_id=acceptor_id)
        await session.execute(stmt)
        await session.commit()

async def create_temp_invite(user_id: int, expires_minutes: int = 10) -> str:
    code = secrets.token_urlsafe(16)
    expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
    async with AsyncSessionLocal() as session:
        invite = TempInvite(user_id=user_id, code=code, expires_at=expires_at)
        session.add(invite)
        await session.commit()
        return code

async def verify_invite(code: str):
    async with AsyncSessionLocal() as session:
        stmt = select(TempInvite).where(TempInvite.code == code, TempInvite.expires_at > datetime.utcnow(), TempInvite.used == False)
        result = await session.execute(stmt)
        invite = result.scalar_one_or_none()
        if invite:
            stmt_upd = update(TempInvite).where(TempInvite.id == invite.id).values(used=True)
            await session.execute(stmt_upd)
            await session.commit()
            return invite.user_id
    return None

async def log_moderation(user_id: int, action: str, reason: str):
    async with AsyncSessionLocal() as session:
        log = ModerationLog(user_id=user_id, action=action, reason=reason)
        session.add(log)
        await session.commit()