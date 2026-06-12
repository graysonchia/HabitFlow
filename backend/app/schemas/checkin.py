from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CheckinBase(BaseModel):
    habit_id: UUID
    checked_date: date
    completed: bool
    mood_score: int | None = Field(default=None, ge=1, le=10)
    note: str | None = None


class CheckinCreate(CheckinBase):
    pass


class CheckinResponse(CheckinBase):
    model_config = ConfigDict(from_attributes=True)

    checkin_id: UUID
    user_id: UUID
    checkin_ts: datetime


class TodayHabitResponse(BaseModel):
    habit_id: UUID
    habit_name: str
    category: str | None
    target_freq: str | None
    reminder_time: time | None
    checked_today: bool
    completed: bool | None = None
    mood_score: int | None = None
    checkin_id: UUID | None = None


class CheckinSummaryResponse(BaseModel):
    days: int
    total_completions: int
    avg_mood_score: float | None
    completion_rate_percent: float
    best_streak: int
