import re
import unicodedata


def normalize_text(text: str) -> str:
    """Chuẩn hoá tên phường/đường để so khớp ILIKE trên DB."""
    if not text:
        return ""

    text = unicodedata.normalize("NFC", text)
    text = text.lower()

    replace_words = [
        "thành phố", "tp.",
        "quận", "huyện",
        "phường", "xã",
        "thị trấn",
        "đường", "đ."
    ]

    for w in replace_words:
        text = text.replace(w, " ")

    text = re.sub(r"\s+", " ", text).strip()

    return text
