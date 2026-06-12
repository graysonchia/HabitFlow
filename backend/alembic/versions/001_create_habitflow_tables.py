"""create habitflow tables

Revision ID: 001_create_habitflow_tables
Revises:
Create Date: 2026-06-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_create_habitflow_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("age_group", sa.String(length=20), nullable=True),
        sa.Column("timezone", sa.String(length=50), nullable=True),
        sa.Column("join_date", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_premium", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "habits",
        sa.Column("habit_id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("habit_name", sa.String(length=150), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("target_freq", sa.String(length=20), nullable=True),
        sa.Column("reminder_time", sa.Time(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("habit_id"),
    )
    op.create_index(op.f("ix_habits_user_id"), "habits", ["user_id"], unique=False)

    op.create_table(
        "checkins",
        sa.Column("checkin_id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("habit_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("checked_date", sa.Date(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("mood_score", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("checkin_ts", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("mood_score BETWEEN 1 AND 10", name="ck_checkins_mood_score_range"),
        sa.ForeignKeyConstraint(["habit_id"], ["habits.habit_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("checkin_id"),
        sa.UniqueConstraint("user_id", "habit_id", "checked_date", name="uq_checkins_user_habit_date"),
    )
    op.create_index("idx_checkins_user_date", "checkins", ["user_id", "checked_date"], unique=False)
    op.create_index("idx_checkins_habit_date", "checkins", ["habit_id", "checked_date"], unique=False)
    op.create_index("idx_checkins_date", "checkins", ["checked_date"], unique=False)

    op.create_table(
        "streaks",
        sa.Column("streak_id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("habit_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("length", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.ForeignKeyConstraint(["habit_id"], ["habits.habit_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("streak_id"),
    )
    op.create_index("idx_streaks_user", "streaks", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_streaks_user", table_name="streaks")
    op.drop_table("streaks")
    op.drop_index("idx_checkins_date", table_name="checkins")
    op.drop_index("idx_checkins_habit_date", table_name="checkins")
    op.drop_index("idx_checkins_user_date", table_name="checkins")
    op.drop_table("checkins")
    op.drop_index(op.f("ix_habits_user_id"), table_name="habits")
    op.drop_table("habits")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
