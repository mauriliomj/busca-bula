from pathlib import Path

import pandas as pd

from app.etl.csv_normalization import (
    ParsedCatalogFile,
    clean_text,
    normalize_registration_series,
    only_digits,
    parse_date_series,
    timestamp_to_datetime,
)

LEAFLET_INDEX_COLUMNS = [
    "bulario_product_id",
    "product_name",
    "registration_number",
    "regulatory_category_code",
    "process_number",
    "company_cnpj",
    "company_name",
    "document_id",
    "expedient_number",
    "published_at",
    "transaction_number",
    "source_updated_at",
]

PUBLICATION_DATE_FORMAT = "%m/%d/%Y %H:%M:%S"


def build_leaflet_record(row: dict) -> dict:
    return {
        "registration_number": row["normalized_registration_number"],
        "bulario_product_id": only_digits(row["bulario_product_id"]),
        "product_name": clean_text(row["product_name"]) or "",
        "process_number": clean_text(row["process_number"]),
        "company_cnpj": only_digits(row["company_cnpj"]),
        "company_name": clean_text(row["company_name"]),
        "document_id": only_digits(row["document_id"]),
        "expedient_number": clean_text(row["expedient_number"]),
        "published_at": timestamp_to_datetime(row["published_at"]),
    }


def parse_leaflet_index(path: Path) -> ParsedCatalogFile:
    frame = pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
        header=None,
        names=LEAFLET_INDEX_COLUMNS,
        dtype=str,
        keep_default_na=False,
    )
    rows_read = len(frame)
    frame["normalized_registration_number"] = normalize_registration_series(frame["registration_number"])
    frame = frame[frame["normalized_registration_number"].notna() & frame["bulario_product_id"].ne("")].copy()
    frame["published_at"] = parse_date_series(frame["published_at"], PUBLICATION_DATE_FORMAT)
    frame = frame.drop_duplicates("normalized_registration_number", keep="last")
    records = [build_leaflet_record(row) for row in frame.to_dict("records")]
    return ParsedCatalogFile(records=records, rows_read=rows_read)
