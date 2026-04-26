"""BƯỚC 1 (V4): Khảo sát độ phổ biến + phân loại chủ đề video YouTube về Quan Vũ.

Cải tiến V4:
- Mở rộng keyword search (tiếng Trung, tiếng Anh)
- max_results = 500
- Progress bar + ETA bằng tqdm cho mỗi keyword
- Phân loại video theo chủ đề
"""
import sys
import time
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from youtube_client import search_videos, get_video_stats

KEYWORDS = [
    "Quan Vũ",
    "Quan Công",
    "Quan Vân Trường",
    "Quan Thánh",
    "Guan Yu",
    "关羽",
]

MAX_RESULTS = 500

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Quy tắc phân loại chủ đề dựa trên title (lowercase)
# ---------------------------------------------------------------------------
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
    t = title.lower()
    for topic, keywords in TOPIC_RULES.items():
        for kw in keywords:
            if kw in t:
                return topic
    return "khác"


def get_video_stats_with_progress(video_ids, keyword_label=""):
    """Lấy stats từng video với tqdm progress bar."""
    rows = []
    desc = f"Stats {keyword_label}" if keyword_label else "Stats"
    with tqdm(total=len(video_ids), desc=desc, unit="video") as pbar:
        for vid in video_ids:
            try:
                stats = get_video_stats([vid])
                rows.extend(stats)
            except Exception as e:
                print(f"\n  [!] Bỏ qua {vid}: {str(e)[:80]}")
            pbar.update(1)
            time.sleep(0.2)
    return rows


def main():
    all_videos = {}  # videoId -> dict (dedup)
    keyword_summary = []

    for kw_idx, kw in enumerate(KEYWORDS, 1):
        print(f"\n{'='*60}")
        print(f"[{kw_idx}/{len(KEYWORDS)}] Keyword: {kw} (max {MAX_RESULTS})")
        print(f"{'='*60}")

        ids = search_videos(kw, max_results=MAX_RESULTS)
        print(f"  → Tìm thấy {len(ids)} video")

        rows = get_video_stats_with_progress(ids, keyword_label=kw)
        df = pd.DataFrame(rows)

        if not df.empty:
            safe_name = kw.replace(" ", "_")
            df.to_csv(DATA_DIR / f"v4_keyword_{safe_name}.csv",
                      index=False, encoding="utf-8-sig")

        keyword_summary.append({
            "keyword": kw,
            "total_videos": len(ids),
            "fetched_stats": len(rows),
            "total_views": int(df["views"].sum()) if not df.empty else 0,
            "avg_views": int(df["views"].mean()) if not df.empty else 0,
            "total_likes": int(df["likes"].sum()) if not df.empty else 0,
            "total_comments": int(df["comments"].sum()) if not df.empty else 0,
        })

        # Gộp dedup
        for r in rows:
            vid = r["videoId"]
            if vid not in all_videos:
                all_videos[vid] = r

        time.sleep(0.5)

    # --- Keyword summary ---
    df_summary = pd.DataFrame(keyword_summary)
    df_summary.to_csv(DATA_DIR / "v4_keyword_summary.csv",
                      index=False, encoding="utf-8-sig")
    print(f"\n{'='*60}")
    print("=== TÓM TẮT THEO TỪ KHOÁ ===")
    print(f"{'='*60}")
    print(df_summary.to_string(index=False))

    # --- Phân loại chủ đề ---
    df_all = pd.DataFrame(list(all_videos.values()))
    if df_all.empty:
        print("[!] Không có video nào, dừng lại.")
        return

    df_all["topic"] = df_all["title"].apply(classify_topic)
    df_all.to_csv(DATA_DIR / "v4_video_topics.csv",
                  index=False, encoding="utf-8-sig")

    print(f"\n{'='*60}")
    print(f"=== PHÂN LOẠI CHỦ ĐỀ ({len(df_all)} video unique) ===")
    print(f"{'='*60}")

    topic_stats = df_all.groupby("topic").agg(
        số_video=("videoId", "count"),
        tổng_views=("views", "sum"),
        tổng_comments=("comments", "sum"),
        tổng_likes=("likes", "sum"),
    ).sort_values("số_video", ascending=False)

    print(topic_stats.to_string())
    print(f"\n[OK] Đã lưu data/v4_keyword_summary.csv + data/v4_video_topics.csv")


if __name__ == "__main__":
    main()
