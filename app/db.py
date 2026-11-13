from collections.abc import AsyncGenerator
import uuid
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/social_media_app"
)


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id=Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False) # foreign key to users table
    caption = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    user=relationship("User",back_populates="posts") # relationship to User model

class User(Base):
    __tablename__="users"

    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    email=Column(String(255),unique=True,nullable=False)
    hashed_password=Column(String(255),nullable=False)
    created_at=Column(
        DateTime(timezone=True),default=lambda:datetime.now(timezone.utc)
    )
    is_active=Column(Boolean,nullable=False,default=True)
    is_superuser=Column(Boolean,nullable=False,default=False)

    posts=relationship("Post",back_populates="user") # relationship to Post model



engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
