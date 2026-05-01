"""BƯỚC 1b (V5): Lọc data rác khỏi v5_3000_videos_raw.csv.
Chiến lược 3 lớp:
  1. Blacklist: Loại ngay nếu title chứa từ khóa rác (quân sự, tin tức, YouTuber…)
  2. Whitelist: Giữ lại nếu title chứa ít nhất 1 từ khóa Tam Quốc / Quan Vũ
  3. Fallback: Không match cả 2 → giữ lại để step2 xử lý bằng AI Embeddings

Input:  data/v5_3000_videos_raw.csv
Output: data/v5_3000_videos_cleaned.csv
"""

import pandas as pd
from pathlib import Path
import sys, io

# Fix encoding trên Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ── LỚP 1: BLACKLIST ─────────────────────────────────────────────────────────
# Nếu title chứa BẤT KỲ cụm nào → loại ngay
BLACKLIST = [
    # Quân sự / vũ khí / chính trị
    "vũ khí", "lực lượng vũ trang", "không quân", "hải quân", "quân vũ",
    "tên lửa", "hạt nhân", "quân đội", "quân sự", "lầu năm góc", "pentagon",
    "chiến hạm", "tàu chiến", "máy bay chiến đấu", "quốc phòng",
    "vệ tinh radar", "siêu vũ khí", "kho vũ khí", "đạn đạo",
    # Tin tức / thời sự quốc tế
    "iran", "ukraine", "nato", "trump", "biden", "putin",
    "bầu cử", "quốc hội", "thời sự", "bản tin thế giới",
    "israel", "hamas", "gaza", "al qaeda", "taliban",
    # Giải trí / YouTuber không liên quan
    "khánh linh", "quang con", "tiktok", "thử thách",
    "man utd", "arsenal", "champions league", "bóng đá", "leo rank",
    "flowborn", "roblox",
    # Nhân vật / phim bị nhầm
    "diêu quán vũ", "hạng vũ", "bao công", "triển chiêu", "bao thanh thiên",
    "quán vũ",  # diễn viên Diêu Quán Vũ
    # Các cụm dễ nhầm
    "đồng diễn quân vũ", "nhảy quân vũ", "điệu vũ",
    "haki vũ trang", "haki quan sát",
    "nhà quan sát",  # kênh tin tức
    "vns defense", "thế trận ngầm", "bàn cờ thế sự",
]

# ── LỚP 2: WHITELIST ─────────────────────────────────────────────────────────
# Nếu title chứa ÍT NHẤT 1 cụm → chắc chắn giữ
WHITELIST = [
    # Quan Vũ & biến thể
    "quan vũ", "quan công", "quan vân trường", "quan thánh",
    "quan thánh đế quân", "guan yu", "关羽", "关公", "关帝",
    "võ thánh", "nhị ca", "nhị gia",
    # Tam Quốc chung
    "tam quốc", "three kingdoms", "三国", "thục hán",
    "ngụy quốc", "đông ngô", "tam quốc diễn nghĩa",
    # Nhân vật Tam Quốc
    "lưu bị", "刘备", "trương phi", "张飞", "tào tháo", "曹操",
    "triệu vân", "赵云", "triệu tử long",
    "gia cát lượng", "诸葛亮", "khổng minh",
    "lã bố", "吕布", "điêu thuyền", "đổng trác",
    "tôn quyền", "chu du", "viên thiệu", "tư mã ý",
    "mã siêu", "hoàng trung", "ngũ hổ tướng",
    "lục tốn", "hứa chử", "điển vi", "trương liêu",
    "bàng thống", "pháp chính", "cam ninh", "thái sử từ",
    # Địa danh / sự kiện Tam Quốc
    "kinh châu", "xích bích", "hoa dung", "trường bản",
    "đào viên", "phượng nghi đình", "ngọa long", "khổng thành kế",
    "bạch đế thành", "hán trung", "ngũ trượng nguyên",
    "xích thố", "thanh long yển nguyệt đao", "thanh long đao",
    # Cải lương Tam Quốc
    "cải lương", "tuồng", "hát bội",
]


def check_blacklist(title_lower: str) -> bool:
    """Trả về True nếu title chứa từ khóa rác."""
    for kw in BLACKLIST:
        if kw in title_lower:
            return True
    return False


def check_whitelist(title_lower: str) -> bool:
    """Trả về True nếu title chứa từ khóa Tam Quốc / Quan Vũ."""
    for kw in WHITELIST:
        if kw in title_lower:
            return True
    return False


def main():
    in_file = DATA_DIR / "v5_3000_videos_raw.csv"
    out_file = DATA_DIR / "v5_3000_videos_cleaned.csv"

    if not in_file.exists():
        print(f"[!] Không tìm thấy {in_file}")
        return

    df = pd.read_csv(in_file)
    total = len(df)
    print(f"[*] Đọc {total} videos từ {in_file.name}")

    # Xóa dòng null title
    df = df.dropna(subset=["title"]).copy()
    df["_title_lower"] = df["title"].str.lower()

    # ── LỚP 1: Blacklist ──
    df["_is_blacklisted"] = df["_title_lower"].apply(check_blacklist)
    blacklisted = df["_is_blacklisted"].sum()
    print(f"[*] LỚP 1 - Blacklist: Đánh dấu loại {blacklisted} videos rác")

    # ── LỚP 2: Whitelist (chỉ xét video KHÔNG bị blacklist) ──
    df["_is_whitelisted"] = df["_title_lower"].apply(check_whitelist)

    # Logic: Giữ nếu (whitelist AND NOT blacklist) HOẶC (NOT blacklist AND NOT whitelist → fallback giữ)
    # Loại nếu: blacklist AND NOT whitelist
    # Trường hợp đặc biệt: blacklist AND whitelist → GIỮ (ví dụ: title có cả "quân vũ" và "tam quốc")
    df["_keep"] = ~df["_is_blacklisted"] | df["_is_whitelisted"]

    removed = (~df["_keep"]).sum()
    kept = df["_keep"].sum()

    # Báo cáo chi tiết
    bl_only = ((df["_is_blacklisted"]) & (~df["_is_whitelisted"])).sum()
    bl_and_wl = ((df["_is_blacklisted"]) & (df["_is_whitelisted"])).sum()
    wl_only = ((~df["_is_blacklisted"]) & (df["_is_whitelisted"])).sum()
    neither = ((~df["_is_blacklisted"]) & (~df["_is_whitelisted"])).sum()

    print(f"[*] LỚP 2 - Whitelist check:")
    print(f"    → Chỉ whitelist (giữ):          {wl_only}")
    print(f"    → Blacklist + whitelist (giữ):   {bl_and_wl}")
    print(f"    → Chỉ blacklist (LOẠI):          {bl_only}")
    print(f"    → Không match gì (giữ fallback): {neither}")

    # Xuất mẫu video bị loại
    removed_df = df[~df["_keep"]]
    if not removed_df.empty:
        print(f"\n[*] MẪU 20 VIDEO BỊ LOẠI:")
        for _, row in removed_df.head(20).iterrows():
            print(f"    ✗ {str(row['title'])[:100]}")

    # Lưu kết quả (bỏ cột tạm)
    result = df[df["_keep"]].drop(
        columns=["_title_lower", "_is_blacklisted", "_is_whitelisted", "_keep"]
    )

    result.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"\n[*] TỔNG KẾT: {total} → {len(result)} videos (loại {removed} rác)")
    print(f"[OK] Đã lưu vào {out_file.name}")


if __name__ == "__main__":
    main()
