import io
import re
from dataclasses import dataclass

import pdfplumber

from app.core.patient_leaflet_sections import PATIENT_LEAFLET_SECTIONS
from app.core.text_normalization import ACCENT_TRANSLATION
from app.exceptions.domain_exceptions import (
    LeafletPdfWithoutTextError,
    ProfessionalLeafletError,
    UnrecognizedLeafletError,
)

MAXIMUM_PAGES = 80
MINIMUM_TEXT_LENGTH = 200
MINIMUM_SECTIONS_FOUND = 5
OPTIONAL_WORDS = frozenset({"eu", "este", "deste"})
WORD_SEPARATOR = r"[\s,]+"
PROFESSIONAL_LEAFLET_MARKERS = ("resultados de eficacia", "caracteristicas farmacologicas", "posologia e modo de usar")
LEAFLET_END_MARKERS = re.compile(r"\n\s*(?:I{1,3}\s*[-–)]\s*)?dizeres\s+legais", re.IGNORECASE)
HYPHENATED_LINE_BREAK = re.compile(r"(\w)-\n(\w)")
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass(frozen=True)
class ExtractedSection:
    section_number: int
    content: str


def extract_pdf_text(pdf_content: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages[:MAXIMUM_PAGES]]
    text = CONTROL_CHARACTERS.sub("", "\n".join(pages))
    return HYPHENATED_LINE_BREAK.sub(r"\1\2", text)


def normalize_for_matching(text: str) -> str:
    return text.translate(ACCENT_TRANSLATION).lower()


def build_heading_pattern(title: str) -> re.Pattern:
    words = re.findall(r"\w+", normalize_for_matching(title))
    pattern = ""
    for index, word in enumerate(words):
        token = re.escape(word) if index == 0 else rf"{WORD_SEPARATOR}{re.escape(word)}"
        pattern += f"(?:{token})?" if word in OPTIONAL_WORDS else token
    return re.compile(rf"(?:^|\n)[ \t]*(?:\d{{1,2}}[ \t]*[.)\-–]?[ \t]*)?{pattern}[ \t]*\??")


HEADING_PATTERNS = {section.number: build_heading_pattern(section.title) for section in PATIENT_LEAFLET_SECTIONS}


def clean_section_text(text: str) -> str:
    lines = [line.strip() for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def locate_headings(normalized_text: str) -> list[tuple[int, int, int]]:
    headings = []
    search_from = 0
    for section in PATIENT_LEAFLET_SECTIONS:
        match = HEADING_PATTERNS[section.number].search(normalized_text, search_from)
        if match:
            headings.append((section.number, match.start(), match.end()))
            search_from = match.end()
    return headings


def segment_patient_leaflet(text: str) -> list[ExtractedSection]:
    normalized_text = normalize_for_matching(text)
    headings = locate_headings(normalized_text)
    if len(headings) < MINIMUM_SECTIONS_FOUND:
        if any(marker in normalized_text for marker in PROFESSIONAL_LEAFLET_MARKERS):
            raise ProfessionalLeafletError()
        raise UnrecognizedLeafletError()
    end_marker = LEAFLET_END_MARKERS.search(text, headings[-1][2])
    leaflet_end = end_marker.start() if end_marker else len(text)
    sections = []
    for index, (section_number, _, content_start) in enumerate(headings):
        content_end = headings[index + 1][1] if index + 1 < len(headings) else leaflet_end
        content = clean_section_text(text[content_start:content_end])
        if content:
            sections.append(ExtractedSection(section_number, content))
    return sections


def extract_patient_leaflet_sections(pdf_content: bytes) -> list[ExtractedSection]:
    text = extract_pdf_text(pdf_content)
    if len(text.strip()) < MINIMUM_TEXT_LENGTH:
        raise LeafletPdfWithoutTextError()
    return segment_patient_leaflet(text)
