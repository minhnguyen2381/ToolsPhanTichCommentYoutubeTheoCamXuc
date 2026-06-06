"""Chạy toàn bộ pipeline: step1 → ... → step10."""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent

STEPS = [
    #("Bước 1 — Cào 3000 video Youtube", "step1_keyword_stats.py"),
    ("Bước 2 — Lọc data rác (blacklist/whitelist)", "step2_clean_raw_data.py"),
    ("Bước 3 — Lọc video liên quan (Keyword + AI)", "step3_filter_videos.py"),
    ("Bước 4 — Phân loại chủ đề và vẽ biểu đồ video", "step4_visualize_videos.py"),
    ("Bước 5 — Thống kê kênh YouTube", "step5_channel_stats.py"),
    ("Bước 6 — Khảo sát Google keyword", "step6_google_search.py"),
    ("Bước 7 — Trực quan hóa kênh & Google", "step7_visualize_v6.py"),
    ("Bước 8 — Crawl comment playlist", "step8_crawl_comments.py"),
    ("Bước 9 — Phân tích sentiment", "step9_sentiment_analysis.py"),
    ("Bước 10 — Phân loại tính cách và vẽ biểu đồ", "step10_visualize_sentiment.py"),
]

def main():
    for name, script in STEPS:
        print("\n" + "=" * 60)
        print(f"▶ {name}")
        print("=" * 60)
        ret = subprocess.call([sys.executable, str(SRC / script)])
        if ret != 0:
            print(f"[FAIL] {script} trả về mã {ret}. Dừng pipeline.")
            sys.exit(ret)
    print("\n[DONE] Pipeline hoàn tất. Xem data/ và report/{vi,en,zh}/.")


if __name__ == "__main__":
    main()
