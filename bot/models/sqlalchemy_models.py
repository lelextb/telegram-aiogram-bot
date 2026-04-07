from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CommandLog(Base):
    __tablename__ = "command_logs"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    command = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(BigInteger, primary_key=True)
    initiator_id = Column(BigInteger, nullable=False)
    acceptor_id = Column(BigInteger, nullable=True)
    status = Column(String(20), default="pending")
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class TempInvite(Base):
    __tablename__ = "temp_invites"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    code = Column(String(64), unique=True)
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ModerationLog(Base):
    __tablename__ = "moderation_logs"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger)
    action = Column(String(50))
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)