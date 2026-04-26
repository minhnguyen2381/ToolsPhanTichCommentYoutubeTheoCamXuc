"""Lexicon V3: whitelist POS/NEG + teencode + emoji + domain keywords.

Cải tiến V3 (xem `solutions/v3_sentiment/GIAI_PHAP_V3.md`):
- Thêm từ lóng khen kiểu Nam Bộ (dữ, ghê, điên) vào LEXICON_POS.
- Thêm HISTORY_DOMAIN_KEYWORDS để phát hiện domain Tam Quốc / lịch sử.
- Thêm QUESTION_PATTERNS để phát hiện câu hỏi.
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
# 3. Lexicon shortcut cho câu ngắn (≤ 8 token — V3 mở rộng từ 5)
# ---------------------------------------------------------------------------
# Lưu ý: so khớp sau khi đã normalize (lowercase, gộp dấu cách, có thể chưa có dấu).
LEXICON_POS = {
    # --- V2 gốc ---
    "hay", "quá hay", "hay quá", "tuyệt vời", "xuất sắc", "đỉnh", "quá đỉnh",
    "mê", "thích", "cám ơn", "cảm ơn", "dễ thương", "đẹp", "tuyệt", "chất",
    "ngon", "ổn", "ok", "oke", "tốt", "hay vậy", "đỉnh quá", "tuyệt cú mèo",
    "yêu", "yêu quá", "quá tuyệt", "quá đẹp", "đẹp quá", "ngon quá", "tốt quá",
    "thích quá", "mê quá", "hay wa", "hay ghê", "hay dữ",
    # không dấu (telex)
    "hay qua", "tuyet voi", "cam on", "thich", "dep", "ngon", "tuyet",
    "tot", "de thuong", "xuat sac", "dinh", "qua dinh", "yeu",
    # --- V3: từ lóng khen kiểu Nam Bộ / cảm thán ---
    "dữ", "ghê", "điên", "kinh", "sốc",
    "quá dữ", "dữ quá", "ghê quá", "quá ghê",
    "điên quá", "quá điên", "kinh quá", "quá kinh",
    "sốc quá", "dữ dội", "hay quá b", "hay quá ạ",
    "hấp dẫn", "bổ ích", "hay lắm", "hay dã man",
    "hay quá trời", "tuyệt đỉnh", "rất tuyệt đỉnh",
    "hay lắm ạ", "hay lắm bạn", "hay quá bạn", "hay quá bạn ơi",
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

# ---------------------------------------------------------------------------
# 4. V3: Domain keywords — phát hiện chủ đề lịch sử / Tam Quốc
# ---------------------------------------------------------------------------
# Khi comment chứa ≥ 2 keyword → domain = history → nâng ngưỡng NEG.
HISTORY_DOMAIN_KEYWORDS = {
    # Tam Quốc — nhân vật
    "quan vũ", "quan công", "quan vân trường", "quan nhị ca",
    "tào tháo", "lưu bị", "trương phi", "triệu vân", "triệu tử long",
    "lữ bố", "lã bố", "gia cát lượng", "khổng minh",
    "tôn kiên", "tôn quyền", "mã siêu", "hoàng trung", "hứa chử",
    "điển vi", "hạ hầu đôn", "trương liêu", "hoa hùng",
    "nhan lương", "văn xú", "lữ mông", "lã mông",
    "bàng đức", "ngụy diên", "tôn sách", "tào nhân", "tào hồng",
    # Tam Quốc — thuật ngữ
    "tam quốc", "ngũ hổ tướng", "kinh châu", "xích bích",
    "thanh long đao", "phương thiên", "hồ quảng", "hát bội",
    "cải lương", "tuồng", "hát bộ",
    # Lịch sử VN — để không gán NEG cho bàn luận so sánh
    "trần hưng đạo", "hưng đạo vương", "quang trung", "nguyễn huệ",
    "lê lợi", "lý thường kiệt", "ngô quyền",
}

# ---------------------------------------------------------------------------
# 5. V3: Question patterns — phát hiện câu hỏi
# ---------------------------------------------------------------------------
# Câu hỏi thường không mang sentiment NEG. Dùng để post-process.
QUESTION_PATTERNS = {
    "cho hỏi", "cho mình hỏi", "xin hỏi", "hỏi",
    "tại sao", "vì sao", "sao lại", "sao không",
    "là gì", "nghĩa là gì", "có nghĩa là",
    "ai biết", "ai đó", "bạn nào biết",
    "ở đâu", "khi nào", "bao giờ", "làm sao",
    "thế nào", "như thế nào", "ra sao",
    "có ai", "có không", "được không", "phải không",
}

