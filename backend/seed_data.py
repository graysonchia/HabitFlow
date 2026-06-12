import os
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

import numpy as np
from dotenv import load_dotenv
from faker import Faker
from passlib.context import CryptContext
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session

from app.models import Base, Checkin, Habit, Streak, User

load_dotenv()

fake = Faker("en_US")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USER_COUNT = 500
HISTORY_DAYS = 180
HIGH_PERFORMER_RATE = 0.15
QUITTER_RATE = 0.20

AGE_GROUPS = ["18-24", "25-34", "35-44", "45+"]
TARGET_FREQUENCIES = ["daily", "weekdays", "weekends", "3x_week"]

HABIT_CATALOG = {
    "Morning Run": "fitness",
    "Drink 8 Glasses of Water": "health",
    "Meditate": "mindfulness",
    "Read 20 Pages": "productivity",
    "No Social Media Before 9am": "productivity",
    "Sleep Before Midnight": "health",
    "Workout": "fitness",
    "Journal": "mindfulness",
    "Take Vitamins": "health",
    "Walk 10,000 Steps": "fitness",
    "No Junk Food": "health",
    "Learn Something New": "productivity",
    "Call Family": "social",
    "Stretch": "fitness",
    "Cold Shower": "health",
}

NOTES_COMPLETED = [
    "Felt focused and steady today.",
    "Completed this earlier than usual.",
    "Good energy after finishing.",
    "Kept the routine even with a busy schedule.",
    "Small win, but it helped my mood.",
]

NOTES_MISSED = [
    "Too tired to finish this today.",
    "Schedule got messy.",
    "Missed it, but planning to restart tomorrow.",
    "Low motivation today.",
    "Had other priorities come up.",
]


@dataclass(frozen=True)
class UserProfile:
    is_high_performer: bool
    is_quitter: bool
    churn_cutoff: date | None


def get_sync_database_url() -> str:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:yourpassword@localhost:5432/habitflow",
    )
    return database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")


def clipped_normal(mean: float, std_dev: float) -> int:
    return int(round(float(np.clip(np.random.normal(mean, std_dev), 1, 10))))


def completion_probability(profile: UserProfile, checked_date: date) -> float:
    if profile.is_quitter and profile.churn_cutoff and checked_date > profile.churn_cutoff:
        return 0.0

    if profile.is_high_performer:
        return 0.90

    is_weekend = checked_date.weekday() >= 5
    return 0.50 if is_weekend else 0.70


def mood_score(completed: bool, profile: UserProfile) -> int:
    if profile.is_high_performer:
        mean = 8.4 if completed else 7.2
        std_dev = 1.0
    elif completed:
        mean = 7.2
        std_dev = 1.5
    else:
        mean = 5.1
        std_dev = 1.8

    return clipped_normal(mean, std_dev)


def generate_user_profile(today: date, is_high_performer: bool, is_quitter: bool) -> UserProfile:
    churn_cutoff = None

    if is_quitter:
        oldest_history_date = today - timedelta(days=HISTORY_DAYS - 1)
        churn_after_days = random.randint(30, 90)
        churn_cutoff = oldest_history_date + timedelta(days=churn_after_days)

    return UserProfile(
        is_high_performer=is_high_performer,
        is_quitter=is_quitter,
        churn_cutoff=churn_cutoff,
    )


def create_user(index: int, profile: UserProfile, today: date) -> User:
    first_name = fake.first_name()
    last_name = fake.last_name()
    email_name = f"{first_name}.{last_name}.{index}".lower().replace(" ", "")
    join_days_ago = random.randint(HISTORY_DAYS + 5, 540)

    return User(
        email=f"{email_name}@example.com",
        username=f"{first_name} {last_name}",
        password_hash=password_context.hash("Password123!"),
        age_group=random.choice(AGE_GROUPS),
        timezone="Asia/Kuala_Lumpur",
        join_date=datetime.combine(today - timedelta(days=join_days_ago), random_time(8, 21)),
        is_premium=random.random() < (0.35 if profile.is_high_performer else 0.18),
        is_active=not profile.is_quitter,
    )


def random_time(start_hour: int, end_hour: int) -> time:
    return time(
        hour=random.randint(start_hour, end_hour),
        minute=random.choice([0, 5, 10, 15, 20, 30, 40, 45, 50]),
    )


def create_habits_for_user(user: User, today: date) -> list[Habit]:
    habit_names = random.sample(list(HABIT_CATALOG.keys()), random.randint(3, 7))
    habits: list[Habit] = []

    for habit_name in habit_names:
        created_days_ago = random.randint(HISTORY_DAYS, HISTORY_DAYS + 120)
        habit = Habit(
            user_id=user.user_id,
            habit_name=habit_name,
            category=HABIT_CATALOG[habit_name],
            target_freq=random.choice(TARGET_FREQUENCIES),
            reminder_time=random_time(6, 22),
            created_at=datetime.combine(today - timedelta(days=created_days_ago), random_time(7, 20)),
            is_active=True,
        )
        habits.append(habit)

    return habits


def note_for_checkin(completed: bool) -> str | None:
    if random.random() > 0.12:
        return None
    return random.choice(NOTES_COMPLETED if completed else NOTES_MISSED)


def generate_checkins_for_habit(user: User, habit: Habit, profile: UserProfile, today: date) -> list[Checkin]:
    checkins: list[Checkin] = []
    oldest_history_date = today - timedelta(days=HISTORY_DAYS - 1)

    for day_offset in range(HISTORY_DAYS):
        checked_date = oldest_history_date + timedelta(days=day_offset)
        if profile.is_quitter and profile.churn_cutoff and checked_date > profile.churn_cutoff:
            continue

        probability = completion_probability(profile, checked_date)
        completed = random.random() < probability

        checkins.append(
            Checkin(
                user_id=user.user_id,
                habit_id=habit.habit_id,
                checked_date=checked_date,
                completed=completed,
                mood_score=mood_score(completed, profile),
                note=note_for_checkin(completed),
                checkin_ts=datetime.combine(checked_date, random_time(7, 23)),
            )
        )

    return checkins


def generate_streaks_from_checkins(user: User, habit: Habit, checkins: list[Checkin]) -> list[Streak]:
    streaks: list[Streak] = []
    active_start: date | None = None
    previous_completed_date: date | None = None

    completed_dates = sorted(checkin.checked_date for checkin in checkins if checkin.completed)
    for completed_date in completed_dates:
        if active_start is None:
            active_start = completed_date
        elif previous_completed_date and completed_date != previous_completed_date + timedelta(days=1):
            streaks.append(
                Streak(
                    user_id=user.user_id,
                    habit_id=habit.habit_id,
                    start_date=active_start,
                    end_date=previous_completed_date,
                    length=(previous_completed_date - active_start).days + 1,
                    is_active=False,
                )
            )
            active_start = completed_date

        previous_completed_date = completed_date

    if active_start and previous_completed_date:
        streaks.append(
            Streak(
                user_id=user.user_id,
                habit_id=habit.habit_id,
                start_date=active_start,
                end_date=None if previous_completed_date == date.today() else previous_completed_date,
                length=(previous_completed_date - active_start).days + 1,
                is_active=previous_completed_date == date.today(),
            )
        )

    return streaks


def clear_existing_data(session: Session) -> None:
    session.execute(delete(Streak))
    session.execute(delete(Checkin))
    session.execute(delete(Habit))
    session.execute(delete(User))
    session.commit()


def seed_database() -> None:
    random.seed(42)
    np.random.seed(42)

    engine = create_engine(get_sync_database_url(), echo=False, pool_pre_ping=True)
    Base.metadata.create_all(engine)

    today = date.today()
    total_habits = 0
    total_checkins = 0
    total_streaks = 0

    with Session(engine) as session:
        clear_existing_data(session)
        user_numbers = list(range(1, USER_COUNT + 1))
        high_performer_ids = set(random.sample(user_numbers, int(USER_COUNT * HIGH_PERFORMER_RATE)))
        quitter_pool = [user_number for user_number in user_numbers if user_number not in high_performer_ids]
        quitter_ids = set(random.sample(quitter_pool, int(USER_COUNT * QUITTER_RATE)))

        for user_index in range(1, USER_COUNT + 1):
            profile = generate_user_profile(
                today=today,
                is_high_performer=user_index in high_performer_ids,
                is_quitter=user_index in quitter_ids,
            )
            user = create_user(user_index, profile, today)
            session.add(user)
            session.flush()

            habits = create_habits_for_user(user, today)
            session.add_all(habits)
            session.flush()
            total_habits += len(habits)

            for habit in habits:
                checkins = generate_checkins_for_habit(user, habit, profile, today)
                session.add_all(checkins)
                session.flush()
                total_checkins += len(checkins)

                streaks = generate_streaks_from_checkins(user, habit, checkins)
                session.add_all(streaks)
                total_streaks += len(streaks)

            if user_index % 50 == 0:
                session.commit()
                print(f"Inserted seed data for {user_index} users...")

        session.commit()

        users_count = session.scalar(select(func.count()).select_from(User))
        habits_count = session.scalar(select(func.count()).select_from(Habit))
        checkins_count = session.scalar(select(func.count()).select_from(Checkin))
        streaks_count = session.scalar(select(func.count()).select_from(Streak))

    print("Seed data generation complete.")
    print("Summary:")
    print(f"  users: {users_count}")
    print(f"  habits: {habits_count or total_habits}")
    print(f"  checkins: {checkins_count or total_checkins}")
    print(f"  streaks: {streaks_count or total_streaks}")


if __name__ == "__main__":
    seed_database()
