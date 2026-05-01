"""Module đa ngôn ngữ (i18n) cho biểu đồ output V5.
Hỗ trợ 3 ngôn ngữ: Tiếng Việt (vi), Tiếng Anh (en), Tiếng Trung (zh).
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ── LOCALES ────────────────────────────────────────────────────────────────────
SUPPORTED_LOCALES = ["vi", "en", "zh"]

# ── TOPIC LABELS (16 chủ đề) ──────────────────────────────────────────────────
TOPIC_LABELS = {
    "vi": {
        "game_esport": "Game / Esport",
        "tuong_mo_hinh": "Tượng / Mô hình",
        "nghệ_thuật_biểu_diễn": "Nghệ thuật biểu diễn",
        "hinh_xam": "Hình xăm / Tattoo",
        "xuyen_khong_tieu_thuyet": "Xuyên không / Tiểu thuyết",
        "nguyên_nhân_chết": "Nguyên nhân chết",
        "tín_ngưỡng": "Tín ngưỡng",
        "vũ_khí_xích_thố": "Vũ khí / Xích Thố",
        "so_sánh_sức_mạnh": "So sánh sức mạnh",
        "tính_cách": "Phân tích tính cách",
        "lai_lịch": "Lai lịch",
        "quan_hệ_nhân_vật": "Quan hệ nhân vật",
        "sự_thật_lịch_sử": "Sự thật / Trận đánh",
        "phim_cut": "Phim / Đoạn cut",
        "cuộc_đời": "Cuộc đời Quan Vũ",
        "khác": "Khác",
    },
    "en": {
        "game_esport": "Game / Esport",
        "tuong_mo_hinh": "Statues / Figurines",
        "nghệ_thuật_biểu_diễn": "Performing Arts",
        "hinh_xam": "Tattoo",
        "xuyen_khong_tieu_thuyet": "Time Travel / Novel",
        "nguyên_nhân_chết": "Cause of Death",
        "tín_ngưỡng": "Beliefs / Worship",
        "vũ_khí_xích_thố": "Weapons / Red Hare",
        "so_sánh_sức_mạnh": "Power Comparison",
        "tính_cách": "Personality Analysis",
        "lai_lịch": "Biography",
        "quan_hệ_nhân_vật": "Character Relations",
        "sự_thật_lịch_sử": "History / Battles",
        "phim_cut": "Movies / Clips",
        "cuộc_đời": "Life of Guan Yu",
        "khác": "Others",
    },
    "zh": {
        "game_esport": "游戏 / 电竞",
        "tuong_mo_hinh": "雕像 / 模型",
        "nghệ_thuật_biểu_diễn": "表演艺术",
        "hinh_xam": "纹身",
        "xuyen_khong_tieu_thuyet": "穿越 / 小说",
        "nguyên_nhân_chết": "死因",
        "tín_ngưỡng": "信仰 / 崇拜",
        "vũ_khí_xích_thố": "武器 / 赤兔",
        "so_sánh_sức_mạnh": "实力对比",
        "tính_cách": "性格分析",
        "lai_lịch": "生平",
        "quan_hệ_nhân_vật": "人物关系",
        "sự_thật_lịch_sử": "史实 / 战役",
        "phim_cut": "影视 / 片段",
        "cuộc_đời": "关羽的一生",
        "khác": "其他",
    },
}

# ── SENTIMENT LABELS ──────────────────────────────────────────────────────────
SENTIMENT_LABELS = {
    "vi": {
        "tích cực": "Tích cực",
        "tiêu cực": "Tiêu cực",
        "trung tính": "Trung tính",
    },
    "en": {
        "tích cực": "Positive",
        "tiêu cực": "Negative",
        "trung tính": "Neutral",
    },
    "zh": {
        "tích cực": "积极",
        "tiêu cực": "消极",
        "trung tính": "中性",
    },
}

# ── KEYWORD (PERSONALITY) LABELS ──────────────────────────────────────────────
KEYWORD_LABELS = {
    "vi": {
        "trung thành": "Trung thành",
        "trung nghĩa": "Trung nghĩa",
        "kiêu ngạo": "Kiêu ngạo",
        "võ thánh": "Võ thánh",
        "anh hùng": "Anh hùng",
        "dũng mãnh": "Dũng mãnh",
        "nghĩa khí": "Nghĩa khí",
        "nhân nghĩa": "Nhân nghĩa",
        "nóng tính": "Nóng tính",
        "trượng nghĩa": "Trượng nghĩa",
        "trung thần": "Trung thần",
        "hào kiệt": "Hào kiệt",
        "yêu nước": "Yêu nước",
        "tín nghĩa": "Tín nghĩa",
    },
    "en": {
        "trung thành": "Loyal",
        "trung nghĩa": "Righteous",
        "kiêu ngạo": "Arrogant",
        "võ thánh": "Martial Saint",
        "anh hùng": "Hero",
        "dũng mãnh": "Brave",
        "nghĩa khí": "Chivalrous",
        "nhân nghĩa": "Benevolent",
        "nóng tính": "Hot-tempered",
        "trượng nghĩa": "Noble",
        "trung thần": "Loyal Minister",
        "hào kiệt": "Outstanding",
        "yêu nước": "Patriotic",
        "tín nghĩa": "Trustworthy",
    },
    "zh": {
        "trung thành": "忠诚",
        "trung nghĩa": "忠义",
        "kiêu ngạo": "傲慢",
        "võ thánh": "武圣",
        "anh hùng": "英雄",
        "dũng mãnh": "勇猛",
        "nghĩa khí": "义气",
        "nhân nghĩa": "仁义",
        "nóng tính": "急躁",
        "trượng nghĩa": "仗义",
        "trung thần": "忠臣",
        "hào kiệt": "豪杰",
        "yêu nước": "爱国",
        "tín nghĩa": "信义",
    },
}

# ── CHART TEXT (titles, axis labels) ──────────────────────────────────────────
CHART_TEXT = {
    "vi": {
        # Step 3 — Topic charts
        "topic_dist_title": "Phân bổ số lượng video theo chủ đề",
        "topic_dist_xlabel": "Chủ đề",
        "topic_dist_ylabel": "Số lượng video",
        "topic_views_title": "Tổng lượt view theo chủ đề",
        "topic_views_ylabel": "Tổng lượt view",
        "topic_comments_title": "Tổng lượt comment theo chủ đề",
        "topic_comments_ylabel": "Tổng lượt comment",
        # Step 6 — Sentiment & Personality
        "sentiment_title": "Phân bố Cảm xúc Bình luận (Sentiment)",
        "personality_title": "Mức độ phổ biến của các tính cách mô tả Quan Vũ",
        "personality_xlabel": "Số lần xuất hiện",
        "personality_ylabel": "Tính cách / Đặc điểm",
    },
    "en": {
        "topic_dist_title": "Video Distribution by Topic",
        "topic_dist_xlabel": "Topic",
        "topic_dist_ylabel": "Number of Videos",
        "topic_views_title": "Total Views by Topic",
        "topic_views_ylabel": "Total Views",
        "topic_comments_title": "Total Comments by Topic",
        "topic_comments_ylabel": "Total Comments",
        "sentiment_title": "Comment Sentiment Distribution",
        "personality_title": "Popularity of Personality Traits Describing Guan Yu",
        "personality_xlabel": "Occurrences",
        "personality_ylabel": "Personality Trait",
    },
    "zh": {
        "topic_dist_title": "各主题视频数量分布",
        "topic_dist_xlabel": "主题",
        "topic_dist_ylabel": "视频数量",
        "topic_views_title": "各主题总观看量",
        "topic_views_ylabel": "总观看量",
        "topic_comments_title": "各主题总评论量",
        "topic_comments_ylabel": "总评论量",
        "sentiment_title": "评论情感分布",
        "personality_title": "描述关羽的性格特征的流行度",
        "personality_xlabel": "出现次数",
        "personality_ylabel": "性格特征",
    },
}


# ── FONT HELPER ───────────────────────────────────────────────────────────────
# Danh sách font CJK phổ biến trên Windows
_CJK_FONT_CANDIDATES = [
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "NSimSun",
    "KaiTi",
    "FangSong",
]

_zh_font_prop = None  # Cache


def get_zh_font():
    """Tìm font CJK khả dụng trên hệ thống cho tiếng Trung."""
    global _zh_font_prop
    if _zh_font_prop is not None:
        return _zh_font_prop

    available = {f.name for f in fm.fontManager.ttflist}
    for candidate in _CJK_FONT_CANDIDATES:
        if candidate in available:
            _zh_font_prop = fm.FontProperties(family=candidate)
            return _zh_font_prop

    print("[!] Không tìm thấy font CJK, biểu đồ tiếng Trung có thể hiển thị lỗi.")
    _zh_font_prop = fm.FontProperties()
    return _zh_font_prop


def apply_locale_font(locale: str):
    """Thiết lập font matplotlib phù hợp với locale.
    QUAN TRỌNG: Gọi hàm này SAU sns.set_theme() vì set_theme() sẽ
    reset rcParams. Thứ tự đúng:
        sns.set_theme(style="whitegrid")
        apply_locale_font(locale)
    """
    if locale == "zh":
        zh_font = get_zh_font()
        font_family = zh_font.get_name()
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = [font_family, 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    else:
        # Reset về font mặc định cho vi/en
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = True

