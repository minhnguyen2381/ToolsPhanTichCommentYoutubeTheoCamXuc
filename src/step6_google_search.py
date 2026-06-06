"""BƯỚC 6 (V6): Khảo sát 5 keyword trên web search (Bing/Brave qua ddgs).

Google scrape trực tiếp thường bị chặn; pipeline dùng ddgs thay thế.

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
from urllib.parse import urlparse

import pandas as pd
from tqdm import tqdm

from google_client import iter_google_search
from paths import DATA_DIR, ensure_data_dir

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

KEYWORDS = [
    "Quan Công",
    "Quan Vũ",
    "Quan Thánh",
    "Quan Thánh Đế Quân",
    "Quan Vân Trường",
]

GOOGLE_NUM_RESULTS = 100
TOP_KEYWORDS = 15
YEAR_RE = re.compile(r"\b(1980|198[1-9]|199\d|20[0-2]\d)\b")

CONTENT_TYPE_RULES = [
    ("Sách", ["goodreads", "nxb", "sách", "book", "wikipedia.org/wiki/sách", "amazon.com"]),
    ("Nghiên cứu", ["scholar.google", "researchgate", "academia.edu", ".edu/", "nghiên cứu"]),
    ("Báo cáo", [".gov", "báo cáo", "report", "whitepaper"]),
    ("Học thuật", ["doi.org", "journal", "tạp chí", "ieee.org", "springer.com"]),
    ("Giải trí", ["youtube.com", "tiktok.com", "game", "facebook.com", "reddit.com"]),
    ("Điện ảnh", ["imdb", "phim", "movie", "netflix", "letterboxd"]),
]

STOPWORDS = {
    "và", "của", "là", "có", "trong", "với", "một", "các", "được", "cho", "từ",
    "the", "a", "an", "of", "in", "on", "to", "for", "is", "are", "was", "were",
    "quan", "công", "vũ", "thánh", "vân", "trường", "đế", "quân", "guan", "yu",
}


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
    return [int(y) for y in YEAR_RE.findall(text) if 1980 <= int(y) <= 2026]


def _tokenize(text):
    if not isinstance(text, str):
        return []
    text = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = text.split()
    return [t for t in tokens if len(t) > 2 and t not in STOPWORDS]


def _bigrams(tokens):
    return [" ".join(tokens[i : i + 2]) for i in range(len(tokens) - 1)]


RAW_COLUMNS = ["keyword", "title", "url", "description", "domain"]


def crawl_google():
    rows = []
    per_keyword = {}
    for kw in KEYWORDS:
        print(f"\n{'='*60}")
        print(f"[*] Web search: {kw} (max {GOOGLE_NUM_RESULTS})")
        print(f"{'='*60}")
        before = len(rows)
        try:
            for r in tqdm(
                iter_google_search(kw, num_results=GOOGLE_NUM_RESULTS),
                desc=kw,
                total=GOOGLE_NUM_RESULTS,
            ):
                rows.append({
                    "keyword": kw,
                    "title": r.title,
                    "url": r.url,
                    "description": r.description,
                    "domain": _domain(r.url),
                })
        except Exception as e:
            print(f"[!] Lỗi search '{kw}': {str(e)[:120]}")
        per_keyword[kw] = len(rows) - before
        print(f"[*] '{kw}': {per_keyword[kw]} kết quả")
    return pd.DataFrame(rows), per_keyword


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
    print(f"[*] Xu thế năm: {matched}/{len(df_raw)} kết quả có năm trong text")
    return df


def build_top_keywords(df_raw):
    counter = Counter()
    for _, row in df_raw.iterrows():
        text = f"{row.get('title', '')} {row.get('description', '')}"
        tokens = _tokenize(text)
        for tok in tokens:
            counter[tok] += 1
        for bg in _bigrams(tokens):
            counter[bg] += 1

    seed_lower = {k.lower() for k in KEYWORDS}
    for kw in seed_lower:
        counter.pop(kw, None)
        for part in kw.split():
            counter.pop(part, None)

    total = sum(counter.values()) or 1
    top = counter.most_common(TOP_KEYWORDS)
    rows = []
    for i, (kw, cnt) in enumerate(top, 1):
        rows.append({
            "stt": i,
            "keyword": kw,
            "ty_le_xuat_hien": cnt,
            "ty_le_pct": round(cnt / total * 100, 2),
        })
    df = pd.DataFrame(rows)
    df.to_csv(DATA_DIR / "v6_google_top_keywords.csv", index=False, encoding="utf-8-sig")
    return df


def main():
    ensure_data_dir()
    df_raw, per_keyword = crawl_google()

    print("\n=== TÓM TẮT KẾT QUẢ THEO KEYWORD ===")
    for kw, cnt in per_keyword.items():
        print(f"  {kw}: {cnt}")
    print(f"  Tổng: {len(df_raw)}")

    if df_raw.empty:
        print("[!] Không thu được kết quả tìm kiếm nào.")
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
    print("\n=== TOP 15 KEYWORD LIÊN QUAN ===")
    print(top_df.to_string(index=False))
    print("\n[OK] Hoàn tất step6 — xem output/data/v6_google_*.csv")


if __name__ == "__main__":
    main()
