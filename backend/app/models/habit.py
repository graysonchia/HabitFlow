from datetime import datetime, time
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Time, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class Habit(Base):
    __tablename__ = "habits"

    habit_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    habit_name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))
    target_freq: Mapped[str | None] = mapped_column(String(20))
    reminder_time: Mapped[time | None] = mapped_column(Time)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)

    user: Mapped["User"] = relationship(back_populates="habits")
    checkins: Mapped[list["Checkin"]] = relationship(
        back_populates="habit",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    streaks: Mapped[list["Streak"]] = relationship(
        back_populates="habit",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
