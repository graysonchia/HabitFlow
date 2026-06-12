from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.habit import Habit
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitResponse, HabitUpdate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    payload: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Habit:
    habit = Habit(user_id=current_user.user_id, **payload.model_dump())
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit


@router.get("", response_model=list[HabitResponse])
async def list_habits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Habit]:
    result = await db.execute(
        select(Habit)
        .where(Habit.user_id == current_user.user_id, Habit.is_active.is_(True))
        .order_by(Habit.created_at.desc())
    )
    return list(result.scalars().all())


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: UUID,
    payload: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Habit:
    habit = await _get_owned_habit(db, current_user.user_id, habit_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(habit, field, value)

    await db.commit()
    await db.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    habit = await _get_owned_habit(db, current_user.user_id, habit_id)
    habit.is_active = False
    await db.commit()


async def _get_owned_habit(db: AsyncSession, user_id: UUID, habit_id: UUID) -> Habit:
    result = await db.execute(
        select(Habit).where(
            Habit.habit_id == habit_id,
            Habit.user_id == user_id,
            Habit.is_active.is_(True),
        )
    )
    habit = result.scalar_one_or_none()
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    return habit
