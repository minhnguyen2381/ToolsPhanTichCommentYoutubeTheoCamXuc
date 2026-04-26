"""BƯỚC 2 (V4): Crawl comments từ top video + trích xuất keyword phổ biến.

Cải tiến V4:
- Input từ v4_video_topics.csv (output step1)
- Chọn top 30 video nhiều comment nhất
- Trích xuất keyword bằng underthesea + loại stopwords
"""
import sys
import time
from pathlib import Path
from collections import Counter

import pandas as pd
from tqdm import tqdm

from youtube_client import iter_comments
from normalize import normalize

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TOP_N_VIDEOS = 30
MAX_COMMENTS_PER_VIDEO = 2000

# ---------------------------------------------------------------------------
# Stopwords tiếng Việt cơ bản
# ---------------------------------------------------------------------------
STOPWORDS_VI = {
    "và", "của", "là", "có", "được", "cho", "này", "đó", "để", "trong",
    "với", "từ", "một", "không", "những", "các", "đã", "cũng", "người",
    "về", "thì", "nhưng", "hay", "như", "mà", "nếu", "khi", "tôi", "bạn",
    "ông", "anh", "em", "chị", "họ", "mình", "ra", "vào", "lên", "xuống",
    "đi", "đến", "lại", "rồi", "thế", "vậy", "nào", "gì", "ấy", "đây",
    "lắm", "rất", "quá", "nhiều", "ít", "hơn", "nhất", "nên", "bị", "phải",
    "sẽ", "còn", "chỉ", "làm", "biết", "thấy", "nói", "bảo", "xem",
    "nghe", "hiểu", "muốn", "cần", "theo", "tại", "vì", "do", "qua",
    "sau", "trước", "trên", "dưới", "giữa", "bên", "ngoài", "lúc",
    "đều", "chưa", "sao", "thật", "đúng", "nhỉ", "ạ", "à", "ơi", "hả",
    "nhé", "nha", "luôn", "ngay", "mới", "cái", "con", "thằng", "bao",
    "video", "clip", "youtube", "channel", "subscribe", "like",
    "ok", "oke", "the", "and", "is", "of", "to", "in", "it", "that",
    "this", "you", "he", "she", "we", "they", "my", "your", "his", "her",
    "tích_cực", "tiêu_cực", "hài_hước",  # token emoji
}


def extract_keywords(texts):
    """Trích xuất và đếm tần suất keyword từ danh sách text đã normalize."""
    from underthesea import word_tokenize

    counter = Counter()
    for text in tqdm(texts, desc="Tokenize & count"):
        if not text or not text.strip():
            continue
        tokens = word_tokenize(text, format="text").split()
        for token in tokens:
            token_clean = token.lower().strip()
            if len(token_clean) < 2:
                continue
            if token_clean in STOPWORDS_VI:
                continue
            if token_clean.isdigit():
                continue
            counter[token_clean] += 1
    return counter


def main():
    # --- Load video list từ step1 ---
    topics_file = DATA_DIR / "v4_video_topics.csv"
    if not topics_file.exists():
        raise SystemExit(
            f"[!] Không tìm thấy {topics_file}. Chạy step1 trước."
        )

    df_videos = pd.read_csv(topics_file)
    print(f"[*] Đọc {len(df_videos)} video từ v4_video_topics.csv")

    # --- Chọn top N video nhiều comment nhất ---
    df_sorted = df_videos.sort_values("comments", ascending=False)
    df_top = df_sorted.head(TOP_N_VIDEOS)
    print(f"[*] Chọn top {len(df_top)} video nhiều comment nhất:")
    for _, row in df_top.iterrows():
        print(f"  {row['videoId']} | {row['comments']:>6} cmt | {row['title'][:60]}")

    # --- Crawl comments ---
    all_comments = []
    video_ids = df_top["videoId"].tolist()

    for idx, vid in enumerate(video_ids, 1):
        print(f"\n[{idx}/{len(video_ids)}] Crawl comments: {vid}")
        cmts = list(iter_comments(vid, max_comments=MAX_COMMENTS_PER_VIDEO))
        print(f"  → {len(cmts)} comments")
        all_comments.extend(cmts)
        time.sleep(0.2)

    df_comments = pd.DataFrame(all_comments)
    df_comments.to_csv(DATA_DIR / "v4_comments_raw.csv",
                       index=False, encoding="utf-8-sig")
    print(f"\n[OK] Tổng {len(df_comments)} comments → data/v4_comments_raw.csv")

    # --- Normalize comments ---
    print(f"\n[*] Normalize {len(df_comments)} comments...")
    normalized_texts = [
        normalize(t) for t in tqdm(
            df_comments["text"].fillna(""), desc="Normalize"
        )
    ]

    # --- Trích xuất keyword ---
    print(f"\n[*] Trích xuất keyword...")
    keyword_counter = extract_keywords(normalized_texts)

    # --- Lưu kết quả ---
    total_keywords = sum(keyword_counter.values())
    top_keywords = keyword_counter.most_common(500)

    df_kw = pd.DataFrame(top_keywords, columns=["keyword", "count"])
    df_kw["percentage"] = (df_kw["count"] / total_keywords * 100).round(3)
    df_kw.to_csv(DATA_DIR / "v4_keyword_frequency.csv",
                 index=False, encoding="utf-8-sig")

    print(f"\n{'='*60}")
    print(f"=== TOP 50 KEYWORD ({total_keywords} tổng từ) ===")
    print(f"{'='*60}")
    print(df_kw.head(50).to_string(index=False))
    print(f"\n[OK] Đã lưu data/v4_keyword_frequency.csv (top 500)")


if __name__ == "__main__":
    main()
