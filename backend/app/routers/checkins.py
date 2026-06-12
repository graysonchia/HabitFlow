from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.checkin import Checkin
from app.models.habit import Habit
from app.models.user import User
from app.schemas.checkin import CheckinCreate, CheckinResponse, CheckinSummaryResponse, TodayHabitResponse
from app.utils.auth import get_current_user
from app.utils.streak_calculator import calculate_longest_streak, calculate_streak

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.post("", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
async def log_checkin(
    payload: CheckinCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Checkin:
    await _ensure_owned_habit(db, current_user.user_id, payload.habit_id)

    statement = (
        insert(Checkin)
        .values(user_id=current_user.user_id, **payload.model_dump())
        .on_conflict_do_update(
            constraint="uq_checkins_user_habit_date",
            set_={
                "completed": payload.completed,
                "mood_score": payload.mood_score,
                "note": payload.note,
                "checkin_ts": func.now(),
            },
        )
        .returning(Checkin)
    )
    result = await db.execute(statement)
    await db.commit()
    return result.scalar_one()


@router.get("", response_model=list[CheckinResponse])
async def list_checkins(
    days: int = Query(default=30, ge=1, le=3650),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Checkin]:
    start_date = date.today() - timedelta(days=days - 1)
    result = await db.execute(
        select(Checkin)
        .where(Checkin.user_id == current_user.user_id, Checkin.checked_date >= start_date)
        .order_by(Checkin.checked_date.desc(), Checkin.checkin_ts.desc())
    )
    return list(result.scalars().all())


@router.get("/today", response_model=list[TodayHabitResponse])
async def get_today_checkins(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TodayHabitResponse]:
    today = date.today()
    result = await db.execute(
        select(Habit, Checkin)
        .outerjoin(
            Checkin,
            (Checkin.habit_id == Habit.habit_id)
            & (Checkin.user_id == current_user.user_id)
            & (Checkin.checked_date == today),
        )
        .where(Habit.user_id == current_user.user_id, Habit.is_active.is_(True))
        .order_by(Habit.created_at.desc())
    )

    responses: list[TodayHabitResponse] = []
    for habit, checkin in result.all():
        responses.append(
            TodayHabitResponse(
                habit_id=habit.habit_id,
                habit_name=habit.habit_name,
                category=habit.category,
                target_freq=habit.target_freq,
                reminder_time=habit.reminder_time,
                checked_today=checkin is not None,
                completed=checkin.completed if checkin else None,
                mood_score=checkin.mood_score if checkin else None,
                checkin_id=checkin.checkin_id if checkin else None,
            )
        )
    return responses


@router.get("/streak/{habit_id}")
async def get_current_streak(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int | UUID]:
    await _ensure_owned_habit(db, current_user.user_id, habit_id)
    result = await db.execute(
        select(Checkin.checked_date)
        .where(
            Checkin.user_id == current_user.user_id,
            Checkin.habit_id == habit_id,
            Checkin.completed.is_(True),
        )
        .order_by(Checkin.checked_date)
    )
    completed_dates = list(result.scalars().all())
    return {"habit_id": habit_id, "current_streak": calculate_streak(completed_dates)}


@router.get("/summary", response_model=CheckinSummaryResponse)
async def get_summary(
    days: int = Query(default=7, ge=1, le=3650),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckinSummaryResponse:
    start_date = date.today() - timedelta(days=days - 1)
    checkins_result = await db.execute(
        select(Checkin).where(
            Checkin.user_id == current_user.user_id,
            Checkin.checked_date >= start_date,
        )
    )
    checkins = list(checkins_result.scalars().all())

    active_habits_result = await db.execute(
        select(func.count()).select_from(Habit).where(
            Habit.user_id == current_user.user_id,
            Habit.is_active.is_(True),
            Habit.created_at <= func.now(),
        )
    )
    active_habit_count = active_habits_result.scalar_one()

    completed_checkins = [checkin for checkin in checkins if checkin.completed]
    mood_scores = [checkin.mood_score for checkin in checkins if checkin.mood_score is not None]
    completion_slots = active_habit_count * days
    completion_rate = (len(completed_checkins) / completion_slots * 100) if completion_slots else 0.0
    completed_dates = sorted(checkin.checked_date for checkin in completed_checkins)

    return CheckinSummaryResponse(
        days=days,
        total_completions=len(completed_checkins),
        avg_mood_score=round(sum(mood_scores) / len(mood_scores), 2) if mood_scores else None,
        completion_rate_percent=round(completion_rate, 2),
        best_streak=calculate_longest_streak(completed_dates),
    )


async def _ensure_owned_habit(db: AsyncSession, user_id: UUID, habit_id: UUID) -> None:
    result = await db.execute(
        select(Habit.habit_id).where(
            Habit.habit_id == habit_id,
            Habit.user_id == user_id,
            Habit.is_active.is_(True),
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
