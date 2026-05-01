"""BƯỚC 3 (V5): Phân loại và trực quan hóa 3000 videos.
- Phân loại video dựa vào title (15 chủ đề)
- Vẽ biểu đồ phân bổ chủ đề (số lượng video, lượt view, lượt comment)
- Lưu vào report/v5/
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys, io

# Fix encoding trên Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORT_DIR = Path(__file__).resolve().parent.parent / "report" / "v5"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ── 15 CHỦ ĐỀ PHÂN LOẠI ─────────────────────────────────────────────────────
# Thứ tự trong dict = thứ tự ưu tiên khi phân loại.
# Chủ đề cụ thể hơn đặt trước, chủ đề chung đặt sau.
TOPIC_RULES = {
    # ── NHÓM 1: Keywords cực kỳ cụ thể (ưu tiên cao nhất) ──

    # 1. Game / Esport (keywords rất specific, không thể nhầm)
    "game_esport": [
        "game", "gameplay", "omg 3q", "omg3q", "danh tướng 3q", "dt3q",
        "honor of king", "vgvd", "epic heroes", "heroes evolved",
        "bangbang", "bang bang", "đỉnh phong", "ngọa long",
        "cf mobile", "đột kích", "crossfire",
        "gacha", "skin", "build đồ",
        "quần anh", "đấu trường chân lý", "wo long", "liên quân",
        "vtc game", "zing me", "knight of valour",
        "arena of glory", "aog", "i am monkey",
    ],

    # 2. Tượng / Mô hình / Phong thủy (keywords rất specific)
    "tuong_mo_hinh": [
        "tượng", "mô hình", "figure", "unboxing", "khui hộp",
        "gỗ hương", "gỗ mun", "gỗ trắc", "gỗ bách xanh", "gỗ ngọc am",
        "gỗ xá cừ", "gỗ quý", "gỗ sơn trắc",
        "đồ gỗ", "đồ đồng", "đúc đồng", "thếp vàng",
        "điêu khắc", "chế tác", "mỹ nghệ",
        "dây chuyền", "mặt dây", "vòng cổ", "zippo",
        "phong thủy", "phong thuỷ", "trấn trạch", "hóa giải",
        "bán lẻ", "đặt tượng", "trưng bày", "báo giá",
        "cao 40cm", "cao 50cm", "cao 60cm", "cao 80cm", "cao 1m",
    ],

    # 3. Hình xăm / Tattoo
    "hinh_xam": [
        "xăm", "tattoo", "hình xăm",
    ],

    # 4. Xuyên không / Tiểu thuyết audio
    "xuyen_khong_tieu_thuyet": [
        "xuyên không", "chapter", "tuyệt lộ",
        "xuyên thành con trai",
    ],

    # ── NHÓM 2: Chủ đề Tam Quốc cụ thể ──

    # 5. Nguyên nhân cái chết
    "nguyên_nhân_chết": [
        "cái chết", "chết", "tử", "bại tẩu", "mạch thành", "lý do chết",
        "sa cơ", "lâm nạn", "bị giết", "thua trận", "thất bại",
        "nguyên nhân", "bi kịch", "hy sinh", "tử trận",
    ],

    # 6. Tín ngưỡng
    "tín_ngưỡng": [
        "tín ngưỡng", "thờ", "đền", "miếu", "linh thiêng", "phong thần",
        "quan thánh đế quân", "thánh đế", "hiển thánh", "thần", "phúc đức",
        "chùa", "lễ hội", "worship", "temple", "deity",
        "vì sao thờ", "tại sao thờ", "được thờ",
    ],

    # 7. Vũ khí / Xích Thố
    "vũ_khí_xích_thố": [
        "thanh long đao", "thanh long yển nguyệt",
        "xích thố", "ngựa xích thố", "bảo đao", "đại đao",
        "yển nguyệt đao", "long đao", "cây đao",
    ],

    # 8. So sánh sức mạnh
    "so_sánh_sức_mạnh": [
        "so sánh", "ai mạnh", "vs", "đấu với", "đánh nhau",
        "top", "xếp hạng", "ranking", "mạnh nhất", "số 1",
        "đọ sức", "ai giỏi", "chiến thần", "bất bại",
        "so tài", "đấu tướng", "ai thắng", "ngang tài",
        "so kèo", "ai hơn ai",
    ],

    # 9. Phân tích tính cách
    "tính_cách": [
        "tính cách", "kiêu ngạo", "trung nghĩa", "nhân cách", "đức",
        "kiêu", "ngạo", "trung thành", "tự phụ", "phẩm chất",
        "nhân nghĩa", "trung can", "nghĩa khí", "hào hiệp",
        "dũng mãnh", "cao ngạo", "tính tình",
    ],

    # 10. Lai lịch
    "lai_lịch": [
        "lai lịch", "thân thế", "tiểu sử", "nguồn gốc", "xuất thân",
        "quê quán", "họ tên", "sơ yếu", "lai lịch",
        "là ai", "gia thế", "dòng dõi",
    ],

    # 11. Quan hệ nhân vật (interactions giữa Quan Vũ và các tướng khác)
    "quan_hệ_nhân_vật": [
        "tào tháo", "lưu bị", "gia cát lượng", "khổng minh",
        "trương phi", "lữ bố", "tôn quyền", "lã mông",
        "triệu vân", "hoa đà", "mã siêu", "hoàng trung",
        "chu du", "cam ninh", "lý túc", "lục tốn",
        "nhan lương", "văn xú", "quan hưng", "quan bình",
        "hứa chử", "trương liêu", "bàng thống",
    ],

    # 12. Sự thật lịch sử
    "sự_thật_lịch_sử": [
        "sự thật", "thật sự", "bí ẩn", "bí mật", "giải mã",
        "có thật", "thực hư", "chính sử", "lịch sử",
        "phân tích", "sử", "diễn nghĩa", "ngũ hổ tướng",
        "kinh châu", "xích bích", "tranh hùng", "hào kiệt",
        "history", "three kingdoms",
    ],

    # 13. Kịch cải lương
    "kịch_cải_lương": [
        "cải lương", "tuồng", "hát bội", "kịch", "tiếng trung",
        "京剧", "opera", "sân khấu", "nghệ sĩ", "diễn viên",
        "vọng cổ", "tân cổ giao duyên",
    ],

    # 14. Phim / Đoạn cut
    "phim_cut": [
        "phim", "movie", "drama", "tập", "cut", "clip",
        "trích đoạn", "full hd", "thuyết minh", "vietsub",
        "lồng tiếng", "trọn bộ", "full bộ", "tổng hợp phim",
        "trùm phim", "review phim", "tóm tắt phim",
    ],

    # 15. Cuộc đời Quan Vũ (chung nhất → cuối cùng)
    "cuộc_đời": [
        "cuộc đời", "hành trình", "sự nghiệp", "chiến công",
        "tóm tắt", "toàn bộ", "summary", "trọn đời",
        "đời", "truyện", "câu chuyện", "tam quốc",
    ],
}

# Nhãn hiển thị tiếng Việt cho biểu đồ
TOPIC_LABELS = {
    "game_esport": "Game / Esport",
    "tuong_mo_hinh": "Tượng / Mô hình",
    "hinh_xam": "Hình xăm / Tattoo",
    "xuyen_khong_tieu_thuyet": "Xuyên không / Tiểu thuyết",
    "nguyên_nhân_chết": "Nguyên nhân chết",
    "tín_ngưỡng": "Tín ngưỡng",
    "vũ_khí_xích_thố": "Vũ khí / Xích Thố",
    "so_sánh_sức_mạnh": "So sánh sức mạnh",
    "tính_cách": "Phân tích tính cách",
    "lai_lịch": "Lai lịch",
    "quan_hệ_nhân_vật": "Quan hệ nhân vật",
    "sự_thật_lịch_sử": "Sự thật lịch sử",
    "kịch_cải_lương": "Kịch cải lương",
    "phim_cut": "Phim / Đoạn cut",
    "cuộc_đời": "Cuộc đời Quan Vũ",
    "khác": "Khác",
}


def classify_topic(title: str) -> str:
    """Phân loại chủ đề video dựa trên title.
    Thứ tự ưu tiên: chủ đề cụ thể trước, chung sau.
    """
    if not isinstance(title, str):
        return "khác"
    t = title.lower()
    for topic, keywords in TOPIC_RULES.items():
        for kw in keywords:
            if kw in t:
                return topic
    return "khác"


def main():
    in_file = DATA_DIR / "v5_3000_videos_filtered.csv"
    if not in_file.exists():
        # Fallback: dùng file cleaned nếu không có filtered
        in_file = DATA_DIR / "v5_3000_videos_cleaned.csv"
        if not in_file.exists():
            print(f"[!] Không tìm thấy file input")
            return

    df = pd.read_csv(in_file)
    print(f"[*] Đang phân loại {len(df)} videos từ {in_file.name}...")
    
    df['topic'] = df['title'].apply(classify_topic)
    
    # Save the classified dataframe just in case
    df.to_csv(DATA_DIR / "v5_video_topics.csv", index=False, encoding="utf-8-sig")

    topic_stats = df.groupby("topic").agg(
        số_video=("videoId", "count"),
        tổng_views=("views", "sum"),
        tổng_comments=("comments", "sum"),
        tổng_likes=("likes", "sum"),
    ).sort_values("số_video", ascending=False).reset_index()

    # Thêm nhãn tiếng Việt
    topic_stats["label"] = topic_stats["topic"].map(TOPIC_LABELS).fillna(topic_stats["topic"])

    print("\n=== THỐNG KÊ CHỦ ĐỀ ===")
    print(topic_stats[["label", "số_video", "tổng_views", "tổng_comments", "tổng_likes"]].to_string())

    # Vẽ biểu đồ
    sns.set_theme(style="whitegrid")
    
    # 1. Biểu đồ số lượng video theo chủ đề
    plt.figure(figsize=(14, 8))
    sns.barplot(x="label", y="số_video", data=topic_stats, palette="viridis", hue="label", legend=False)
    plt.title("Phân bổ số lượng video theo chủ đề", fontsize=16)
    plt.xlabel("Chủ đề")
    plt.ylabel("Số lượng video")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "topic_distribution.png", dpi=300)
    plt.close()

    # 2. Biểu đồ lượt view theo chủ đề
    plt.figure(figsize=(14, 8))
    ax = sns.barplot(x="label", y="tổng_views", data=topic_stats, palette="magma", hue="label", legend=False)
    plt.title("Tổng lượt view theo chủ đề", fontsize=16)
    plt.xlabel("Chủ đề")
    plt.ylabel("Tổng lượt view")
    plt.xticks(rotation=45, ha="right")
    
    # Tắt scientific notation trên trục Y
    ax.ticklabel_format(style='plain', axis='y')
    
    # In số lên đỉnh cột
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f', padding=3)
        
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "topic_views.png", dpi=300)
    plt.close()

    # 3. Biểu đồ lượt comment theo chủ đề
    plt.figure(figsize=(14, 8))
    ax2 = sns.barplot(x="label", y="tổng_comments", data=topic_stats, palette="coolwarm", hue="label", legend=False)
    plt.title("Tổng lượt comment theo chủ đề", fontsize=16)
    plt.xlabel("Chủ đề")
    plt.ylabel("Tổng lượt comment")
    plt.xticks(rotation=45, ha="right")
    ax2.ticklabel_format(style='plain', axis='y')
    for container in ax2.containers:
        ax2.bar_label(container, fmt='%.0f', padding=3)
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "topic_comments.png", dpi=300)
    plt.close()

    print(f"[OK] Đã xuất biểu đồ ra thư mục {REPORT_DIR}")

if __name__ == "__main__":
    main()
