import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import pandas as pd

REGISTRATION_LENGTH = 9
MINIMUM_REGISTRATION_LENGTH = 8
EMPTY_MARKERS = frozenset({"", "-", "- (*)", "NaN", "nan"})


@dataclass
class ParsedCatalogFile:
    records: list[dict] = field(default_factory=list)
    rows_read: int = 0


def clean_text(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return None if text in EMPTY_MARKERS else text


def only_digits(value: object) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    digits = re.sub(r"\D", "", text)
    return digits or None


def normalize_registration_number(value: object) -> str | None:
    digits = only_digits(value)
    if digits is None or not MINIMUM_REGISTRATION_LENGTH <= len(digits) <= REGISTRATION_LENGTH:
        return None
    return digits.zfill(REGISTRATION_LENGTH)


def parse_brazilian_decimal(value: object) -> Decimal | None:
    text = clean_text(value)
    if text is None:
        return None
    try:
        return Decimal(text.replace(".", "").replace(",", "."))
    except InvalidOperation:
        return None


def parse_date(value: object, date_format: str) -> date | None:
    parsed = parse_datetime(value, date_format)
    return parsed.date() if parsed else None


def parse_datetime(value: object, date_format: str) -> datetime | None:
    text = clean_text(value)
    if text is None:
        return None
    try:
        return datetime.strptime(text, date_format)
    except ValueError:
        return None


def parse_month_year(value: object) -> date | None:
    digits = only_digits(value)
    if digits is None or len(digits) != 6:
        return None
    month, year = int(digits[:2]), int(digits[2:])
    if not 1 <= month <= 12:
        return None
    return date(year, month, 1)


def parse_yes_no(value: object) -> bool | None:
    text = (clean_text(value) or "").lower()
    if text == "sim":
        return True
    if text in {"não", "nao"}:
        return False
    return None


def split_document_and_name(value: object) -> tuple[str | None, str | None]:
    text = clean_text(value)
    if text is None:
        return None, None
    document, separator, name = text.partition(" - ")
    if separator and document.isdigit():
        return document, clean_text(name)
    return None, text


def normalize_registration_series(values: pd.Series) -> pd.Series:
    digits = values.fillna("").astype(str).str.replace(r"\D", "", regex=True)
    valid_length = digits.str.len().between(MINIMUM_REGISTRATION_LENGTH, REGISTRATION_LENGTH)
    return digits.str.zfill(REGISTRATION_LENGTH).where(valid_length)


def parse_decimal_series(values: pd.Series) -> pd.Series:
    normalized = (
        values.fillna("")
        .astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(normalized, errors="coerce")


def parse_date_series(values: pd.Series, date_format: str) -> pd.Series:
    return pd.to_datetime(values.fillna("").astype(str).str.strip(), format=date_format, errors="coerce")


def timestamp_to_date(value: object) -> date | None:
    return None if pd.isna(value) else value.date()


def timestamp_to_datetime(value: object) -> datetime | None:
    return None if pd.isna(value) else value.to_pydatetime()
