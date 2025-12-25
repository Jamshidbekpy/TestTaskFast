from datetime import datetime
import uuid
from sqlalchemy import Integer, String, ForeignKey, func, Boolean, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_mixin
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .database import Base
@declarative_mixin
class BaseMixin:
    """Yozuv yaratilgan va yangilangan vaqtni qo‘shuvchi mikskin."""

    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        nullable=False,
        comment="Yozuv yaratilgan sana va vaqt"
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Yozuv oxirgi yangilangan sana va vaqt"
    )
    
class User(Base, BaseMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String)
    time_zone: Mapped[str] = mapped_column(
        String, nullable=False, default="Asia/Tashkent"
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Event(Base, BaseMixin):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )

    title: Mapped[str | None] = mapped_column(String)
    all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    time_start: Mapped[datetime | None] = mapped_column(DateTime)
    time_end: Mapped[datetime | None] = mapped_column(DateTime)
    repeat: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(String)
    note: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="events")
    invites: Mapped[list["EventInvite"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )

class EventInvite(Base, BaseMixin):
    __tablename__ = "event_invites"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE")
    )

    email: Mapped[str] = mapped_column(String, nullable=False)

    event: Mapped["Event"] = relationship(back_populates="invites")
    alerts: Mapped[list["EventAlert"]] = relationship(
        back_populates="invite", cascade="all, delete-orphan"
    )


class EventAlert(Base, BaseMixin):
    __tablename__ = "event_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("event_invites.id", ondelete="CASCADE"),
    )

    offset_seconds: Mapped[int] = mapped_column(
        Integer, default=600  # 10 daqiqa oldin
    )

    invite: Mapped["EventInvite"] = relationship(back_populates="alerts")


class AuditLog(Base, BaseMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID| None] = mapped_column(UUID(as_uuid=True))
    event_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    action: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSONB)


class BlacklistToken(Base, BaseMixin):
    __tablename__ = "blacklist_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)