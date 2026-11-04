from pathlib import Path

import pandas as pd

from app.etl.csv_normalization import (
    ParsedCatalogFile,
    clean_text,
    normalize_registration_series,
    parse_date_series,
    parse_month_year,
    split_document_and_name,
    timestamp_to_date,
)

ACTIVE_STATUS = "Ativo"

REGULATORY_CATEGORY_FIXES = {
    "FITOTER?PICO": "Fitoterápico",
    "GASES MEDICI": "Gases medicinais",
    "PRODUTO DE T": "Produto de terapia avançada",
}


def normalize_regulatory_category(value: object) -> str | None:
    category = clean_text(value)
    if category is None:
        return None
    category = REGULATORY_CATEGORY_FIXES.get(category.upper(), category)
    return category[0].upper() + category[1:].lower()


def build_medicine_record(row: dict) -> dict:
    holder_cnpj, holder_name = split_document_and_name(row["EMPRESA_DETENTORA_REGISTRO"])
    active_ingredient = clean_text(row["PRINCIPIO_ATIVO"])
    return {
        "registration_number": row["registration_number"],
        "product_name": clean_text(row["NOME_PRODUTO"]) or "",
        "active_ingredient": active_ingredient.lower() if active_ingredient else None,
        "therapeutic_class": clean_text(row["CLASSE_TERAPEUTICA"]),
        "regulatory_category": normalize_regulatory_category(row["CATEGORIA_REGULATORIA"]),
        "holder_cnpj": holder_cnpj,
        "holder_name": holder_name,
        "process_number": clean_text(row["NUMERO_PROCESSO"]),
        "is_active": bool(row["is_active"]),
        "registration_expires_on": parse_month_year(row["DATA_VENCIMENTO_REGISTRO"]),
        "process_finished_on": timestamp_to_date(row["process_finished_on"]),
    }


def parse_medicine_catalog(path: Path) -> ParsedCatalogFile:
    frame = pd.read_csv(path, sep=";", encoding="latin-1", dtype=str, keep_default_na=False)
    rows_read = len(frame)
    frame["registration_number"] = normalize_registration_series(frame["NUMERO_REGISTRO_PRODUTO"])
    frame = frame[frame["registration_number"].notna()].copy()
    frame["is_active"] = frame["SITUACAO_REGISTRO"].str.strip().eq(ACTIVE_STATUS)
    frame["process_finished_on"] = parse_date_series(frame["DATA_FINALIZACAO_PROCESSO"], "%d/%m/%Y")
    frame = frame.sort_values(
        ["registration_number", "is_active", "process_finished_on"],
        ascending=[True, False, False],
        na_position="last",
    ).drop_duplicates("registration_number")
    records = [build_medicine_record(row) for row in frame.to_dict("records")]
    return ParsedCatalogFile(records=records, rows_read=rows_read)
