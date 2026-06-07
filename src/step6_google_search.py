"""BƯỚC 6 (V6): Khảo sát keyword Tam quốc trên web search (Bing/Brave qua ddgs).

Google scrape trực tiếp thường bị chặn; pipeline dùng ddgs thay thế.
Query ghép — mỗi query gắn anchor Tam quốc (xem tamquoc_keywords.GOOGLE_SEARCH_QUERIES).

Output:
  output/data/v6_google_results_raw.csv
  output/data/v6_google_content_types.csv
  output/data/v6_google_year_trend.csv
  output/data/v6_google_top_keywords.csv
"""

import io
import re
import sys
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
from tqdm import tqdm

from google_client import iter_google_search
from paths import DATA_DIR, ensure_data_dir
from tamquoc_keywords import (
    CANONICAL_TO_CATEGORY,
    GOOGLE_SEARCH_QUERIES,
    is_result_relevant,
    is_seed_keyword,
    match_tamquoc_keywords,
)

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

GOOGLE_NUM_RESULTS = 50
TOP_KEYWORDS = 15
MIN_YEAR = 2000
MAX_YEAR = datetime.now().year
YEAR_RE = re.compile(r"\b(20[0-2]\d|2000)\b")

CONTENT_TYPE_RULES = [
    ("Sách", ["goodreads", "nxb", "sách", "book", "wikipedia.org/wiki/sách", "amazon.com"]),
    ("Nghiên cứu", ["scholar.google", "researchgate", "academia.edu", ".edu/", "nghiên cứu"]),
    ("Báo cáo", [".gov", "báo cáo", "report", "whitepaper"]),
    ("Học thuật", ["doi.org", "journal", "tạp chí", "ieee.org", "springer.com"]),
    ("Giải trí", ["youtube.com", "tiktok.com", "game", "facebook.com", "reddit.com"]),
    ("Điện ảnh", ["imdb", "phim", "movie", "netflix", "letterboxd"]),
]


def _domain(url):
    try:
        host = urlparse(url).netloc.lower()
        return host.removeprefix("www.")
    except Exception:
        return ""


def classify_content(url, title, description):
    blob = f"{url} {title} {description}".lower()
    for label, signals in CONTENT_TYPE_RULES:
        if any(sig in blob for sig in signals):
            return label
    return "Khác"


def extract_years(text):
    if not isinstance(text, str):
        return []
    return [int(y) for y in YEAR_RE.findall(text) if MIN_YEAR <= int(y) <= MAX_YEAR]


RAW_COLUMNS = ["keyword", "title", "url", "description", "domain"]


def crawl_google():
    rows = []
    seen_urls: set[str] = set()
    per_keyword = {}
    for kw in GOOGLE_SEARCH_QUERIES:
        print(f"\n{'='*60}")
        print(f"[*] Web search: {kw} (max {GOOGLE_NUM_RESULTS})")
        print(f"{'='*60}")
        added = 0
        try:
            for r in tqdm(
                iter_google_search(kw, num_results=GOOGLE_NUM_RESULTS),
                desc=kw,
                total=GOOGLE_NUM_RESULTS,
            ):
                if r.url in seen_urls:
                    continue
                seen_urls.add(r.url)
                rows.append({
                    "keyword": kw,
                    "title": r.title,
                    "url": r.url,
                    "description": r.description,
                    "domain": _domain(r.url),
                })
                added += 1
        except Exception as e:
            print(f"[!] Lỗi search '{kw}': {str(e)[:120]}")
        per_keyword[kw] = added
        print(f"[*] '{kw}': {added} kết quả mới (dedupe URL)")
    return pd.DataFrame(rows), per_keyword


def filter_relevant(df_raw):
    """Lọc kết quả không liên quan Tam quốc."""
    if df_raw.empty:
        return df_raw
    mask = df_raw.apply(
        lambda r: is_result_relevant(
            r.get("title", ""), r.get("description", ""), r.get("keyword", "")
        ),
        axis=1,
    )
    filtered = df_raw[mask].reset_index(drop=True)
    dropped = len(df_raw) - len(filtered)
    print(f"[*] Lọc relevance: giữ {len(filtered)}/{len(df_raw)} (bỏ {dropped})")
    return filtered


def _write_empty_raw_diagnostic():
    raw_file = DATA_DIR / "v6_google_results_raw.csv"
    pd.DataFrame(columns=RAW_COLUMNS).to_csv(raw_file, index=False, encoding="utf-8-sig")
    print(f"[*] Đã ghi file diagnostic (rỗng): {raw_file.name}")


def build_content_types(df_raw):
    df = df_raw.copy()
    df["content_type"] = df.apply(
        lambda r: classify_content(r["url"], r["title"], r["description"]), axis=1
    )
    df.to_csv(DATA_DIR / "v6_google_content_types.csv", index=False, encoding="utf-8-sig")

    summary = (
        df.groupby(["keyword", "content_type"])
        .size()
        .reset_index(name="so_ket_qua")
    )
    totals = df.groupby("keyword").size().to_dict()
    summary["ty_le_pct"] = summary.apply(
        lambda r: round(r["so_ket_qua"] / totals[r["keyword"]] * 100, 2), axis=1
    )
    return df, summary


def build_year_trend(df_raw):
    year_counts = Counter()
    matched = 0
    for _, row in df_raw.iterrows():
        text = f"{row.get('title', '')} {row.get('description', '')}"
        years = extract_years(text)
        if years:
            matched += 1
            for y in years:
                year_counts[y] += 1

    total = sum(year_counts.values()) or 1
    rows = [
        {"nam": y, "so_ket_qua": c, "ty_le_pct": round(c / total * 100, 2)}
        for y, c in sorted(year_counts.items())
    ]
    df = pd.DataFrame(rows)
    df.to_csv(DATA_DIR / "v6_google_year_trend.csv", index=False, encoding="utf-8-sig")
    print(f"[*] Xu thế năm ({MIN_YEAR}–{MAX_YEAR}): {matched}/{len(df_raw)} kết quả có năm trong text")
    return df


def build_top_keywords(df_raw):
    counter = Counter()
    for _, row in df_raw.iterrows():
        text = f"{row.get('title', '')} {row.get('description', '')}"
        for canonical in match_tamquoc_keywords(text):
            if is_seed_keyword(canonical):
                continue
            counter[canonical] += 1

    total_rows = len(df_raw) or 1
    top = counter.most_common(TOP_KEYWORDS)
    rows = []
    for i, (kw, cnt) in enumerate(top, 1):
        rows.append({
            "stt": i,
            "keyword": kw,
            "category": CANONICAL_TO_CATEGORY.get(kw, "khác"),
            "ty_le_xuat_hien": cnt,
            "ty_le_pct": round(cnt / total_rows * 100, 2),
        })
    df = pd.DataFrame(rows)
    df.to_csv(DATA_DIR / "v6_google_top_keywords.csv", index=False, encoding="utf-8-sig")

    if not df.empty and "category" in df.columns:
        by_cat = df.groupby("category").size()
        print("\n=== PHÂN LOẠI TOP KEYWORD (theo category) ===")
        for cat, n in by_cat.items():
            print(f"  {cat}: {n}")

    return df


def main():
    ensure_data_dir()
    df_raw, per_keyword = crawl_google()

    print("\n=== TÓM TẮT KẾT QUẢ THEO KEYWORD (trước lọc) ===")
    for kw, cnt in per_keyword.items():
        print(f"  {kw}: {cnt}")
    print(f"  Tổng (dedupe URL): {len(df_raw)}")

    if df_raw.empty:
        print("[!] Không thu được kết quả tìm kiếm nào.")
        _write_empty_raw_diagnostic()
        sys.exit(1)

    df_raw = filter_relevant(df_raw)
    if df_raw.empty:
        print("[!] Không còn kết quả sau lọc relevance.")
        _write_empty_raw_diagnostic()
        sys.exit(1)

    raw_file = DATA_DIR / "v6_google_results_raw.csv"
    df_raw.to_csv(raw_file, index=False, encoding="utf-8-sig")
    print(f"\n[OK] {len(df_raw)} kết quả → {raw_file.name}")

    _, summary = build_content_types(df_raw)
    print("\n=== PHÂN LOẠI NỘI DUNG (theo keyword) ===")
    print(summary.to_string(index=False))

    build_year_trend(df_raw)
    top_df = build_top_keywords(df_raw)
    print("\n=== TOP 15 KEYWORD TAM QUỐC LIÊN QUAN ===")
    print(top_df.to_string(index=False))
    print("\n[OK] Hoàn tất step6 — xem output/data/v6_google_*.csv")


if __name__ == "__main__":
    main()
