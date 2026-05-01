from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

DATABASE_URL = "postgresql+asyncpg://user:password@db/proxy_service"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    email:Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    activation_key: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    activation_key_expires:Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vm:Mapped[Optional["VirtualMachine"]] = relationship("VirtualMachine", back_populates="current_user")

class VirtualMachine(Base):
    __tablename__ = "virtual_machines"

    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    name:Mapped[str] = mapped_column(String)
    host:Mapped[str] = mapped_column(String)
    port:Mapped[int] = mapped_column(Integer)
    protocol:Mapped[str] = mapped_column(String, default="socks5")
    is_active:Mapped[bool] = mapped_column(Boolean, default=True)
    current_user_id:Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    current_user: Mapped[Optional["User"]] = relationship("User", back_populates="vm")
