"""Chạy toàn bộ pipeline: step1 → ... → stepN."""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent

STEPS = [
    #("Bước 1 — Cào 3000 video Youtube và phân loại", "step1_keyword_stats.py"),
    ("Bước 1b — Lọc data rác (blacklist/whitelist)", "step1b_clean_raw_data.py"),
    ("Bước 2 — Lọc video liên quan (Keyword + AI Embeddings)", "step2_filter_3000_videos.py"),
    ("Bước 3 — Phân loại 9 chủ đề và vẽ biểu đồ", "step3_visualize_3000_video.py"),
    #("Bước 4 — Crawl comment playlist", "step4_crawl_comments.py"),
    ("Bước 5 — Phân tích sentiment trên mẫu video playlist", "step5_sentiment_analysis.py"),
    ("Bước 6 — Phân loại tính cách và vẽ biểu đồ", "step6_visualize.py"),
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
    print("\n[DONE] Pipeline hoàn tất. Xem thư mục data/ và report/.")


if __name__ == "__main__":
    main()
