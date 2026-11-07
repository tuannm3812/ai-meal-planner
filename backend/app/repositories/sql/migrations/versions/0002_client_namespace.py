"""G4: every record gets a client namespace, and plans an indexed request id.

Existing records join the open local mode's namespace, as ``client_of`` treats
them. The request id is copied out of each stored plan, so feedback can still
find plans written before this column existed.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# Copied rather than imported: a revision must keep meaning what it meant when
# it was written, whatever the app's constants become.
LOCAL_CLIENT_ID = "local"

meal_plans = sa.table(
    "meal_plans",
    sa.column("id", sa.Integer()),
    sa.column("client_id", sa.String()),
    sa.column("request_id", sa.String()),
    sa.column("payload", sa.JSON()),
)
meal_feedback = sa.table("meal_feedback", sa.column("client_id", sa.String()))


def upgrade() -> None:
    """Add the columns, fill them from existing rows, then index them."""
    with op.batch_alter_table("meal_plans") as batch:
        batch.add_column(sa.Column("client_id", sa.String(), nullable=True))
        batch.add_column(sa.Column("request_id", sa.String(), nullable=True))
    with op.batch_alter_table("meal_feedback") as batch:
        batch.add_column(sa.Column("client_id", sa.String(), nullable=True))

    connection = op.get_bind()
    connection.execute(meal_plans.update().values(client_id=LOCAL_CLIENT_ID))
    connection.execute(meal_feedback.update().values(client_id=LOCAL_CLIENT_ID))
    rows = connection.execute(sa.select(meal_plans.c.id, meal_plans.c.payload)).all()
    for row_id, payload in rows:
        request_id = payload.get("request_id") if isinstance(payload, dict) else None
        if isinstance(request_id, str):
            connection.execute(
                meal_plans.update().where(meal_plans.c.id == row_id).values(request_id=request_id)
            )

    with op.batch_alter_table("meal_plans") as batch:
        batch.alter_column("client_id", existing_type=sa.String(), nullable=False)
        batch.create_index("ix_meal_plans_client_id", ["client_id"])
        batch.create_index("ix_meal_plans_request_id", ["request_id"])
    with op.batch_alter_table("meal_feedback") as batch:
        batch.alter_column("client_id", existing_type=sa.String(), nullable=False)
        batch.create_index("ix_meal_feedback_client_id", ["client_id"])


def downgrade() -> None:
    """Remove the columns and their indexes."""
    with op.batch_alter_table("meal_feedback") as batch:
        batch.drop_index("ix_meal_feedback_client_id")
        batch.drop_column("client_id")
    with op.batch_alter_table("meal_plans") as batch:
        batch.drop_index("ix_meal_plans_request_id")
        batch.drop_index("ix_meal_plans_client_id")
        batch.drop_column("request_id")
        batch.drop_column("client_id")
