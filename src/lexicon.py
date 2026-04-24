"""Lexicon V2: whitelist POS/NEG cho câu ngắn + teencode + emoji map.

Dùng bởi `normalize.py` (teencode/emoji) và `step3_sentiment.py` (lexicon shortcut).
"""

# ---------------------------------------------------------------------------
# 1. Teencode / viết tắt phổ biến trong comment YouTube VN
# ---------------------------------------------------------------------------
TEENCODE_MAP = {
    "ko": "không", "k": "không", "kh": "không", "hk": "không", "khong": "không",
    "kg": "không", "kgo": "không",
    "dc": "được", "đc": "được", "duoc": "được",
    "wa": "quá", "qa": "quá", "qua": "quá",
    "j": "gì", "jj": "gì",
    "ntn": "như thế nào",
    "ah": "à", "ak": "à", "a": "à",
    "mn": "mọi người",
    "mik": "mình", "mh": "mình", "m": "mình",
    "trc": "trước",
    "bt": "biết",
    "bik": "biết",
    "ng": "người",
    "vs": "với",
    "z": "vậy", "zậy": "vậy",
    "r": "rồi", "rùi": "rồi",
    "thik": "thích", "thick": "thích",
    "iu": "yêu",
    "cute": "dễ thương",
    "tks": "cảm ơn", "thanks": "cảm ơn", "thank": "cảm ơn",
    "ok": "ổn", "oke": "ổn", "okie": "ổn",
    # intensifier có sentiment, giữ nguyên ý nghĩa nhưng map về dạng có dấu/đầy đủ
    "vcl": "vãi", "vl": "vãi", "sml": "vãi",
}

# ---------------------------------------------------------------------------
# 2. Emoji → token sentiment (giữ tín hiệu thay vì xoá)
# ---------------------------------------------------------------------------
EMOJI_POS = {
    "👍", "❤", "❤️", "😍", "🥰", "🌷", "🌹", "🔥", "💯", "👏",
    "💖", "💗", "💕", "😘", "🤩", "🥳", "✨", "🌟", "⭐", "👌",
    "💪", "🙌", "🫶", "💝",
}
EMOJI_NEG = {
    "👎", "😡", "🤬", "💩", "😤", "😠", "🤮", "🤢", "😒", "🙄",
    "😞", "😔", "😟", "😢", "😭", "💔",
}
EMOJI_FUNNY = {
    "😂", "🤣", "😅", "😆", "😹",
}

# ---------------------------------------------------------------------------
# 3. Lexicon shortcut cho câu ngắn (≤ 5 token)
# ---------------------------------------------------------------------------
# Lưu ý: so khớp sau khi đã normalize (lowercase, gộp dấu cách, có thể chưa có dấu).
LEXICON_POS = {
    # có dấu
    "hay", "quá hay", "hay quá", "tuyệt vời", "xuất sắc", "đỉnh", "quá đỉnh",
    "mê", "thích", "cám ơn", "cảm ơn", "dễ thương", "đẹp", "tuyệt", "chất",
    "ngon", "ổn", "ok", "oke", "tốt", "hay vậy", "đỉnh quá", "tuyệt cú mèo",
    "yêu", "yêu quá", "quá tuyệt", "quá đẹp", "đẹp quá", "ngon quá", "tốt quá",
    "thích quá", "mê quá", "hay wa", "hay ghê", "hay dữ",
    # không dấu (telex)
    "hay qua", "tuyet voi", "cam on", "thich", "dep", "ngon", "tuyet",
    "tot", "de thuong", "xuat sac", "dinh", "qua dinh", "yeu",
}

LEXICON_NEG = {
    # có dấu
    "tệ", "dở", "chán", "thất vọng", "ghét", "kém", "nhảm", "rác", "ngu",
    "dở tệ", "chán quá", "tệ quá", "dở quá", "ghét quá", "kém quá",
    "vớ vẩn", "nhảm nhí", "thua", "thất bại",
    # không dấu (telex)
    "te", "do", "chan", "that vong", "ghet", "kem", "nham", "rac",
    "do te", "vo van", "nham nhi",
}
