from alembic import op
import sqlalchemy as sa

revision = "b7d41e0c9a25"
down_revision = "8a3f2c6e1d97"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "branding",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("primary_color", sa.String(7), nullable=True),
        sa.Column("secondary_color", sa.String(7), nullable=True),
        sa.Column("logo", sa.LargeBinary(), nullable=True),
        sa.Column("logo_content_type", sa.String(40), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("branding")
