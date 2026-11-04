from alembic import op
import sqlalchemy as sa

revision = "e1f6c2b8d4a7"
down_revision = "9d2b7f4a1c08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leaflet_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("registration_number", sa.String(9), nullable=False, unique=True),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("expedient_number", sa.String(20), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "leaflet_sections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("leaflet_documents.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("section_number", sa.SmallInteger(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.UniqueConstraint("document_id", "section_number", name="uq_leaflet_sections_document_number"),
    )


def downgrade() -> None:
    op.drop_table("leaflet_sections")
    op.drop_table("leaflet_documents")
