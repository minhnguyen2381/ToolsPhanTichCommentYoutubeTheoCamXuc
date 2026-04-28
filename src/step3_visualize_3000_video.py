"""BƯỚC 3 (V5): Phân loại và trực quan hóa 3000 videos.
- Phân loại video dựa vào title
- Vẽ biểu đồ phân bổ chủ đề (số lượng video, lượt view, lượt comment)
- Lưu vào report/v5/
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORT_DIR = Path(__file__).resolve().parent.parent / "report" / "v5"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

TOPIC_RULES = {
    "lịch_sử": [
        "phân tích", "lịch sử", "tiểu sử", "tam quốc", "three kingdoms",
        "history", "sử", "diễn nghĩa", "chính sử", "ngũ hổ tướng",
        "kinh châu", "xích bích", "tranh hùng", "hào kiệt",
    ],
    "nguyên_nhân_chết": [
        "cái chết", "chết", "tử", "bại tẩu", "mạch thành", "lý do chết",
        "sa cơ", "lâm nạn", "bị giết", "thua trận", "thất bại",
        "nguyên nhân", "bi kịch",
    ],
    "tín_ngưỡng": [
        "tín ngưỡng", "thờ", "đền", "miếu", "linh thiêng", "phong thần",
        "quan thánh đế quân", "thánh đế", "hiển thánh", "thần", "phúc đức",
        "chùa", "lễ hội", "worship", "temple", "deity",
    ],
    "kịch_cải_lương": [
        "cải lương", "tuồng", "hát bội", "kịch", "tiếng trung",
        "京剧", "opera", "phim", "movie", "drama", "sân khấu",
        "diễn viên", "nghệ sĩ",
    ],
}

def classify_topic(title: str) -> str:
    """Phân loại chủ đề video dựa trên title."""
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
        print(f"[!] Không tìm thấy {in_file}")
        return

    df = pd.read_csv(in_file)
    print(f"[*] Đang phân loại {len(df)} videos...")
    
    df['topic'] = df['title'].apply(classify_topic)
    
    # Save the classified dataframe just in case
    df.to_csv(DATA_DIR / "v5_video_topics.csv", index=False, encoding="utf-8-sig")

    topic_stats = df.groupby("topic").agg(
        số_video=("videoId", "count"),
        tổng_views=("views", "sum"),
        tổng_comments=("comments", "sum"),
        tổng_likes=("likes", "sum"),
    ).sort_values("số_video", ascending=False).reset_index()

    print("\n=== THỐNG KÊ CHỦ ĐỀ ===")
    print(topic_stats.to_string())

    # Vẽ biểu đồ
    sns.set_theme(style="whitegrid")
    
    # 1. Biểu đồ số lượng video theo chủ đề
    plt.figure(figsize=(10, 6))
    sns.barplot(x="topic", y="số_video", data=topic_stats, palette="viridis", hue="topic", legend=False)
    plt.title("Phân bổ số lượng video theo chủ đề", fontsize=16)
    plt.xlabel("Chủ đề")
    plt.ylabel("Số lượng video")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "topic_distribution.png", dpi=300)
    plt.close()

    # 2. Biểu đồ lượt view theo chủ đề
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x="topic", y="tổng_views", data=topic_stats, palette="magma", hue="topic", legend=False)
    plt.title("Tổng lượt view theo chủ đề", fontsize=16)
    plt.xlabel("Chủ đề")
    plt.ylabel("Tổng lượt view")
    plt.xticks(rotation=45)
    
    # Tắt scientific notation trên trục Y
    ax.ticklabel_format(style='plain', axis='y')
    
    # In số lên đỉnh cột
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f', padding=3)
        
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "topic_views.png", dpi=300)
    plt.close()

    print(f"[OK] Đã xuất biểu đồ ra thư mục {REPORT_DIR}")

if __name__ == "__main__":
    main()
