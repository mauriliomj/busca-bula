from alembic import op
import sqlalchemy as sa

revision = "c5e8a3d6f1b4"
down_revision = "b7d41e0c9a25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("consultation_history_consented_at", sa.DateTime(timezone=True), nullable=True))
    op.create_table(
        "consultations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("registration_number", sa.String(9), nullable=False),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("active_ingredient", sa.Text(), nullable=True),
        sa.Column("consulted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "registration_number", name="uq_consultations_user_registration"),
    )
    op.create_index("ix_consultations_user_consulted_at", "consultations", ["user_id", "consulted_at"])


def downgrade() -> None:
    op.drop_index("ix_consultations_user_consulted_at", table_name="consultations")
    op.drop_table("consultations")
    op.drop_column("users", "consultation_history_consented_at")
