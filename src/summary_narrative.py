"""Sinh báo cáo Markdown ngôn ngữ tự nhiên từ dữ liệu V6 (kênh YouTube + Google)."""

from pathlib import Path

import pandas as pd

from i18n_charts import (
    NARRATIVE_TEXT,
    SUMMARY_TEXT,
    account_type_label,
    content_type_label,
    fmt_dot,
    google_category_label,
    google_keyword_label,
)

_COL_RENAME_KEYS = (
    "ten_tai_khoan", "loai_tai_khoan", "so_luong_video", "ty_le_pct",
    "keyword", "content_type", "title", "url", "nam", "so_ket_qua", "ty_le_xuat_hien",
    "category",
)


def rename_summary_columns(df, locale):
    if df is None or df.empty:
        return df
    st = SUMMARY_TEXT[locale]
    rename = {col: st[f"col_{col}"] for col in _COL_RENAME_KEYS if col in df.columns}
    out = df.copy()
    if "loai_tai_khoan" in out.columns:
        out["loai_tai_khoan"] = out["loai_tai_khoan"].apply(
            lambda s: account_type_label(s, locale)
        )
    if "keyword" in out.columns:
        out["keyword"] = out["keyword"].apply(
            lambda k: google_keyword_label(k, locale)
        )
    if "category" in out.columns:
        out["category"] = out["category"].apply(
            lambda c: google_category_label(c, locale)
        )
    if "content_type" in out.columns:
        out["content_type"] = out["content_type"].apply(
            lambda v: content_type_label(v, locale)
        )
    return out.rename(columns=rename)


def build_summary_tables(df_ch, df_ct, df_yr, df_kw, locale):
    st = SUMMARY_TEXT[locale]
    ch_display = (
        df_ch[["ten_tai_khoan", "loai_tai_khoan", "so_luong_video", "ty_le_pct"]]
        if not df_ch.empty else df_ch
    )
    if not df_ct.empty and "keyword" in df_ct.columns:
        ct_display = df_ct[["keyword", "content_type", "title", "url"]].head(50)
    elif not df_ct.empty:
        ct_display = df_ct.head(50)
    else:
        ct_display = df_ct
    return [
        (st["section_channels"], ch_display),
        (st["section_google_content"], ct_display),
        (st["section_year_trend"], df_yr),
        (st["section_top_keywords"], df_kw),
    ]


def _fmt_pct(value):
    return f"{float(value):.1f}"


def _join_items(items, join_key, nt):
    return nt[join_key].join(items)


def _df_to_markdown_table(df):
    if df is None or df.empty:
        return ""
    display = df.astype(str).map(lambda v: str(v).replace("|", "\\|"))
    headers = "| " + " | ".join(display.columns) + " |"
    sep = "| " + " | ".join("---" for _ in display.columns) + " |"
    rows = [
        "| " + " | ".join(row) + " |"
        for row in display.itertuples(index=False, name=None)
    ]
    return "\n".join([headers, sep, *rows])


def _compute_summary_metrics(df_ch, df_ct, df_yr, df_kw, locale):
    metrics = {}

    if not df_ch.empty:
        metrics["has_channels"] = True
        metrics["total_channels"] = len(df_ch)
        top = df_ch.nlargest(1, "so_luong_video").iloc[0]
        metrics["top_channel"] = top["ten_tai_khoan"]
        metrics["top_videos"] = fmt_dot(top["so_luong_video"])
        metrics["top_pct"] = _fmt_pct(top.get("ty_le_pct", 0))

        top3 = df_ch.nlargest(3, "so_luong_video")
        metrics["top3_channels"] = [
            {
                "name": row["ten_tai_khoan"],
                "videos": fmt_dot(row["so_luong_video"]),
                "pct": _fmt_pct(row.get("ty_le_pct", 0)),
            }
            for _, row in top3.iterrows()
        ]

        type_sums = df_ch.groupby("loai_tai_khoan")["so_luong_video"].sum()
        total_videos = int(type_sums.sum()) or 1
        metrics["account_types"] = [
            {
                "slug": slug,
                "videos": fmt_dot(videos),
                "pct": round(100.0 * videos / total_videos, 1),
            }
            for slug, videos in type_sums.items()
        ]
    else:
        metrics["has_channels"] = False

    if not df_ct.empty and "content_type" in df_ct.columns:
        metrics["has_content"] = True
        counts = df_ct.groupby("content_type").size().sort_values(ascending=False)
        total = int(counts.sum()) or 1
        metrics["total_content"] = fmt_dot(total)
        metrics["top_content_types"] = [
            {
                "type": content_type_label(content_type, locale),
                "count": fmt_dot(count),
                "pct": round(100.0 * count / total, 1),
            }
            for content_type, count in counts.head(3).items()
        ]
    else:
        metrics["has_content"] = False

    if not df_yr.empty and "nam" in df_yr.columns and "so_ket_qua" in df_yr.columns:
        metrics["has_year"] = True
        df_sorted = df_yr.sort_values("nam")
        peak_row = df_yr.loc[df_yr["so_ket_qua"].idxmax()]
        metrics["peak_year"] = int(peak_row["nam"])
        metrics["peak_count"] = fmt_dot(peak_row["so_ket_qua"])

        if len(df_sorted) >= 10:
            recent_avg = df_sorted.tail(5)["so_ket_qua"].mean()
            prior_avg = df_sorted.iloc[-10:-5]["so_ket_qua"].mean()
            if prior_avg > 0:
                change = (recent_avg - prior_avg) / prior_avg
                if change > 0.15:
                    metrics["trend"] = "up"
                elif change < -0.15:
                    metrics["trend"] = "down"
                else:
                    metrics["trend"] = "stable"
            else:
                metrics["trend"] = "stable"
        else:
            metrics["trend"] = "stable"
    else:
        metrics["has_year"] = False

    if not df_kw.empty and "keyword" in df_kw.columns:
        metrics["has_keywords"] = True
        metrics["top_keywords"] = [
            {
                "keyword": google_keyword_label(row["keyword"], locale),
                "rate": row["ty_le_xuat_hien"],
            }
            for _, row in df_kw.head(5).iterrows()
        ]
    else:
        metrics["has_keywords"] = False

    return metrics


def _section_with_table(title, paragraph, df, locale, nt, st):
    parts = [f"## {title}", ""]
    if paragraph:
        parts.extend([paragraph, ""])
    if df is None or df.empty:
        parts.extend([f"*{st['no_data']}*", ""])
    else:
        parts.extend([f"### {nt['table_detail']}", "", _df_to_markdown_table(rename_summary_columns(df, locale)), ""])
    return parts


def generate_summary_markdown(df_ch, df_ct, df_yr, df_kw, locale):
    st = SUMMARY_TEXT[locale]
    nt = NARRATIVE_TEXT[locale]
    metrics = _compute_summary_metrics(df_ch, df_ct, df_yr, df_kw, locale)
    tables = build_summary_tables(df_ch, df_ct, df_yr, df_kw, locale)

    parts = [f"# {st['page_heading']}", "", nt["intro"], ""]

    if metrics.get("has_channels"):
        account_parts = [
            nt["account_item"].format(
                label=account_type_label(item["slug"], locale),
                pct=item["pct"],
                videos=item["videos"],
            )
            for item in metrics["account_types"]
        ]
        account_breakdown = _join_items(account_parts, "account_join", nt)
        channels_para = nt["channels_para"].format(
            total_channels=fmt_dot(metrics["total_channels"]),
            top_channel=metrics["top_channel"],
            top_videos=metrics["top_videos"],
            top_pct=metrics["top_pct"],
            account_breakdown=account_breakdown,
        )
        top3_list = _join_items(
            [
                nt["top3_item"].format(**item)
                for item in metrics["top3_channels"]
            ],
            "top3_join",
            nt,
        )
        channels_para = f"{channels_para} {nt['channels_top3'].format(top3_list=top3_list)}"
    else:
        channels_para = None

    if metrics.get("has_content"):
        top_types = _join_items(
            [
                nt["content_type_item"].format(type=item["type"], pct=item["pct"])
                for item in metrics["top_content_types"]
            ],
            "content_type_join",
            nt,
        )
        content_para = nt["content_para"].format(
            total=metrics["total_content"],
            top_types=top_types,
        )
    else:
        content_para = None

    if metrics.get("has_year"):
        trend_label = nt[f"trend_{metrics['trend']}"]
        year_para = nt["year_para"].format(
            peak_year=metrics["peak_year"],
            peak_count=metrics["peak_count"],
            trend_label=trend_label,
        )
    else:
        year_para = None

    if metrics.get("has_keywords"):
        keyword_list = _join_items(
            [
                nt["keyword_item"].format(keyword=item["keyword"], rate=item["rate"])
                for item in metrics["top_keywords"]
            ],
            "keyword_join",
            nt,
        )
        keywords_para = nt["keywords_para"].format(keyword_list=keyword_list)
    else:
        keywords_para = None

    narratives = [channels_para, content_para, year_para, keywords_para]
    for (title, df), paragraph in zip(tables, narratives):
        parts.extend(_section_with_table(title, paragraph, df, locale, nt, st))

    return "\n".join(parts).rstrip() + "\n"


def write_summary_markdown(df_ch, df_ct, df_yr, df_kw, locale, out_path):
    content = generate_summary_markdown(df_ch, df_ct, df_yr, df_kw, locale)
    out_path = Path(out_path)
    out_path.write_text(content, encoding="utf-8")
    print(f"[OK] [{locale}] {out_path}")
