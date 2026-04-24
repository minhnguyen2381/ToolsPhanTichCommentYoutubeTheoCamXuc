"""Tiền xử lý V2 cho comment YouTube tiếng Việt.

So với V1 (`clean_text` cũ trong step3): giữ lại emoji-as-token, dấu câu cảm thán,
chuẩn hoá teencode + ký tự lặp, tuỳ chọn phục hồi dấu.
"""
import re
import unicodedata
from typing import Optional

from lexicon import EMOJI_POS, EMOJI_NEG, EMOJI_FUNNY, TEENCODE_MAP

_URL_RE = re.compile(r"http\S+|www\.\S+")
_HTML_RE = re.compile(r"<[^>]+>")
_ELONG_RE = re.compile(r"(.)\1{2,}")  # ký tự lặp ≥3 lần
_MULTI_SPACE_RE = re.compile(r"\s+")
# Giữ chữ + số + khoảng trắng + . ! ? , và emoji (emoji được xử lý trước)
_KEEP_RE = re.compile(r"[^\wÀ-ỹ\s\.\!\?\,]", flags=re.UNICODE)

_VIET_DIACRITIC_RE = re.compile(r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", re.IGNORECASE)


def map_emoji(text: str) -> str:
    """Thay emoji bằng token ' tích_cực ' / ' tiêu_cực ' / ' hài_hước '."""
    out = []
    for ch in text:
        if ch in EMOJI_POS:
            out.append(" tích_cực ")
        elif ch in EMOJI_NEG:
            out.append(" tiêu_cực ")
        elif ch in EMOJI_FUNNY:
            out.append(" hài_hước ")
        else:
            out.append(ch)
    return "".join(out)


def map_teencode(text: str) -> str:
    """Thay từng token teencode bằng dạng đầy đủ."""
    tokens = text.split()
    out = []
    for tk in tokens:
        # tách dấu câu trailing để khớp dictionary
        m = re.match(r"^(.*?)([\.\!\?\,]*)$", tk)
        core, tail = (m.group(1), m.group(2)) if m else (tk, "")
        rep = TEENCODE_MAP.get(core, core)
        out.append(rep + tail)
    return " ".join(out)


def collapse_elongation(text: str) -> str:
    """`hayyyy` → `hayy`, `quááá` → `quáá` (giữ tối đa 2 lần)."""
    return _ELONG_RE.sub(lambda m: m.group(1) * 2, text)


def diacritic_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 1.0
    diacritics = _VIET_DIACRITIC_RE.findall(text)
    return len(diacritics) / len(letters)


_DIACRITIC_RESTORER = None


def restore_diacritics(text: str) -> str:
    """Tuỳ chọn — gọi mô hình phục hồi dấu nếu text có vẻ telex/no-tone.

    Lazy-load mô hình ở lần gọi đầu. Nếu không có internet/transformers thì trả nguyên.
    """
    global _DIACRITIC_RESTORER
    if _DIACRITIC_RESTORER is None:
        try:
            from transformers import pipeline
            _DIACRITIC_RESTORER = pipeline(
                "text2text-generation",
                model="bmd1905/vietnamese-correction",
            )
        except Exception as e:
            print(f"[!] Không tải được mô hình phục hồi dấu: {e}")
            _DIACRITIC_RESTORER = False  # đánh dấu đã thử và fail
    if not _DIACRITIC_RESTORER:
        return text
    try:
        out = _DIACRITIC_RESTORER(text, max_length=256)[0]["generated_text"]
        return out
    except Exception:
        return text


def normalize(text: str, use_diacritic_restore: bool = False) -> str:
    """Pipeline normalize hoàn chỉnh — không tokenize.

    Trả về chuỗi đã sạch, sẵn sàng cho `underthesea.word_tokenize`.
    """
    if not isinstance(text, str):
        return ""
    t = unicodedata.normalize("NFC", text)
    t = _URL_RE.sub(" ", t)
    t = _HTML_RE.sub(" ", t)
    t = map_emoji(t)
    t = t.lower()
    t = _KEEP_RE.sub(" ", t)
    t = collapse_elongation(t)
    t = _MULTI_SPACE_RE.sub(" ", t).strip()
    if not t:
        return ""
    t = map_teencode(t)
    if use_diacritic_restore and diacritic_ratio(t) < 0.15:
        t = restore_diacritics(t)
    t = _MULTI_SPACE_RE.sub(" ", t).strip()
    return t


def tokenize_for_phobert(normalized_text: str) -> str:
    """Tokenize bằng underthesea theo định dạng PhoBERT mong đợi."""
    if not normalized_text:
        return ""
    from underthesea import word_tokenize
    return word_tokenize(normalized_text, format="text")
