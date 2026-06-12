from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class Checkin(Base):
    __tablename__ = "checkins"
    __table_args__ = (
        CheckConstraint("mood_score BETWEEN 1 AND 10", name="ck_checkins_mood_score_range"),
        UniqueConstraint("user_id", "habit_id", "checked_date", name="uq_checkins_user_habit_date"),
        Index("idx_checkins_user_date", "user_id", "checked_date"),
        Index("idx_checkins_habit_date", "habit_id", "checked_date"),
        Index("idx_checkins_date", "checked_date"),
    )

    checkin_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    habit_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("habits.habit_id", ondelete="CASCADE"),
        nullable=False,
    )
    checked_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    mood_score: Mapped[int | None] = mapped_column()
    note: Mapped[str | None] = mapped_column(Text)
    checkin_ts: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="checkins")
    habit: Mapped["Habit"] = relationship(back_populates="checkins")
