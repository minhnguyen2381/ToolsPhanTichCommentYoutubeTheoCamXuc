"""BƯỚC 1: Khảo sát độ phổ biến của từ khoá trên YouTube (dùng yt-dlp)."""
import time
from pathlib import Path
import pandas as pd
from youtube_client import search_videos, get_video_stats

KEYWORDS = ["Quan Vũ", "Quan Vân Trường", "Quan Công", "Quan Thánh"]
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def main():
    summary = []
    for kw in KEYWORDS:
        print(f"[*] Tìm kiếm: {kw}")
        ids = search_videos(kw, max_results=50)
        print(f"  → {len(ids)} video, đang lấy thống kê...")
        rows = get_video_stats(ids)
        df = pd.DataFrame(rows)
        safe_name = kw.replace(" ", "_")
        df.to_csv(DATA_DIR / f"keyword_{safe_name}.csv",
                  index=False, encoding="utf-8-sig")
        summary.append({
            "keyword": kw,
            "top50_total_views": int(df["views"].sum()) if not df.empty else 0,
            "top50_avg_views": int(df["views"].mean()) if not df.empty else 0,
            "top50_total_likes": int(df["likes"].sum()) if not df.empty else 0,
            "top50_total_comments": int(df["comments"].sum()) if not df.empty else 0,
        })
        time.sleep(0.2)

    out = pd.DataFrame(summary)
    out.to_csv(DATA_DIR / "keyword_summary.csv",
               index=False, encoding="utf-8-sig")
    print("\n=== Tóm tắt ===")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
