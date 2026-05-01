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

    # 1. Game / Esport
    "game_esport": [
        "game", "gameplay", "omg 3q", "omg3q", "danh tướng 3q", "dt3q",
        "honor of king", "honorofkings", "vgvd", "epic heroes", "heroes evolved",
        "bangbang", "bang bang", "đỉnh phong", "ngọa long",
        "cf mobile", "đột kích", "crossfire", "m4a1",
        "gacha", "skin", "build đồ", "build ",
        "quần anh", "đấu trường chân lý", "wo long", "liên quân",
        "vtc game", "zing me", "knight of valour", "knights of valour",
        "arena of glory", "aog", "i am monkey",
        # English game titles
        "dynasty warriors", "watcher of realms", "smite", "hades",
        "for honor", "empires and puzzles", "kessen",
        "musou", "chaos mode", "chaos difficulty", "hard mode",
        "free mode", "moon rush", "overlords",
        "showcase", "guide", "tutorial", "how to play", "how to use",
        "f2p", "tier", "op hero", "broken", "banner",
        "pvp", "pvp ", "pve", "hack ", "lv10", "lv6",
        "weapon", "unlock", "walkthrough",
        # Chinese game keywords
        "王者荣耀", "荣耀", "赛季", "赛",
        "tank ", "gánh team",
    ],

    # 2. Tượng / Mô hình / Phong thủy
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
        "statue", "sculpture", "origami", "gundam",
        "thác khói", "trầm hương",
        "ngọc cẩm thạch", "jadeite", "ngọc bích",
    ],

    # 3. Nghệ thuật biểu diễn (cải lương, tuồng, kịch, xiếc, múa…)
    "nghệ_thuật_biểu_diễn": [
        # Cải lương / Tuồng / Hát bội
        "cải lương", "tuồng", "hát bội", "vọng cổ", "tân cổ giao duyên",
        # Kịch / Sân khấu
        "kịch", "sân khấu", "nghệ sĩ", "diễn viên",
        "tiết mục", "biểu diễn", "trình diễn", "giao lưu",
        # Kinh kịch / Nghệ thuật Trung Quốc
        "京剧", "opera", "kinh kịch", "peking opera",
        "đoàn nghệ thuật", "nghệ thuật trung quốc",
        # Xiếc / Múa / Biểu diễn khác
        "xiếc", "kungfu", "múa", "điện ảnh",
        "tiếng trung",
    ],

    # 4. Hình xăm / Tattoo
    "hinh_xam": [
        "xăm", "tattoo", "hình xăm",
    ],

    # 5. Xuyên không / Tiểu thuyết audio
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
        "death of", "killed", "death", "tragic",
    ],

    # 6. Tín ngưỡng
    "tín_ngưỡng": [
        "tín ngưỡng", "thờ", "đền", "miếu", "linh thiêng", "phong thần",
        "quan thánh đế quân", "thánh đế", "hiển thánh", "thần", "phúc đức",
        "chùa", "lễ hội", "worship", "temple", "deity",
        "vì sao thờ", "tại sao thờ", "được thờ",
        "god of war", "warrior saint", "martial saint",
        "deification", "tôn kính", "cúi đầu",
        "nghinh ông", "diễu hành", "tuần du", "múa lân", "đoàn lân",
        "lễ xuất", "lễ vía", "quan đế",
        "quan thánh",
    ],

    # 7. Vũ khí / Xích Thố
    "vũ_khí_xích_thố": [
        "thanh long đao", "thanh long yển nguyệt",
        "xích thố", "ngựa xích thố", "bảo đao", "đại đao",
        "yển nguyệt đao", "long đao", "cây đao",
        "green dragon", "crescent blade", "red hare",
        "blue moon dragon",
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
        "loyalty", "arrogant", "righteous",
    ],

    # 10. Lai lịch
    "lai_lịch": [
        "lai lịch", "thân thế", "tiểu sử", "nguồn gốc", "xuất thân",
        "quê quán", "họ tên", "sơ yếu",
        "là ai", "gia thế", "dòng dõi",
        "who is", "real story", "true story",
    ],

    # 11. Quan hệ nhân vật
    "quan_hệ_nhân_vật": [
        "tào tháo", "lưu bị", "gia cát lượng", "khổng minh",
        "trương phi", "lữ bố", "tôn quyền", "lã mông",
        "triệu vân", "hoa đà", "mã siêu", "hoàng trung",
        "chu du", "cam ninh", "lý túc", "lục tốn",
        "nhan lương", "văn xú", "quan hưng", "quan bình",
        "hứa chử", "trương liêu", "bàng thống",
        # English names
        "cao cao", "liu bei", "zhuge liang", "zhang fei",
        "lu bu", "sun quan", "lu meng", "zhao yun",
        "hua tuo", "ma chao", "huang zhong",
        "yan liang", "wen chou", "hua xiong", "pang de",
        "guan xing", "ne zha",
        # Chinese names
        "曹操", "刘备", "诸葛亮", "张飞", "吕布", "孙权",
    ],

    # 12. Sự thật lịch sử / Trận đánh
    "sự_thật_lịch_sử": [
        "sự thật", "thật sự", "bí ẩn", "bí mật", "giải mã",
        "có thật", "thực hư", "chính sử", "lịch sử",
        "phân tích", "sử", "diễn nghĩa", "ngũ hổ tướng",
        "kinh châu", "xích bích", "tranh hùng", "hào kiệt",
        "history", "three kingdoms",
        # Trận đánh / Sự kiện cụ thể
        "trận", "chém", "xuất trận", "ra trận", "đại phá",
        "vượt ải", "qua ải", "hoa dung", "tha tào",
        "phục ma", "trảm", "đánh bại", "xuất thế",
        "chiến dịch", "đơn đao", "cứu viện",
        "battle", "fight", "escape", "siege", "fan castle",
        "guan du", "si shui", "chang ban", "wu zhang",
        "mythology", "legend", "legendary", "hero",
        "remarkable life", "complete",
        # Lăng mộ
        "lăng mộ", "mộ", "khai quật", "tomb",
    ],



    # 14. Phim / Đoạn cut
    "phim_cut": [
        "phim", "movie", "drama", "tập", "cut", "clip",
        "trích đoạn", "full hd", "thuyết minh", "vietsub",
        "lồng tiếng", "trọn bộ", "full bộ", "tổng hợp phim",
        "trùm phim", "review phim", "tóm tắt phim",
        "kiếm hiệp hay", "onfilm", "hồ uy tướng",
        "quán sử kỳ tài", "capcapsub",
        "the lost bladesman",
    ],

    # 15. Fan content / Nghệ thuật
    "fan_content": [
        "edit", "brodyaga", "lil quan", "preach",
        "karaoke", "remix", "nhạc",
        "drawing", "vẽ ", "tranh", "hình nền",
        "diy", "custom", "parody", "music video",
        "tướng quân", "hào khí",
    ],

    # 16. Cuộc đời Quan Vũ (chung nhất → cuối cùng)
    "cuộc_đời": [
        "cuộc đời", "hành trình", "sự nghiệp", "chiến công",
        "tóm tắt", "toàn bộ", "summary", "trọn đời",
        "đời", "truyện", "câu chuyện", "tam quốc",
        "guan yu", "guan gong", "关羽", "关公", "关帝",
        "quan vũ", "quan công", "quan vân trường",
    ],
}

# Nhãn hiển thị tiếng Việt cho biểu đồ
TOPIC_LABELS = {
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
    "fan_content": "Fan content / Nghệ thuật",
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
