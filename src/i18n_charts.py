"""Module đa ngôn ngữ (i18n) cho biểu đồ và báo cáo output.
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
        "game_esport": "游戏电竞",
        "tuong_mo_hinh": "关于雕像/模型",
        "nghệ_thuật_biểu_diễn": "表演艺术",
        "hinh_xam": "关羽纹身",
        "xuyen_khong_tieu_thuyet": "穿越小说",
        "nguyên_nhân_chết": "关羽死因",
        "tín_ngưỡng": "信仰崇拜",
        "vũ_khí_xích_thố": "关羽的武器",
        "so_sánh_sức_mạnh": "各武将实力对比",
        "tính_cách": "性格分析",
        "lai_lịch": "关羽生平",
        "quan_hệ_nhân_vật": "各人物关系",
        "sự_thật_lịch_sử": "史实战役",
        "phim_cut": "影视",
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

# ── ACCOUNT TYPE LABELS (step5 slugs) ─────────────────────────────────────────
ACCOUNT_TYPE_LABELS = {
    "vi": {
        "chinh_thong": "Tài khoản chính thống",
        "ca_nhan": "Tài khoản cá nhân",
    },
    "en": {
        "chinh_thong": "Official account",
        "ca_nhan": "Personal account",
    },
    "zh": {
        "chinh_thong": "官方账号",
        "ca_nhan": "个人账号",
    },
}

# Map giá trị cũ (tiếng Việt) → slug, để tương thích CSV đã sinh trước khi đổi step5
ACCOUNT_TYPE_LEGACY = {
    "Tài khoản chính thống": "chinh_thong",
    "Tài khoản cá nhân": "ca_nhan",
}

# ── CHART TEXT (titles, axis labels) ──────────────────────────────────────────
CHART_TEXT = {
    "vi": {
        # Step 4 — Topic charts
        "topic_dist_title": "Phân bổ số lượng video theo chủ đề",
        "topic_dist_xlabel": "Chủ đề",
        "topic_dist_ylabel": "Số lượng video",
        "topic_views_title": "Tổng lượt view theo chủ đề",
        "topic_views_ylabel": "Tổng lượt view",
        "topic_comments_title": "Tổng lượt comment theo chủ đề",
        "topic_comments_ylabel": "Tổng lượt comment",
        # Step 7 — Channel charts
        "channel_top15_title": "Top 15 kênh YouTube liên quan Quan Vũ",
        "channel_top15_xlabel": "Tên kênh",
        "channel_top15_ylabel": "Số lượng video",
        "channel_account_types_title": "Phân bổ video theo loại tài khoản",
        "channel_account_types_xlabel": "Loại tài khoản",
        "channel_account_types_ylabel": "Số lượng video",
        # Step 7 — Google charts
        "google_content_types_title": "Phân loại nội dung Google (tổng hợp)",
        "google_content_types_xlabel": "Loại nội dung",
        "google_content_types_ylabel": "Số kết quả",
        "google_year_trend_title": "Xu thế năm xuất hiện trong kết quả Google (1980–nay)",
        "google_year_trend_xlabel": "Năm",
        "google_year_trend_ylabel": "Số lần xuất hiện",
        "google_top_keywords_title": "Top 15 keyword liên quan trên Google",
        "google_top_keywords_xlabel": "Keyword",
        "google_top_keywords_ylabel": "Tỷ lệ xuất hiện",
        # Step 10 — Sentiment & Personality
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
        "channel_top15_title": "Top 15 YouTube Channels Related to Guan Yu",
        "channel_top15_xlabel": "Channel Name",
        "channel_top15_ylabel": "Number of Videos",
        "channel_account_types_title": "Video Distribution by Account Type",
        "channel_account_types_xlabel": "Account Type",
        "channel_account_types_ylabel": "Number of Videos",
        "google_content_types_title": "Google Content Type Classification (Summary)",
        "google_content_types_xlabel": "Content Type",
        "google_content_types_ylabel": "Number of Results",
        "google_year_trend_title": "Year Trend in Google Results (1980–Present)",
        "google_year_trend_xlabel": "Year",
        "google_year_trend_ylabel": "Occurrences",
        "google_top_keywords_title": "Top 15 Related Keywords on Google",
        "google_top_keywords_xlabel": "Keyword",
        "google_top_keywords_ylabel": "Occurrence Rate",
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
        "channel_top15_title": "与关羽相关的YouTube频道Top 15",
        "channel_top15_xlabel": "频道名称",
        "channel_top15_ylabel": "视频数量",
        "channel_account_types_title": "按账号类型分布的视频数量",
        "channel_account_types_xlabel": "账号类型",
        "channel_account_types_ylabel": "视频数量",
        "google_content_types_title": "Google内容类型分类（汇总）",
        "google_content_types_xlabel": "内容类型",
        "google_content_types_ylabel": "结果数量",
        "google_year_trend_title": "Google结果年份趋势（1980年至今）",
        "google_year_trend_xlabel": "年份",
        "google_year_trend_ylabel": "出现次数",
        "google_top_keywords_title": "Google相关关键词Top 15",
        "google_top_keywords_xlabel": "关键词",
        "google_top_keywords_ylabel": "出现比率",
        "sentiment_title": "评论情感分布",
        "personality_title": "描述关羽的性格特征的流行度",
        "personality_xlabel": "出现次数",
        "personality_ylabel": "性格特征",
    },
}

# ── SUMMARY HTML TEXT ─────────────────────────────────────────────────────────
SUMMARY_TEXT = {
    "vi": {
        "page_title": "Báo cáo — Kênh YouTube & Khảo sát Google",
        "page_heading": "Báo cáo — Kênh YouTube & Khảo sát Google",
        "section_channels": "Thống kê kênh YouTube",
        "section_google_content": "Phân loại nội dung Google",
        "section_year_trend": "Xu thế theo năm",
        "section_top_keywords": "Top 15 keyword Google",
        "no_data": "Không có dữ liệu.",
        "col_ten_tai_khoan": "Tên tài khoản",
        "col_loai_tai_khoan": "Loại tài khoản",
        "col_so_luong_video": "Số lượng video",
        "col_ty_le_pct": "Tỷ lệ %",
        "col_keyword": "Keyword",
        "col_content_type": "Loại nội dung",
        "col_title": "Tiêu đề",
        "col_url": "URL",
        "col_nam": "Năm",
        "col_so_ket_qua": "Số kết quả",
        "col_ty_le_xuat_hien": "Tỷ lệ xuất hiện",
    },
    "en": {
        "page_title": "Report — YouTube Channels & Google Survey",
        "page_heading": "Report — YouTube Channels & Google Survey",
        "section_channels": "YouTube Channel Statistics",
        "section_google_content": "Google Content Classification",
        "section_year_trend": "Year Trend",
        "section_top_keywords": "Top 15 Google Keywords",
        "no_data": "No data available.",
        "col_ten_tai_khoan": "Account Name",
        "col_loai_tai_khoan": "Account Type",
        "col_so_luong_video": "Number of Videos",
        "col_ty_le_pct": "Percentage (%)",
        "col_keyword": "Keyword",
        "col_content_type": "Content Type",
        "col_title": "Title",
        "col_url": "URL",
        "col_nam": "Year",
        "col_so_ket_qua": "Number of Results",
        "col_ty_le_xuat_hien": "Occurrence Rate",
    },
    "zh": {
        "page_title": "报告 — YouTube频道与Google调查",
        "page_heading": "报告 — YouTube频道与Google调查",
        "section_channels": "YouTube频道统计",
        "section_google_content": "Google内容分类",
        "section_year_trend": "年份趋势",
        "section_top_keywords": "Google关键词Top 15",
        "no_data": "暂无数据。",
        "col_ten_tai_khoan": "账号名称",
        "col_loai_tai_khoan": "账号类型",
        "col_so_luong_video": "视频数量",
        "col_ty_le_pct": "比率 (%)",
        "col_keyword": "关键词",
        "col_content_type": "内容类型",
        "col_title": "标题",
        "col_url": "URL",
        "col_nam": "年份",
        "col_so_ket_qua": "结果数量",
        "col_ty_le_xuat_hien": "出现比率",
    },
}


def fmt_dot(x, _=None):
    """Format số với dấu chấm phân cách hàng nghìn: 9890000 → 9.890.000"""
    return f"{int(x):,}".replace(",", ".")


def account_type_label(slug_or_legacy: str, locale: str) -> str:
    """Dịch slug loại tài khoản (hoặc giá trị legacy tiếng Việt) sang locale."""
    slug = ACCOUNT_TYPE_LEGACY.get(slug_or_legacy, slug_or_legacy)
    return ACCOUNT_TYPE_LABELS[locale].get(slug, slug_or_legacy)


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

