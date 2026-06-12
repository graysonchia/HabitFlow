from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HabitBase(BaseModel):
    habit_name: str = Field(min_length=1, max_length=150)
    category: str | None = Field(default=None, max_length=50)
    target_freq: str | None = Field(default=None, max_length=20)
    reminder_time: time | None = None


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    habit_name: str | None = Field(default=None, min_length=1, max_length=150)
    category: str | None = Field(default=None, max_length=50)
    target_freq: str | None = Field(default=None, max_length=20)
    reminder_time: time | None = None
    is_active: bool | None = None


class HabitResponse(HabitBase):
    model_config = ConfigDict(from_attributes=True)

    habit_id: UUID
    user_id: UUID
    created_at: datetime
    is_active: bool
