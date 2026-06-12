"""Phân tích V7 — phân loại nội dung & xu thế năm theo 5 keyword cốt lõi Quan."""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime

import pandas as pd

from google_content_classifier import _domain, classify_content
from paths import DATA_DIR
from tamquoc_keywords import resolve_core_keyword

MIN_YEAR = 2000
MAX_YEAR = datetime.now().year
YEAR_RE = re.compile(r"\b(20[0-2]\d|2000)\b")


def extract_years(text: str) -> list[int]:
    if not isinstance(text, str):
        return []
    return [int(y) for y in YEAR_RE.findall(text) if MIN_YEAR <= int(y) <= MAX_YEAR]


def enrich_results(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Thêm core_keyword, content_type, nam cho từng kết quả SERP."""
    if df_raw.empty:
        return pd.DataFrame(columns=[
            "keyword", "core_keyword", "title", "url", "domain", "content_type", "nam",
        ])

    df = df_raw.copy()
    if "domain" not in df.columns:
        df["domain"] = df["url"].apply(_domain)

    df["core_keyword"] = df["keyword"].apply(resolve_core_keyword)
    df = df[df["core_keyword"].notna()].reset_index(drop=True)

    if df.empty:
        return df

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

    def _first_year(row) -> int | None:
        years = extract_years(f"{row.get('title', '')} {row.get('description', '')}")
        return years[0] if years else None

    df["nam"] = df.apply(_first_year, axis=1)
    return df


def build_keyword_content_types(df_enriched: pd.DataFrame) -> pd.DataFrame:
    """Mục 2 — groupby core_keyword × content_type."""
    if df_enriched.empty:
        return pd.DataFrame(columns=["core_keyword", "content_type", "so_ket_qua", "ty_le_pct"])

    grouped = (
        df_enriched.groupby(["core_keyword", "content_type"])
        .size()
        .reset_index(name="so_ket_qua")
    )
    totals = df_enriched.groupby("core_keyword").size().to_dict()
    grouped["ty_le_pct"] = grouped.apply(
        lambda r: round(r["so_ket_qua"] / totals[r["core_keyword"]] * 100, 2),
        axis=1,
    )
    return grouped.sort_values(["core_keyword", "so_ket_qua"], ascending=[True, False])


def build_year_content_trend(df_enriched: pd.DataFrame) -> pd.DataFrame:
    """Mục 3 — groupby nam × content_type (explode tất cả năm trong text)."""
    if df_enriched.empty:
        return pd.DataFrame(columns=["nam", "content_type", "so_ket_qua", "ty_le_pct"])

    counter: Counter[tuple[int, str]] = Counter()
    for _, row in df_enriched.iterrows():
        text = f"{row.get('title', '')}"
        if "description" in row and pd.notna(row.get("description")):
            text = f"{text} {row.get('description', '')}"
        years = extract_years(text)
        if not years:
            continue
        ct = row.get("content_type", "Khác")
        for y in years:
            counter[(y, ct)] += 1

    if not counter:
        return pd.DataFrame(columns=["nam", "content_type", "so_ket_qua", "ty_le_pct"])

    total = sum(counter.values())
    rows = [
        {
            "nam": y,
            "content_type": ct,
            "so_ket_qua": c,
            "ty_le_pct": round(c / total * 100, 2),
        }
        for (y, ct), c in sorted(counter.items())
    ]
    return pd.DataFrame(rows)


def write_v7_outputs(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Enrich, build bảng V7, ghi CSV."""
    enriched = enrich_results(df_raw)
    kw_ct = build_keyword_content_types(enriched)
    yr_ct = build_year_content_trend(enriched)

    out_cols = ["keyword", "core_keyword", "title", "url", "domain", "content_type", "nam"]
    enriched[out_cols].to_csv(
        DATA_DIR / "v7_google_results_enriched.csv", index=False, encoding="utf-8-sig",
    )
    kw_ct.to_csv(DATA_DIR / "v7_google_keyword_content_types.csv", index=False, encoding="utf-8-sig")
    yr_ct.to_csv(DATA_DIR / "v7_google_year_content_trend.csv", index=False, encoding="utf-8-sig")

    print(f"\n=== V7 PHÂN LOẠI THEO KEYWORD CỐT LÕI ({len(enriched)} kết quả) ===")
    if kw_ct.empty:
        print("  (không có dữ liệu — kiểm tra query map về 5 keyword cốt lõi)")
    else:
        for core in kw_ct["core_keyword"].unique():
            sub = kw_ct[kw_ct["core_keyword"] == core]
            print(f"\n  [{core}]")
            for _, r in sub.iterrows():
                print(f"    {r['content_type']}: {r['so_ket_qua']} ({r['ty_le_pct']}%)")

    print(f"\n=== V7 XU THẾ NĂM × LOẠI NỘI DUNG ===")
    if yr_ct.empty:
        print("  (không trích được năm từ SERP)")
    else:
        peak = yr_ct.loc[yr_ct["so_ket_qua"].idxmax()]
        print(f"  Peak: năm {int(peak['nam'])} — {peak['content_type']} ({peak['so_ket_qua']} lần)")
        print(f"  → v7_google_keyword_content_types.csv, v7_google_year_content_trend.csv")

    return enriched, kw_ct, yr_ct
