"""Lexicon keyword Tam Quốc — dùng cho khảo sát Google (step6) và tái sử dụng sau này.

Mỗi entry: canonical (nhãn VI), category, patterns (vi/en/zh, lowercase khi match).
"""

from __future__ import annotations

# Seed keywords tìm kiếm gốc — loại khỏi top list vì đã là query chính.
SEED_CANONICALS = {
    "Quan Công", "Quan Vũ", "Quan Thánh", "Quan Thánh Đế Quân", "Quan Vân Trường",
    "Tam quốc", "Tam quốc diễn nghĩa",
}

# Anchor Tam quốc — mỗi query search phải chứa ít nhất một anchor.
TAMQUOC_ANCHORS = (
    "tam quốc",
    "tam quoc",
    "tam quốc diễn nghĩa",
    "three kingdoms",
    "romance of the three kingdoms",
    "三国演义",
    "三国",
)

# Query ghép cho step6 — đa dạng chủ đề, luôn gắn anchor Tam quốc.
GOOGLE_SEARCH_QUERIES: list[str] = [
    # Quan Vũ (spec gốc)
    "Quan Vũ Tam quốc",
    "Quan Công Tam quốc diễn nghĩa",
    "Quan Thánh Tam quốc",
    "Quan Vân Trường Tam quốc",
    "关云长 三国",
    "Guan Yu Three Kingdoms",
    # Nhân vật chính
    "Lưu Bị Tam quốc",
    "Tào Tháo Tam quốc",
    "Gia Cát Lượng Tam quốc",
    "Triệu Vân Tam quốc",
    "Lữ Bố Tam quốc",
    # Sự kiện / địa danh
    "Trận Xích Bích Tam quốc",
    "Trường Bản Tam quốc",
    "Kinh Châu Tam quốc",
    "Tam quốc Mạch Thành",
    # Khái niệm / văn hóa / media
    "Tam quốc diễn nghĩa",
    "Ngũ hổ tướng Tam quốc",
    "Tam quốc phim",
    "Tam quốc game",
    "Tam quốc cải lương",
    # Tín ngưỡng Quan
    "Quan Thánh Đế Quân Tam quốc",
    "thờ Quan Công Tam quốc",
]

# (canonical, category, patterns)
_RAW_ENTRIES: list[tuple[str, str, list[str]]] = [
    # ── nhân_vật ──
    ("Lưu Bị", "nhân_vật", ["lưu bị", "liu bei", "刘备", "liú bèi"]),
    ("Trương Phi", "nhân_vật", ["trương phi", "zhang fei", "张飞"]),
    ("Tào Tháo", "nhân_vật", ["tào tháo", "cao cao", "曹操"]),
    ("Triệu Vân", "nhân_vật", ["triệu vân", "triệu tử long", "zhao yun", "赵云", "赵子龙"]),
    ("Gia Cát Lượng", "nhân_vật", ["gia cát lượng", "khổng minh", "zhuge liang", "诸葛亮"]),
    ("Lữ Bố", "nhân_vật", ["lữ bố", "lã bố", "lu bu", "吕布"]),
    ("Điêu Thuyền", "nhân_vật", ["điêu thuyền", "diao chan", "貂蝉"]),
    ("Đổng Trác", "nhân_vật", ["đổng trác", "dong zhuo", "董卓"]),
    ("Tôn Quyền", "nhân_vật", ["tôn quyền", "sun quan", "孙权"]),
    ("Chu Du", "nhân_vật", ["chu du", "周瑜"]),
    ("Viên Thiệu", "nhân_vật", ["viên thiệu", "yuan shao", "袁绍"]),
    ("Tư Mã Ý", "nhân_vật", ["tư mã ý", "simayi", "司马懿"]),
    ("Mã Siêu", "nhân_vật", ["mã siêu", "ma chao", "马超"]),
    ("Hoàng Trung", "nhân_vật", ["hoàng trung", "huang zhong", "黄忠"]),
    ("Lục Tốn", "nhân_vật", ["lục tốn", "lu xun", "陆逊"]),
    ("Hứa Chử", "nhân_vật", ["hứa chử", "xu chu", "许褚"]),
    ("Điển Vi", "nhân_vật", ["điển vi", "dian wei", "典韦"]),
    ("Trương Liêu", "nhân_vật", ["trương liêu", "zhang liao", "张辽"]),
    ("Bàng Thống", "nhân_vật", ["bàng thống", "pang tong", "庞统"]),
    ("Pháp Chính", "nhân_vật", ["pháp chính", "fa zheng", "法正"]),
    ("Cam Ninh", "nhân_vật", ["cam ninh", "gan ning", "甘宁"]),
    ("Thái Sử Từ", "nhân_vật", ["thái sử từ", "taishi ci", "太史慈"]),
    ("Lã Mông", "nhân_vật", ["lã mông", "lữ mông", "lu meng", "吕蒙"]),
    ("Nhan Lương", "nhân_vật", ["nhan lương", "yan liang", "颜良"]),
    ("Văn Xú", "nhân_vật", ["văn xú", "wen chou", "文丑"]),
    ("Hoa Hùng", "nhân_vật", ["hoa hùng", "hua xiong", "华雄"]),
    ("Hoa Đà", "nhân_vật", ["hoa đà", "hua tuo", "华佗"]),
    ("Quan Bình", "nhân_vật", ["quan bình", "guan ping", "关平"]),
    ("Quan Hưng", "nhân_vật", ["quan hưng", "guan xing", "关兴"]),
    ("Bàng Đức", "nhân_vật", ["bàng đức", "pang de", "庞德"]),
    ("Ngụy Diên", "nhân_vật", ["ngụy diên", "wei yan", "魏延"]),
    ("Tôn Kiên", "nhân_vật", ["tôn kiên", "sun jian", "孙坚"]),
    ("Tôn Sách", "nhân_vật", ["tôn sách", "sun ce", "孙策"]),
    ("Tào Nhân", "nhân_vật", ["tào nhân", "cao ren", "曹仁"]),
    ("Tào Hồng", "nhân_vật", ["tào hồng", "cao hong", "曹洪"]),
    ("Hạ Hầu Đôn", "nhân_vật", ["hạ hầu đôn", "xiahou dun", "夏侯惇"]),
    ("Lý Túc", "nhân_vật", ["lý túc", "li su", "李肃"]),
    ("Nezha", "nhân_vật", ["ne zha", "nezha", "哪吒"]),
    # ── địa_danh_sự_kiện ──
    ("Kinh Châu", "địa_danh_sự_kiện", ["kinh châu", "jingzhou", "荆州"]),
    ("Xích Bích", "địa_danh_sự_kiện", ["xích bích", "chi bi", "red cliff", "赤壁"]),
    ("Mạch Thành", "địa_danh_sự_kiện", ["mạch thành", "fan castle", "麦城", "mai thành"]),
    ("Trường Bản", "địa_danh_sự_kiện", ["trường bản", "chang ban", "长坂坡"]),
    ("Đào Viên", "địa_danh_sự_kiện", ["đào viên", "taoyuan", "桃园"]),
    ("Phượng Nghi Đình", "địa_danh_sự_kiện", ["phượng nghi đình", "phoenix pavilion"]),
    ("Ngọa Long", "địa_danh_sự_kiện", ["ngọa long", "wo long", "卧龙"]),
    ("Khổng Thành Kế", "địa_danh_sự_kiện", ["khổng thành kế", "empty city"]),
    ("Bạch Đế Thành", "địa_danh_sự_kiện", ["bạch đế thành", "white emperor"]),
    ("Hán Trung", "địa_danh_sự_kiện", ["hán trung", "han zhong", "汉中"]),
    ("Ngũ Trượng Nguyên", "địa_danh_sự_kiện", ["ngũ trượng nguyên", "wuzhang plains"]),
    ("Quan Độ", "địa_danh_sự_kiện", ["quan độ", "guan du", "官渡"]),
    ("Hoa Dung", "địa_danh_sự_kiện", ["hoa dung", "sliding through"]),
    ("Thục Hán", "địa_danh_sự_kiện", ["thục hán", "shu han", "蜀汉"]),
    ("Ngụy Quốc", "địa_danh_sự_kiện", ["ngụy quốc", "wei kingdom", "魏国"]),
    ("Đông Ngô", "địa_danh_sự_kiện", ["đông ngô", "dong wu", "东吴"]),
    # ── khái_niệm ──
    ("Tam quốc", "khái_niệm", ["tam quốc", "three kingdoms", "三国"]),
    ("Tam quốc diễn nghĩa", "khái_niệm", ["tam quốc diễn nghĩa", "romance of the three kingdoms", "三国演义"]),
    ("Ngũ hổ tướng", "khái_niệm", ["ngũ hổ tướng", "five tiger generals", "五虎上将"]),
    ("Trung nghĩa", "khái_niệm", ["trung nghĩa", "righteous", "忠义"]),
    ("Trung thành", "khái_niệm", ["trung thành", "loyal", "忠诚"]),
    ("Nhân nghĩa", "khái_niệm", ["nhân nghĩa", "benevolent", "仁义"]),
    ("Nghĩa khí", "khái_niệm", ["nghĩa khí", "chivalrous", "义气"]),
    ("Võ thánh", "khái_niệm", ["võ thánh", "martial saint", "武圣", "warrior saint"]),
    ("Chiến thần", "khái_niệm", ["chiến thần", "god of war"]),
    ("Kiêu ngạo", "khái_niệm", ["kiêu ngạo", "arrogant", "傲慢"]),
    ("Lịch sử", "khái_niệm", ["lịch sử", "chính sử", "history", "historical"]),
    ("Diễn nghĩa", "khái_niệm", ["diễn nghĩa", "romance"]),
    ("Hào kiệt", "khái_niệm", ["hào kiệt", "hero"]),
    ("Ngũ hổ", "khái_niệm", ["ngũ hổ"]),
    ("Cải lương", "khái_niệm", ["cải lương", "tuồng", "hát bội", "hát bộ", "opera"]),
    # ── tín_ngưỡng ──
    ("Quan Thánh Đế Quân", "tín_ngưỡng", ["quan thánh đế quân", "quan thánh", "关圣帝君"]),
    ("Thờ cúng", "tín_ngưỡng", ["thờ cúng", "thờ", "được thờ", "worship", "tôn kính"]),
    ("Đền miếu", "tín_ngưỡng", ["đền", "miếu", "chùa", "temple", "đền thờ"]),
    ("Linh thiêng", "tín_ngưỡng", ["linh thiêng", "phúc đức", "deity", "phong thần"]),
    ("Quan Đế", "tín_ngưỡng", ["quan đế", "quan nhị ca", "nhị ca", "nhị gia"]),
    ("Lễ hội", "tín_ngưỡng", ["lễ hội", "lễ vía", "diễu hành", "múa lân"]),
    # ── vũ_khí_biểu_tượng ──
    ("Thanh Long đao", "vũ_khí_biểu_tượng", [
        "thanh long đao", "thanh long yển nguyệt", "thanh long yển nguyệt đao",
        "green dragon", "crescent blade", "青龙偃月刀",
    ]),
    ("Yển Nguyệt đao", "vũ_khí_biểu_tượng", ["yển nguyệt đao", "blue moon dragon"]),
    ("Xích Thố", "vũ_khí_biểu_tượng", ["xích thố", "red hare", "赤兔", "ngựa xích thố"]),
    ("Phương Thiên", "vũ_khí_biểu_tượng", ["phương thiên", "方天画戟"]),
    ("Hồ Quảng", "vũ_khí_biểu_tượng", ["hồ quảng"]),
    ("Tượng", "vũ_khí_biểu_tượng", ["tượng quan", "tượng gỗ", "statue", "sculpture"]),
    # ── nội_dung ──
    ("Phim", "nội_dung", ["phim", "movie", "drama", "điện ảnh", "review phim"]),
    ("Sách", "nội_dung", ["sách", "book", "nxb", "goodreads"]),
    ("Game", "nội_dung", ["game", "dynasty warriors", "honor of king", "王者荣耀", "omg 3q"]),
]


def _build_pattern_index() -> list[tuple[str, str, str]]:
    """Trả list (pattern, canonical, category) sắp theo độ dài pattern giảm dần."""
    rows: list[tuple[str, str, str]] = []
    for canonical, category, patterns in _RAW_ENTRIES:
        for pat in patterns:
            rows.append((pat.lower(), canonical, category))
    rows.sort(key=lambda x: len(x[0]), reverse=True)
    return rows


TAMQUOC_PATTERN_INDEX = _build_pattern_index()

CANONICAL_TO_CATEGORY = {canonical: cat for canonical, cat, _ in _RAW_ENTRIES}


def match_tamquoc_keywords(text: str) -> list[str]:
    """Tìm keyword Tam Quốc trong text (longest-match, mỗi canonical tối đa 1 lần)."""
    if not isinstance(text, str) or not text.strip():
        return []
    blob = text.lower()
    found: set[str] = set()
    for pattern, canonical, _ in TAMQUOC_PATTERN_INDEX:
        if canonical in found:
            continue
        if pattern in blob:
            found.add(canonical)
    return list(found)


def is_seed_keyword(canonical: str) -> bool:
    return canonical in SEED_CANONICALS


def query_has_tamquoc_anchor(query: str) -> bool:
    """Query search có chứa anchor Tam quốc (lowercase)."""
    q = query.lower()
    return any(a in q for a in TAMQUOC_ANCHORS)


def is_result_relevant(title: str, description: str, query: str) -> bool:
    """Giữ kết quả nếu text khớp lexicon Tam quốc hoặc query đã có anchor."""
    text = f"{title} {description}"
    if match_tamquoc_keywords(text):
        return True
    return query_has_tamquoc_anchor(query)
