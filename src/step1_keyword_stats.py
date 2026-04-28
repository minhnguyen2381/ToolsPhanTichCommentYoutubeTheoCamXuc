"""BƯỚC 1 (V5): Khảo sát độ phổ biến video YouTube về Quan Vũ.

Cải tiến V5:
- Mở rộng keyword search (tiếng Trung, tiếng Anh)
- max_results = 500
- Progress bar + ETA bằng tqdm cho mỗi keyword
- Thu thập và lưu thẳng ra v5_3000_videos_raw.csv
"""
import sys
import time
import concurrent.futures
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

# (Đã di chuyển phân loại chủ đề sang step 3)


def get_video_stats_with_progress(video_ids, keyword_label=""):
    """Lấy stats từng video với tqdm progress bar (Đa luồng)."""
    rows = []
    desc = f"Stats {keyword_label}" if keyword_label else "Stats"
    max_workers = 12  # Đã có cookie bảo kê, nâng lên 12 luồng chạy tốc độ cao
    
    with tqdm(total=len(video_ids), desc=desc, unit="video") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Hạ sleep xuống 0.1s vì đã có chứng thực
            future_to_vid = {
                executor.submit(get_video_stats, [vid], 0.1): vid 
                for vid in video_ids
            }
            
            for future in concurrent.futures.as_completed(future_to_vid):
                vid = future_to_vid[future]
                try:
                    stats = future.result()
                    rows.extend(stats)
                except Exception as e:
                    print(f"\n  [!] Bỏ qua {vid}: {str(e)[:80]}")
                pbar.update(1)
                
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
            # Không lưu từng keyword ra file riêng nữa
            pass

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
    print(f"\n{'='*60}")
    print("=== TÓM TẮT THEO TỪ KHOÁ ===")
    print(f"{'='*60}")
    print(df_summary.to_string(index=False))

    # --- Gộp toàn bộ video và lưu raw ---
    df_all = pd.DataFrame(list(all_videos.values()))
    if df_all.empty:
        print("[!] Không có video nào, dừng lại.")
        return

    out_file = DATA_DIR / "v5_3000_videos_raw.csv"
    df_all.to_csv(out_file, index=False, encoding="utf-8-sig")

    print(f"\n[OK] Đã lưu tổng cộng {len(df_all)} video unique vào {out_file.name}")


if __name__ == "__main__":
    main()
