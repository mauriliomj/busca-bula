from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "3e8c5a1f7b62"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "medicines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("registration_number", sa.String(9), nullable=False, unique=True),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("active_ingredient", sa.Text(), nullable=True),
        sa.Column("therapeutic_class", sa.String(255), nullable=True),
        sa.Column("regulatory_category", sa.String(60), nullable=True),
        sa.Column("holder_cnpj", sa.String(14), nullable=True),
        sa.Column("holder_name", sa.String(255), nullable=True),
        sa.Column("process_number", sa.String(30), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("registration_expires_on", sa.Date(), nullable=True),
        sa.Column("process_finished_on", sa.Date(), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "leaflets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("registration_number", sa.String(9), nullable=False, unique=True),
        sa.Column("bulario_product_id", sa.String(20), nullable=False),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("process_number", sa.String(30), nullable=True),
        sa.Column("company_cnpj", sa.String(14), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("document_id", sa.String(20), nullable=True),
        sa.Column("expedient_number", sa.String(20), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "medicine_presentations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ggrem_code", sa.String(20), nullable=False, unique=True),
        sa.Column("registration_number", sa.String(13), nullable=True),
        sa.Column("medicine_registration_number", sa.String(9), nullable=True, index=True),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("presentation", sa.Text(), nullable=True),
        sa.Column("active_ingredient", sa.Text(), nullable=True),
        sa.Column("laboratory_cnpj", sa.String(14), nullable=True),
        sa.Column("laboratory_name", sa.String(255), nullable=True),
        sa.Column("therapeutic_class", sa.String(255), nullable=True),
        sa.Column("product_type", sa.String(60), nullable=True),
        sa.Column("price_regime", sa.String(30), nullable=True),
        sa.Column("prescription_label", sa.String(60), nullable=True),
        sa.Column("ean_codes", postgresql.ARRAY(sa.String(14)), nullable=False),
        sa.Column("hospital_restricted", sa.Boolean(), nullable=True),
        sa.Column("marketed", sa.Boolean(), nullable=True),
        sa.Column("factory_price_without_taxes", sa.Numeric(12, 2), nullable=True),
        sa.Column("consumer_price_without_taxes", sa.Numeric(12, 2), nullable=True),
        sa.Column("factory_prices", postgresql.JSONB(), nullable=False),
        sa.Column("consumer_prices", postgresql.JSONB(), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "catalog_imports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(30), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rows_read", sa.Integer(), nullable=True),
        sa.Column("rows_loaded", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("catalog_imports")
    op.drop_table("medicine_presentations")
    op.drop_table("leaflets")
    op.drop_table("medicines")
