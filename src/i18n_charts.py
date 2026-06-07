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

# ── GOOGLE TAM QUỐC KEYWORD LABELS (step6/step7) ─────────────────────────────
GOOGLE_CATEGORY_LABELS = {
    "vi": {
        "nhân_vật": "Nhân vật",
        "địa_danh_sự_kiện": "Địa danh / Sự kiện",
        "khái_niệm": "Khái niệm",
        "tín_ngưỡng": "Tín ngưỡng",
        "vũ_khí_biểu_tượng": "Vũ khí / Biểu tượng",
        "nội_dung": "Nội dung",
        "khác": "Khác",
    },
    "en": {
        "nhân_vật": "Character",
        "địa_danh_sự_kiện": "Place / Event",
        "khái_niệm": "Concept",
        "tín_ngưỡng": "Belief / Worship",
        "vũ_khí_biểu_tượng": "Weapon / Symbol",
        "nội_dung": "Content",
        "khác": "Other",
    },
    "zh": {
        "nhân_vật": "人物",
        "địa_danh_sự_kiện": "地名/事件",
        "khái_niệm": "概念",
        "tín_ngưỡng": "信仰",
        "vũ_khí_biểu_tượng": "武器/象征",
        "nội_dung": "内容",
        "khác": "其他",
    },
}

GOOGLE_TAMQUOC_LABELS = {
    "en": {
        "Lưu Bị": "Liu Bei",
        "Trương Phi": "Zhang Fei",
        "Tào Tháo": "Cao Cao",
        "Triệu Vân": "Zhao Yun",
        "Gia Cát Lượng": "Zhuge Liang",
        "Lữ Bố": "Lu Bu",
        "Điêu Thuyền": "Diao Chan",
        "Đổng Trác": "Dong Zhuo",
        "Tôn Quyền": "Sun Quan",
        "Chu Du": "Zhou Yu",
        "Viên Thiệu": "Yuan Shao",
        "Tư Mã Ý": "Sima Yi",
        "Mã Siêu": "Ma Chao",
        "Hoàng Trung": "Huang Zhong",
        "Lục Tốn": "Lu Xun",
        "Hứa Chử": "Xu Chu",
        "Điển Vi": "Dian Wei",
        "Trương Liêu": "Zhang Liao",
        "Bàng Thống": "Pang Tong",
        "Pháp Chính": "Fa Zheng",
        "Cam Ninh": "Gan Ning",
        "Thái Sử Từ": "Taishi Ci",
        "Lã Mông": "Lu Meng",
        "Nhan Lương": "Yan Liang",
        "Văn Xú": "Wen Chou",
        "Hoa Hùng": "Hua Xiong",
        "Hoa Đà": "Hua Tuo",
        "Quan Bình": "Guan Ping",
        "Quan Hưng": "Guan Xing",
        "Bàng Đức": "Pang De",
        "Ngụy Diên": "Wei Yan",
        "Tôn Kiên": "Sun Jian",
        "Tôn Sách": "Sun Ce",
        "Tào Nhân": "Cao Ren",
        "Tào Hồng": "Cao Hong",
        "Hạ Hầu Đôn": "Xiahou Dun",
        "Lý Túc": "Li Su",
        "Nezha": "Nezha",
        "Kinh Châu": "Jingzhou",
        "Xích Bích": "Red Cliffs",
        "Mạch Thành": "Fan Castle",
        "Trường Bản": "Changban",
        "Đào Viên": "Peach Garden",
        "Phượng Nghi Đình": "Phoenix Pavilion",
        "Ngọa Long": "Sleeping Dragon",
        "Khổng Thành Kế": "Empty City Stratagem",
        "Bạch Đế Thành": "White Emperor City",
        "Hán Trung": "Hanzhong",
        "Ngũ Trượng Nguyên": "Wuzhang Plains",
        "Quan Độ": "Battle of Guandu",
        "Hoa Dung": "Sliding Through",
        "Thục Hán": "Shu Han",
        "Ngụy Quốc": "Wei Kingdom",
        "Đông Ngô": "Eastern Wu",
        "Tam quốc": "Three Kingdoms",
        "Tam quốc diễn nghĩa": "Romance of the Three Kingdoms",
        "Ngũ hổ tướng": "Five Tiger Generals",
        "Trung nghĩa": "Righteousness",
        "Trung thành": "Loyalty",
        "Nhân nghĩa": "Benevolence",
        "Nghĩa khí": "Chivalry",
        "Võ thánh": "Martial Saint",
        "Chiến thần": "God of War",
        "Kiêu ngạo": "Arrogance",
        "Lịch sử": "History",
        "Diễn nghĩa": "Romance Fiction",
        "Hào kiệt": "Hero",
        "Ngũ hổ": "Five Tigers",
        "Cải lương": "Cai Luong Opera",
        "Quan Thánh Đế Quân": "Guan Sheng Emperor",
        "Thờ cúng": "Worship",
        "Đền miếu": "Temple / Shrine",
        "Linh thiêng": "Sacred",
        "Quan Đế": "Guan Di",
        "Lễ hội": "Festival",
        "Thanh Long đao": "Green Dragon Blade",
        "Yển Nguyệt đao": "Crescent Moon Blade",
        "Xích Thố": "Red Hare",
        "Phương Thiên": "Sky Piercer",
        "Hồ Quảng": "Hu Guang",
        "Tượng": "Statue",
        "Phim": "Film",
        "Sách": "Book",
        "Game": "Game",
    },
    "zh": {
        "Lưu Bị": "刘备",
        "Trương Phi": "张飞",
        "Tào Tháo": "曹操",
        "Triệu Vân": "赵云",
        "Gia Cát Lượng": "诸葛亮",
        "Lữ Bố": "吕布",
        "Điêu Thuyền": "貂蝉",
        "Đổng Trác": "董卓",
        "Tôn Quyền": "孙权",
        "Chu Du": "周瑜",
        "Viên Thiệu": "袁绍",
        "Tư Mã Ý": "司马懿",
        "Mã Siêu": "马超",
        "Hoàng Trung": "黄忠",
        "Lục Tốn": "陆逊",
        "Hứa Chử": "许褚",
        "Điển Vi": "典韦",
        "Trương Liêu": "张辽",
        "Bàng Thống": "庞统",
        "Pháp Chính": "法正",
        "Cam Ninh": "甘宁",
        "Thái Sử Từ": "太史慈",
        "Lã Mông": "吕蒙",
        "Nhan Lương": "颜良",
        "Văn Xú": "文丑",
        "Hoa Hùng": "华雄",
        "Hoa Đà": "华佗",
        "Quan Bình": "关平",
        "Quan Hưng": "关兴",
        "Bàng Đức": "庞德",
        "Ngụy Diên": "魏延",
        "Tôn Kiên": "孙坚",
        "Tôn Sách": "孙策",
        "Tào Nhân": "曹仁",
        "Tào Hồng": "曹洪",
        "Hạ Hầu Đôn": "夏侯惇",
        "Lý Túc": "李肃",
        "Nezha": "哪吒",
        "Kinh Châu": "荆州",
        "Xích Bích": "赤壁",
        "Mạch Thành": "麦城",
        "Trường Bản": "长坂坡",
        "Đào Viên": "桃园",
        "Phượng Nghi Đình": "凤仪亭",
        "Ngọa Long": "卧龙",
        "Khổng Thành Kế": "空城计",
        "Bạch Đế Thành": "白帝城",
        "Hán Trung": "汉中",
        "Ngũ Trượng Nguyên": "五丈原",
        "Quan Độ": "官渡",
        "Hoa Dung": "过五关斩六将",
        "Thục Hán": "蜀汉",
        "Ngụy Quốc": "魏国",
        "Đông Ngô": "东吴",
        "Tam quốc": "三国",
        "Tam quốc diễn nghĩa": "三国演义",
        "Ngũ hổ tướng": "五虎上将",
        "Trung nghĩa": "忠义",
        "Trung thành": "忠诚",
        "Nhân nghĩa": "仁义",
        "Nghĩa khí": "义气",
        "Võ thánh": "武圣",
        "Chiến thần": "战神",
        "Kiêu ngạo": "傲慢",
        "Lịch sử": "历史",
        "Diễn nghĩa": "演义",
        "Hào kiệt": "豪杰",
        "Ngũ hổ": "五虎",
        "Cải lương": "粤剧/戏曲",
        "Quan Thánh Đế Quân": "关圣帝君",
        "Thờ cúng": "祭祀",
        "Đền miếu": "庙宇",
        "Linh thiêng": "神圣",
        "Quan Đế": "关帝",
        "Lễ hội": "节庆",
        "Thanh Long đao": "青龙偃月刀",
        "Yển Nguyệt đao": "偃月刀",
        "Xích Thố": "赤兔",
        "Phương Thiên": "方天画戟",
        "Hồ Quảng": "虎关",
        "Tượng": "雕像",
        "Phim": "影视",
        "Sách": "书籍",
        "Game": "游戏",
    },
}


def google_keyword_label(canonical: str, locale: str) -> str:
    if locale == "vi":
        return canonical
    return GOOGLE_TAMQUOC_LABELS.get(locale, {}).get(canonical, canonical)


def google_category_label(category: str, locale: str) -> str:
    return GOOGLE_CATEGORY_LABELS.get(locale, {}).get(category, category)

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

CONTENT_TYPE_LABELS = {
    "vi": {
        "Tin tức": "Tin tức",
        "Bách khoa": "Bách khoa",
        "Văn học": "Văn học",
        "Giáo dục": "Giáo dục",
        "Tín ngưỡng": "Tín ngưỡng",
        "Lịch sử": "Lịch sử",
        "Giải trí": "Giải trí",
        "Điện ảnh": "Điện ảnh",
        "Game": "Game",
        "Sách": "Sách",
        "Blog": "Blog",
        "Hình ảnh": "Hình ảnh",
        "Thương mại": "Thương mại",
        "Du lịch": "Du lịch",
        "MXH": "MXH",
        "Nghiên cứu": "Nghiên cứu",
        "Học thuật": "Học thuật",
        "Báo cáo": "Báo cáo",
        "Khác": "Khác",
    },
    "en": {
        "Tin tức": "News",
        "Bách khoa": "Encyclopedia",
        "Văn học": "Literature",
        "Giáo dục": "Education",
        "Tín ngưỡng": "Religion & Culture",
        "Lịch sử": "History",
        "Giải trí": "Entertainment",
        "Điện ảnh": "Film",
        "Game": "Games",
        "Sách": "Books",
        "Blog": "Blog & Forum",
        "Hình ảnh": "Images & Stock",
        "Thương mại": "Commerce",
        "Du lịch": "Travel",
        "MXH": "Chinese Social",
        "Nghiên cứu": "Research",
        "Học thuật": "Academic",
        "Báo cáo": "Report",
        "Khác": "Other",
    },
    "zh": {
        "Tin tức": "新闻",
        "Bách khoa": "百科",
        "Văn học": "文学",
        "Giáo dục": "教育",
        "Tín ngưỡng": "信仰文化",
        "Lịch sử": "历史",
        "Giải trí": "娱乐",
        "Điện ảnh": "影视",
        "Game": "游戏",
        "Sách": "书籍",
        "Blog": "博客论坛",
        "Hình ảnh": "图片素材",
        "Thương mại": "商业",
        "Du lịch": "旅游",
        "MXH": "中文社交",
        "Nghiên cứu": "研究",
        "Học thuật": "学术",
        "Báo cáo": "报告",
        "Khác": "其他",
    },
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
        "google_year_trend_title": "Xu thế năm xuất hiện trong kết quả Google (2000–nay)",
        "google_year_trend_xlabel": "Năm",
        "google_year_trend_ylabel": "Số lần xuất hiện",
        "google_top_keywords_title": "Top 15 keyword Tam Quốc liên quan trên Google",
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
        "google_year_trend_title": "Year Trend in Google Results (2000–Present)",
        "google_year_trend_xlabel": "Year",
        "google_year_trend_ylabel": "Occurrences",
        "google_top_keywords_title": "Top 15 Three Kingdoms Keywords on Google",
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
        "google_year_trend_title": "Google结果年份趋势（2000年至今）",
        "google_year_trend_xlabel": "年份",
        "google_year_trend_ylabel": "出现次数",
        "google_top_keywords_title": "Google三国演义相关关键词Top 15",
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
        "section_top_keywords": "Top 15 keyword Tam Quốc (Google)",
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
        "col_category": "Phân loại",
    },
    "en": {
        "page_title": "Report — YouTube Channels & Google Survey",
        "page_heading": "Report — YouTube Channels & Google Survey",
        "section_channels": "YouTube Channel Statistics",
        "section_google_content": "Google Content Classification",
        "section_year_trend": "Year Trend",
        "section_top_keywords": "Top 15 Three Kingdoms Keywords (Google)",
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
        "col_category": "Category",
    },
    "zh": {
        "page_title": "报告 — YouTube频道与Google调查",
        "page_heading": "报告 — YouTube频道与Google调查",
        "section_channels": "YouTube频道统计",
        "section_google_content": "Google内容分类",
        "section_year_trend": "年份趋势",
        "section_top_keywords": "Google三国演义关键词Top 15",
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
        "col_category": "分类",
    },
}

# ── SUMMARY NARRATIVE (Markdown) ──────────────────────────────────────────────
NARRATIVE_TEXT = {
    "vi": {
        "intro": (
            "Báo cáo này tổng hợp kết quả khảo sát nội dung liên quan đến "
            "Quan Công, Quan Vũ, Quan Thánh, Quan Thánh Đế Quân và Quan Vân Trường "
            "trên YouTube và kết quả tìm kiếm web."
        ),
        "table_detail": "Bảng chi tiết",
        "channels_para": (
            "Trong tổng số **{total_channels}** kênh có từ 2 video trở lên, "
            "kênh **{top_channel}** dẫn đầu với **{top_videos}** video "
            "({top_pct}%). Về loại tài khoản, {account_breakdown}."
        ),
        "channels_top3": "Ba kênh hàng đầu gồm: {top3_list}.",
        "account_item": "{label} chiếm **{pct}%** ({videos} video)",
        "account_join": " và ",
        "top3_item": "**{name}** ({videos} video, {pct}%)",
        "top3_join": ", ",
        "content_para": (
            "Trong tổng số **{total}** kết quả được phân loại, "
            "{top_types} chiếm tỷ lệ cao nhất."
        ),
        "content_type_item": "**{type}** ({pct}%)",
        "content_type_join": ", ",
        "year_para": (
            "Năm **{peak_year}** ghi nhận số lần xuất hiện cao nhất "
            "với **{peak_count}** lần. Xu hướng gần đây: {trend_label}."
        ),
        "trend_up": "tăng dần",
        "trend_down": "giảm dần",
        "trend_stable": "tương đối ổn định",
        "keywords_para": "Các keyword Tam Quốc nổi bật nhất trên Google gồm: {keyword_list}.",
        "keyword_item": "**{keyword}** ({rate})",
        "keyword_join": ", ",
    },
    "en": {
        "intro": (
            "This report summarizes survey results for content related to "
            "Guan Gong, Guan Yu, Guan Sheng, Guan Sheng Emperor, and Guan Yun Chang "
            "on YouTube and web search results."
        ),
        "table_detail": "Detailed table",
        "channels_para": (
            "Among **{total_channels}** channels with at least 2 videos, "
            "**{top_channel}** leads with **{top_videos}** videos "
            "({top_pct}%). By account type, {account_breakdown}."
        ),
        "channels_top3": "The top three channels are: {top3_list}.",
        "account_item": "{label} accounts for **{pct}%** ({videos} videos)",
        "account_join": " and ",
        "top3_item": "**{name}** ({videos} videos, {pct}%)",
        "top3_join": ", ",
        "content_para": (
            "Out of **{total}** classified results, "
            "{top_types} account for the largest share."
        ),
        "content_type_item": "**{type}** ({pct}%)",
        "content_type_join": ", ",
        "year_para": (
            "The year **{peak_year}** recorded the highest occurrence count "
            "with **{peak_count}** mentions. Recent trend: {trend_label}."
        ),
        "trend_up": "increasing",
        "trend_down": "decreasing",
        "trend_stable": "relatively stable",
        "keywords_para": "The most prominent Three Kingdoms keywords on Google include: {keyword_list}.",
        "keyword_item": "**{keyword}** ({rate})",
        "keyword_join": ", ",
    },
    "zh": {
        "intro": (
            "本报告汇总了与关羽、关圣、关圣帝君、关云长相关内容"
            "在YouTube及网络搜索结果中的调查数据。"
        ),
        "table_detail": "详细表格",
        "channels_para": (
            "在至少发布2个视频的 **{total_channels}** 个频道中，"
            "**{top_channel}** 以 **{top_videos}** 个视频位居首位"
            "（{top_pct}%）。按账号类型，{account_breakdown}。"
        ),
        "channels_top3": "排名前三的频道为：{top3_list}。",
        "account_item": "{label}占 **{pct}%**（{videos} 个视频）",
        "account_join": "，",
        "top3_item": "**{name}**（{videos} 个视频，{pct}%）",
        "top3_join": "、",
        "content_para": (
            "在 **{total}** 条已分类结果中，"
            "{top_types} 占比最高。"
        ),
        "content_type_item": "**{type}**（{pct}%）",
        "content_type_join": "、",
        "year_para": (
            "**{peak_year}** 年出现次数最多，"
            "共 **{peak_count}** 次。近期趋势：{trend_label}。"
        ),
        "trend_up": "呈上升趋势",
        "trend_down": "呈下降趋势",
        "trend_stable": "相对稳定",
        "keywords_para": "Google上最相关的三国演义关键词包括：{keyword_list}。",
        "keyword_item": "**{keyword}**（{rate}）",
        "keyword_join": "、",
    },
}


def fmt_dot(x, _=None):
    """Format số với dấu chấm phân cách hàng nghìn: 9890000 → 9.890.000"""
    return f"{int(x):,}".replace(",", ".")


def account_type_label(slug_or_legacy: str, locale: str) -> str:
    """Dịch slug loại tài khoản (hoặc giá trị legacy tiếng Việt) sang locale."""
    slug = ACCOUNT_TYPE_LEGACY.get(slug_or_legacy, slug_or_legacy)
    return ACCOUNT_TYPE_LABELS[locale].get(slug, slug_or_legacy)


def content_type_label(value: str, locale: str) -> str:
    """Dịch loại nội dung Google (tiếng Việt canonical) sang locale."""
    return CONTENT_TYPE_LABELS[locale].get(value, value)


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
_latin_font_prop = None  # Cache

_LATIN_FONT_CANDIDATES = [
    "Segoe UI",
    "Arial",
    "DejaVu Sans",
]


def get_latin_font():
    """Font Latin có dấu tiếng Việt cho nhãn trục trên biểu đồ zh."""
    global _latin_font_prop
    if _latin_font_prop is not None:
        return _latin_font_prop

    available = {f.name for f in fm.fontManager.ttflist}
    for candidate in _LATIN_FONT_CANDIDATES:
        if candidate in available:
            _latin_font_prop = fm.FontProperties(family=candidate)
            return _latin_font_prop

    _latin_font_prop = fm.FontProperties(family="DejaVu Sans")
    return _latin_font_prop


def apply_latin_xticklabels(ax, locale: str):
    """Gán font Latin cho nhãn trục X khi locale zh hiển thị text tiếng Việt."""
    if locale != "zh":
        return
    latin_font = get_latin_font()
    for label in ax.get_xticklabels():
        label.set_fontproperties(latin_font)


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
        plt.rcParams['font.sans-serif'] = [font_family, 'Segoe UI', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    else:
        # Reset về font mặc định cho vi/en
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = True

