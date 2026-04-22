"""Chạy toàn bộ pipeline: step1 → step2 → step3 → visualize."""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent

STEPS = [
    ("Bước 1 — Khảo sát keyword", "step1_keyword_stats.py"),
    ("Bước 2 — Crawl comment playlist", "step2_crawl_comments.py"),
    ("Bước 3 — Phân tích sentiment", "step3_sentiment.py"),
    ("Bước 4 — Vẽ biểu đồ", "visualize.py"),
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
