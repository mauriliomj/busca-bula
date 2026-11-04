import re
from pathlib import Path

import pandas as pd

from app.core.patient_leaflet_sections import SECTION_TITLES_BY_NUMBER
from app.etl.csv_normalization import ParsedCatalogFile, clean_text, normalize_registration_series

DATASET_COLUMNS = ["registro", "nome_produto", "expediente", "secao_id", "resposta"]
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
TRAILING_PART_MARKER = re.compile(r"\n\s*I{1,3}\s*[-–]?\s*$")


def clean_section_content(value: object) -> str:
    text = CONTROL_CHARACTERS.sub("", str(value or "").replace("\r\n", "\n").replace("\r", "\n"))
    lines = [line.rstrip() for line in text.split("\n")]
    return TRAILING_PART_MARKER.sub("", "\n".join(lines).strip()).strip()


def build_document_record(registration_number: str, rows: pd.DataFrame) -> dict | None:
    sections = [
        {"section_number": int(row.secao_id), "content": clean_section_content(row.resposta)}
        for row in rows.sort_values("secao_id").itertuples()
        if int(row.secao_id) in SECTION_TITLES_BY_NUMBER
    ]
    sections = [section for section in sections if section["content"]]
    if not sections:
        return None
    first_row = rows.iloc[0]
    return {
        "registration_number": registration_number,
        "product_name": clean_text(first_row["nome_produto"]) or "",
        "expedient_number": clean_text(first_row["expediente"]),
        "sections": sections,
    }


def parse_chatbulario_dataset(paths: list[Path]) -> ParsedCatalogFile:
    frame = pd.concat([pd.read_parquet(path, columns=DATASET_COLUMNS) for path in paths], ignore_index=True)
    rows_read = len(frame)
    frame["registration_number"] = normalize_registration_series(frame["registro"])
    frame = frame[frame["registration_number"].notna()]
    frame = frame.drop_duplicates(["registration_number", "secao_id"], keep="first")
    records = [
        record
        for registration_number, rows in frame.groupby("registration_number", sort=True)
        if (record := build_document_record(registration_number, rows)) is not None
    ]
    return ParsedCatalogFile(records=records, rows_read=rows_read)
