"""BƯỚC 6 (V6): Khảo sát keyword Tam quốc trên web search (Bing/Brave qua ddgs).

Google scrape trực tiếp thường bị chặn; pipeline dùng ddgs thay thế.
Query ghép — mỗi query gắn anchor Tam quốc (xem tamquoc_keywords.GOOGLE_SEARCH_QUERIES).

Output:
  output/data/v6_google_results_raw.csv
  output/data/v6_google_content_types.csv
  output/data/v6_google_year_trend.csv
  output/data/v6_google_top_keywords.csv          — top 5 keyword Quan Vũ/Quan Công từ SERP
  output/data/v6_google_quan_search_queries.csv — 5 keyword cốt lõi cần search (spec V6)

Chạy lại phân loại (không crawl):
  python src/step6_google_search.py --reclassify-only
"""

import argparse
import io
import re
import sys
from collections import Counter
from datetime import datetime

import pandas as pd
from tqdm import tqdm

from google_client import iter_google_search
from google_content_classifier import (
    _domain,
    classify_content,
    is_valid_result,
)
from paths import DATA_DIR, ensure_data_dir
from tamquoc_keywords import (
    CANONICAL_TO_CATEGORY,
    GOOGLE_SEARCH_QUERIES,
    QUAN_CORE_SEARCH_KEYWORDS,
    is_quan_related,
    is_result_relevant,
    is_seed_keyword,
    match_tamquoc_keywords,
    query_is_quan_focused,
)

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

GOOGLE_NUM_RESULTS = 50
TOP_KEYWORDS = 5
MIN_YEAR = 2000
MAX_YEAR = datetime.now().year
YEAR_RE = re.compile(r"\b(20[0-2]\d|2000)\b")

RAW_COLUMNS = ["keyword", "title", "url", "description", "domain"]


def extract_years(text):
    if not isinstance(text, str):
        return []
    return [int(y) for y in YEAR_RE.findall(text) if MIN_YEAR <= int(y) <= MAX_YEAR]


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


def filter_valid(df_raw):
    """Lọc kết quả SERP rác (title/URL không hợp lệ)."""
    if df_raw.empty:
        return df_raw
    mask = df_raw.apply(
        lambda r: is_valid_result(
            r.get("url", ""), r.get("title", ""), r.get("description", "")
        ),
        axis=1,
    )
    filtered = df_raw[mask].reset_index(drop=True)
    dropped = len(df_raw) - len(filtered)
    print(f"[*] Lọc junk SERP: giữ {len(filtered)}/{len(df_raw)} (bỏ {dropped})")
    return filtered


def _write_empty_raw_diagnostic():
    raw_file = DATA_DIR / "v6_google_results_raw.csv"
    pd.DataFrame(columns=RAW_COLUMNS).to_csv(raw_file, index=False, encoding="utf-8-sig")
    print(f"[*] Đã ghi file diagnostic (rỗng): {raw_file.name}")


def build_content_types(df_raw):
    df = df_raw.copy()
    if "domain" not in df.columns:
        df["domain"] = df["url"].apply(_domain)
    df["content_type"] = df.apply(
        lambda r: classify_content(
            r.get("url", ""),
            r.get("title", ""),
            r.get("description", ""),
            r.get("domain", ""),
            r.get("keyword", ""),
        ),
        axis=1,
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

    print("\n=== PHÂN LOẠI NỘI DUNG (tổng hợp) ===")
    counts = df["content_type"].value_counts()
    total = len(df) or 1
    for ct, n in counts.items():
        print(f"  {ct}: {n} ({round(n / total * 100, 1)}%)")

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


def build_quan_search_queries():
    """Ghi 5 keyword cốt lõi Quan Vũ/Quan Công cần search (spec V6)."""
    rows = [
        {
            "stt": i,
            "keyword": kw,
            "category": CANONICAL_TO_CATEGORY.get(kw, "nhân_vật"),
            "ghi_chu": "keyword cốt lõi — search trực tiếp",
        }
        for i, kw in enumerate(QUAN_CORE_SEARCH_KEYWORDS, 1)
    ]
    df = pd.DataFrame(rows)
    df.to_csv(DATA_DIR / "v6_google_quan_search_queries.csv", index=False, encoding="utf-8-sig")
    return df


def build_top_keywords(df_raw):
    """Top 5 keyword Quan Vũ/Quan Công xuất hiện nhiều nhất trong SERP (trọng số query Quan x2)."""
    counter = Counter()
    quan_rows = 0
    for _, row in df_raw.iterrows():
        query = row.get("keyword", "")
        weight = 2 if query_is_quan_focused(query) else 1
        if weight > 1:
            quan_rows += 1
        text = f"{row.get('title', '')} {row.get('description', '')}"
        for canonical in match_tamquoc_keywords(text):
            if is_seed_keyword(canonical) or not is_quan_related(canonical):
                continue
            counter[canonical] += weight

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

    if df.empty:
        print("[!] Không đủ keyword Quan Vũ/Quan Công trong SERP — dùng danh sách cốt lõi.")
    else:
        by_cat = df.groupby("category").size()
        print("\n=== PHÂN LOẠI TOP KEYWORD QUAN (theo category) ===")
        for cat, n in by_cat.items():
            print(f"  {cat}: {n}")
    print(f"[*] Trọng số: {quan_rows}/{total_rows} kết quả từ query tập trung Quan (x2)")

    return df


def _process_pipeline(df_raw, write_raw=True):
    """Lọc + phân loại + xuất CSV phụ."""
    if write_raw:
        raw_file = DATA_DIR / "v6_google_results_raw.csv"
        df_raw.to_csv(raw_file, index=False, encoding="utf-8-sig")
        print(f"\n[OK] {len(df_raw)} kết quả → {raw_file.name}")

    _, summary = build_content_types(df_raw)
    print("\n=== PHÂN LOẠI NỘI DUNG (theo keyword) ===")
    print(summary.to_string(index=False))

    build_year_trend(df_raw)
    core_df = build_quan_search_queries()
    top_df = build_top_keywords(df_raw)

    print("\n=== 5 KEYWORD CỐT LÕI CẦN SEARCH (Quan Vũ / Quan Công) ===")
    print(core_df[["stt", "keyword", "category"]].to_string(index=False))

    print("\n=== TOP 5 KEYWORD QUAN VŨ / QUAN CÔNG TỪ SERP ===")
    if top_df.empty:
        print("  (chưa có — chạy crawl đầy đủ hoặc xem v6_google_quan_search_queries.csv)")
    else:
        print(top_df.to_string(index=False))
    print("\n[OK] Hoàn tất step6 — xem output/data/v6_google_*.csv")


def reclassify_only():
    """Đọc raw CSV đã crawl, áp classifier mới, không search lại."""
    ensure_data_dir()
    raw_file = DATA_DIR / "v6_google_results_raw.csv"
    if not raw_file.exists():
        print(f"[!] Không tìm thấy {raw_file.name} — chạy crawl đầy đủ trước.")
        sys.exit(1)

    df_raw = pd.read_csv(raw_file, encoding="utf-8-sig")
    if df_raw.empty:
        print("[!] File raw rỗng.")
        sys.exit(1)

    print(f"[*] Reclassify từ {raw_file.name} ({len(df_raw)} hàng)")
    df_raw = filter_valid(df_raw)
    if df_raw.empty:
        print("[!] Không còn kết quả sau lọc junk.")
        sys.exit(1)

    _process_pipeline(df_raw, write_raw=True)


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

    df_raw = filter_valid(df_raw)
    if df_raw.empty:
        print("[!] Không còn kết quả sau lọc junk.")
        _write_empty_raw_diagnostic()
        sys.exit(1)

    _process_pipeline(df_raw, write_raw=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 6 — khảo sát web search Tam quốc")
    parser.add_argument(
        "--reclassify-only",
        action="store_true",
        help="Phân loại lại từ v6_google_results_raw.csv (không crawl)",
    )
    args = parser.parse_args()
    if args.reclassify_only:
        reclassify_only()
    else:
        main()
