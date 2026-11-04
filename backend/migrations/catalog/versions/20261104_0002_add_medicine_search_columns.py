from alembic import op
import sqlalchemy as sa

revision = "9d2b7f4a1c08"
down_revision = "3e8c5a1f7b62"
branch_labels = None
depends_on = None

ACCENTED_CHARACTERS = "ÁÀÂÃÄáàâãäÉÈÊËéèêëÍÌÎÏíìîïÓÒÔÕÖóòôõöÚÙÛÜúùûüÇçÑñ"
UNACCENTED_CHARACTERS = "AAAAAaaaaaEEEEeeeeIIIIiiiiOOOOOoooooUUUUuuuuCcNn"


def build_normalized_expression(*columns: str) -> str:
    joined = " || ' ' || ".join(f"coalesce({column}, '')" for column in columns)
    return f"lower(translate({joined}, '{ACCENTED_CHARACTERS}', '{UNACCENTED_CHARACTERS}'))"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.add_column(
        "medicines",
        sa.Column("search_name", sa.Text(), sa.Computed(build_normalized_expression("product_name"), persisted=True)),
    )
    op.add_column(
        "medicines",
        sa.Column(
            "search_text",
            sa.Text(),
            sa.Computed(
                build_normalized_expression("product_name", "active_ingredient", "therapeutic_class", "holder_name"),
                persisted=True,
            ),
        ),
    )
    op.create_index(
        "ix_medicines_search_name_trgm", "medicines", ["search_name"],
        postgresql_using="gin", postgresql_ops={"search_name": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_medicines_search_text_trgm", "medicines", ["search_text"],
        postgresql_using="gin", postgresql_ops={"search_text": "gin_trgm_ops"},
    )
    op.create_index("ix_medicines_therapeutic_class", "medicines", ["therapeutic_class"])
    op.create_index(
        "ix_medicine_presentations_ean_codes", "medicine_presentations", ["ean_codes"], postgresql_using="gin"
    )


def downgrade() -> None:
    op.drop_index("ix_medicine_presentations_ean_codes", table_name="medicine_presentations")
    op.drop_index("ix_medicines_therapeutic_class", table_name="medicines")
    op.drop_index("ix_medicines_search_text_trgm", table_name="medicines")
    op.drop_index("ix_medicines_search_name_trgm", table_name="medicines")
    op.drop_column("medicines", "search_text")
    op.drop_column("medicines", "search_name")
