"""The schema Phase 2 shipped with create_all, before G4.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the two tables and their indexes."""
    op.create_table(
        "meal_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("saved_at", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
    )
    op.create_index("ix_meal_plans_user_id", "meal_plans", ["user_id"])
    op.create_table(
        "meal_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("saved", sa.Boolean(), nullable=False),
        sa.Column("saved_at", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
    )
    op.create_index("ix_meal_feedback_user_id", "meal_feedback", ["user_id"])
    op.create_index("ix_meal_feedback_saved", "meal_feedback", ["saved"])


def downgrade() -> None:
    """Drop both tables."""
    op.drop_table("meal_feedback")
    op.drop_table("meal_plans")
