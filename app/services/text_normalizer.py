import re
import unicodedata


# =========================
# Text normalization
# =========================
def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = strip_accents(text)
    text = re.sub(r"\s+", " ", text)
    return text
