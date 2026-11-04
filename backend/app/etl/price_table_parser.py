import math
import re
from decimal import Decimal
from pathlib import Path

import pandas as pd

from app.etl.csv_normalization import (
    ParsedCatalogFile,
    clean_text,
    normalize_registration_number,
    only_digits,
    parse_decimal_series,
    parse_yes_no,
)

FULL_REGISTRATION_LENGTH = 13
FACTORY_PRICE_PREFIX = "PF "
CONSUMER_PRICE_PREFIX = "PMC "
WITHOUT_TAXES_SUFFIX = "Sem Impostos"
EAN_COLUMNS = ("EAN 1", "EAN 2", "EAN 3")
PRESCRIPTION_LABEL_FIXES = {"Tarja Sem Tarja": "Sem tarja"}
DESCRIPTIVE_COLUMNS = [
    "CÓDIGO GGREM",
    "REGISTRO",
    "PRODUTO",
    "APRESENTAÇÃO",
    "SUBSTÂNCIA",
    "CNPJ",
    "LABORATÓRIO",
    "CLASSE TERAPÊUTICA",
    "TIPO DE PRODUTO (STATUS DO PRODUTO)",
    "REGIME DE PREÇO",
    "TARJA",
    "RESTRIÇÃO HOSPITALAR",
    *EAN_COLUMNS,
]


def normalize_column_name(column: str) -> str:
    return re.sub(r"\s+", " ", column.replace("\ufeff", "")).strip()


def normalize_tax_rate_label(label: str) -> str:
    return re.sub(r"\s*%\s*", "% ", label).strip()


def find_column(columns: list[str], prefix: str) -> str | None:
    return next((column for column in columns if column.startswith(prefix)), None)


def find_price_columns(columns: list[str], prefix: str) -> dict[str, str]:
    return {
        column: normalize_tax_rate_label(column[len(prefix):])
        for column in columns
        if column.startswith(prefix) and not column.endswith(WITHOUT_TAXES_SUFFIX)
    }


def build_price_maps(frame: pd.DataFrame, price_columns: dict[str, str]) -> list[dict[str, float]]:
    labels = list(price_columns.values())
    values = frame[list(price_columns)].apply(parse_decimal_series).to_numpy()
    return [
        {label: round(float(price), 2) for label, price in zip(labels, row) if not math.isnan(price)}
        for row in values
    ]


def to_decimal(value: float) -> Decimal | None:
    return None if pd.isna(value) else Decimal(str(round(float(value), 2)))


def normalize_prescription_label(value: object) -> str | None:
    label = clean_text(value)
    return PRESCRIPTION_LABEL_FIXES.get(label, label) if label else None


def split_medicine_registration(full_registration: str | None) -> str | None:
    if full_registration is None or len(full_registration) != FULL_REGISTRATION_LENGTH:
        return None
    return normalize_registration_number(full_registration[:9])


def build_presentation_record(row: dict) -> dict:
    full_registration = only_digits(row["REGISTRO"])
    ean_codes = [code for code in (only_digits(row[column]) for column in EAN_COLUMNS) if code]
    active_ingredient = clean_text(row["SUBSTÂNCIA"])
    return {
        "ggrem_code": only_digits(row["CÓDIGO GGREM"]),
        "registration_number": full_registration,
        "medicine_registration_number": split_medicine_registration(full_registration),
        "product_name": clean_text(row["PRODUTO"]) or "",
        "presentation": clean_text(row["APRESENTAÇÃO"]),
        "active_ingredient": active_ingredient.lower() if active_ingredient else None,
        "laboratory_cnpj": only_digits(row["CNPJ"]),
        "laboratory_name": clean_text(row["LABORATÓRIO"]),
        "therapeutic_class": clean_text(row["CLASSE TERAPÊUTICA"]),
        "product_type": clean_text(row["TIPO DE PRODUTO (STATUS DO PRODUTO)"]),
        "price_regime": clean_text(row["REGIME DE PREÇO"]),
        "prescription_label": normalize_prescription_label(row["TARJA"]),
        "ean_codes": list(dict.fromkeys(ean_codes)),
        "hospital_restricted": parse_yes_no(row["RESTRIÇÃO HOSPITALAR"]),
        "marketed": parse_yes_no(row["marketed"]),
        "factory_price_without_taxes": to_decimal(row["factory_price_without_taxes"]),
        "consumer_price_without_taxes": to_decimal(row["consumer_price_without_taxes"]),
        "factory_prices": row["factory_prices"],
        "consumer_prices": row["consumer_prices"],
    }


def parse_price_table(path: Path) -> ParsedCatalogFile:
    frame = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    frame.columns = [normalize_column_name(column) for column in frame.columns]
    columns = list(frame.columns)
    marketed_column = find_column(columns, "COMERCIALIZAÇÃO")
    descriptive = frame[DESCRIPTIVE_COLUMNS].copy()
    descriptive["marketed"] = frame[marketed_column] if marketed_column else ""
    descriptive["factory_price_without_taxes"] = parse_decimal_series(frame[f"{FACTORY_PRICE_PREFIX}{WITHOUT_TAXES_SUFFIX}"])
    descriptive["consumer_price_without_taxes"] = parse_decimal_series(frame[f"{CONSUMER_PRICE_PREFIX}{WITHOUT_TAXES_SUFFIX}"])
    descriptive["factory_prices"] = build_price_maps(frame, find_price_columns(columns, FACTORY_PRICE_PREFIX))
    descriptive["consumer_prices"] = build_price_maps(frame, find_price_columns(columns, CONSUMER_PRICE_PREFIX))
    records = [build_presentation_record(row) for row in descriptive.to_dict("records")]
    unique_records = {record["ggrem_code"]: record for record in records if record["ggrem_code"]}
    return ParsedCatalogFile(records=list(unique_records.values()), rows_read=len(frame))
