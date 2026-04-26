"""BƯỚC 3 (V4): Lọc keyword tính cách Quan Vũ + tạo bảng biểu tỷ lệ %.

Đọc comments đã crawl, tìm keyword tính cách, tính tỷ lệ %,
xuất CSV kết quả. Biểu đồ được tạo bởi visualize.py.
"""
import sys
from pathlib import Path
from collections import Counter

import pandas as pd
from tqdm import tqdm

from normalize import normalize

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Danh sách keyword tính cách Quan Vũ
# ---------------------------------------------------------------------------
PERSONALITY_POSITIVE = {
    "trượng nghĩa": "Trượng nghĩa",
    "nghĩa khí": "Nghĩa khí",
    "trung thành": "Trung thành",
    "trung nghĩa": "Trung nghĩa",
    "nhân nghĩa": "Nhân nghĩa",
    "dũng cảm": "Dũng cảm",
    "anh hùng": "Anh hùng",
    "can trường": "Can trường",
    "oai phong": "Oai phong",
    "uy vũ": "Uy vũ",
    "nghĩa hiệp": "Nghĩa hiệp",
    "nghĩa sĩ": "Nghĩa sĩ",
    "trung liệt": "Trung liệt",
    "hào kiệt": "Hào kiệt",
    "liêm chính": "Liêm chính",
    "khí phách": "Khí phách",
    "trung trinh": "Trung trinh",
    "tài giỏi": "Tài giỏi",
    "võ thánh": "Võ thánh",
    "trung": "Trung (trung thành)",
    "nghĩa": "Nghĩa (nhân nghĩa)",
    "dũng": "Dũng (dũng cảm)",
    "trí dũng": "Trí dũng",
    "trượng phu": "Trượng phu",
    "nghĩa trọng": "Nghĩa trọng",
    "tín nghĩa": "Tín nghĩa",
    "oai hùng": "Oai hùng",
    "uy phong": "Uy phong",
    "nghĩa đảm": "Nghĩa đảm",
    "trung can": "Trung can",
}

PERSONALITY_NEGATIVE = {
    "kiêu ngạo": "Kiêu ngạo",
    "nóng tính": "Nóng tính",
    "tự phụ": "Tự phụ",
    "khinh địch": "Khinh địch",
    "chủ quan": "Chủ quan",
    "ngạo mạn": "Ngạo mạn",
    "cố chấp": "Cố chấp",
    "bảo thủ": "Bảo thủ",
    "ngang tàng": "Ngang tàng",
    "ương bướng": "Ương bướng",
    "đoản mệnh": "Đoản mệnh",
    "khinh người": "Khinh người",
    "coi thường": "Coi thường",
    "kiêu căng": "Kiêu căng",
    "tự cao": "Tự cao",
    "nóng nảy": "Nóng nảy",
    "khinh suất": "Khinh suất",
    "bất cẩn": "Bất cẩn",
    "ngạo nghễ": "Ngạo nghễ",
    "cao ngạo": "Cao ngạo",
}


def count_personality_keywords(texts):
    """Đếm số lần xuất hiện mỗi keyword tính cách."""
    counter = Counter()
    all_keywords = {}
    all_keywords.update(PERSONALITY_POSITIVE)
    all_keywords.update(PERSONALITY_NEGATIVE)

    for text in tqdm(texts, desc="Tìm keyword tính cách"):
        if not text:
            continue
        text_lower = text.lower()
        for kw in all_keywords:
            count = text_lower.count(kw)
            if count > 0:
                counter[kw] += count
    return counter


def main():
    # --- Load comments ---
    comments_file = DATA_DIR / "v4_comments_raw.csv"
    if not comments_file.exists():
        raise SystemExit(
            f"[!] Không tìm thấy {comments_file}. Chạy step2 trước."
        )

    df = pd.read_csv(comments_file)
    print(f"[*] Đọc {len(df)} comments từ v4_comments_raw.csv")

    # --- Normalize ---
    print("[*] Normalize comments...")
    texts = [normalize(t) for t in tqdm(df["text"].fillna(""), desc="Normalize")]

    # --- Đếm keyword tính cách ---
    print("[*] Đếm keyword tính cách Quan Vũ...")
    counter = count_personality_keywords(texts)

    if not counter:
        print("[!] Không tìm thấy keyword tính cách nào trong comments.")
        return

    # --- Tạo DataFrame kết quả ---
    total_hits = sum(counter.values())
    rows = []
    for kw, count in counter.most_common():
        category = "Tích cực" if kw in PERSONALITY_POSITIVE else "Tiêu cực"
        display_name = (
            PERSONALITY_POSITIVE.get(kw) or PERSONALITY_NEGATIVE.get(kw, kw)
        )
        rows.append({
            "keyword": kw,
            "display_name": display_name,
            "count": count,
            "percentage": round(count / total_hits * 100, 2),
            "category": category,
        })

    df_result = pd.DataFrame(rows)
    df_result.to_csv(DATA_DIR / "v4_personality_keywords.csv",
                     index=False, encoding="utf-8-sig")

    # --- In bảng tổng kết ---
    print(f"\n{'='*70}")
    print(f"=== KEYWORD TÍNH CÁCH QUAN VŨ ({total_hits} lần xuất hiện) ===")
    print(f"{'='*70}")
    print(df_result[["display_name", "count", "percentage", "category"]]
          .to_string(index=False))

    # Tổng hợp
    pos_count = df_result[df_result["category"] == "Tích cực"]["count"].sum()
    neg_count = df_result[df_result["category"] == "Tiêu cực"]["count"].sum()
    pos_pct = round(pos_count / total_hits * 100, 1) if total_hits else 0
    neg_pct = round(neg_count / total_hits * 100, 1) if total_hits else 0

    print(f"\n{'='*70}")
    print(f"=== TỔNG HỢP ===")
    print(f"  Tích cực : {pos_count:>5} lần ({pos_pct}%)")
    print(f"  Tiêu cực : {neg_count:>5} lần ({neg_pct}%)")
    print(f"  Tổng     : {total_hits:>5} lần")
    print(f"{'='*70}")
    print(f"\n[OK] Đã lưu data/v4_personality_keywords.csv")


if __name__ == "__main__":
    main()
