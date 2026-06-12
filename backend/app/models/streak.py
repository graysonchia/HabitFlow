from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class Streak(Base):
    __tablename__ = "streaks"
    __table_args__ = (Index("idx_streaks_user", "user_id"),)

    streak_id: Mapped[UUID] = mapped_column(
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
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    length: Mapped[int] = mapped_column(Integer, server_default="1", default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)

    user: Mapped["User"] = relationship(back_populates="streaks")
    habit: Mapped["Habit"] = relationship(back_populates="streaks")
