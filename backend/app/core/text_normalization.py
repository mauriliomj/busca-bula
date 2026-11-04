import re

ACCENTED_CHARACTERS = "ÁÀÂÃÄáàâãäÉÈÊËéèêëÍÌÎÏíìîïÓÒÔÕÖóòôõöÚÙÛÜúùûüÇçÑñ"
UNACCENTED_CHARACTERS = "AAAAAaaaaaEEEEeeeeIIIIiiiiOOOOOoooooUUUUuuuuCcNn"

ACCENT_TRANSLATION = str.maketrans(ACCENTED_CHARACTERS, UNACCENTED_CHARACTERS)


def normalize_search_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.translate(ACCENT_TRANSLATION).lower()).strip()


def split_search_terms(text: str) -> list[str]:
    return [term for term in normalize_search_text(text).split(" ") if term]
