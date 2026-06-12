"""BƯỚC 7: Trực quan hóa thống kê kênh YouTube và khảo sát Google (V6 + V7).

Input:  output/data/v6_*.csv, output/data/v7_google_*.csv
Output: output/report/<locale>/*.png, output/report/<locale>/summary.html, summary.md (vi, en, zh)
"""

import io
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
import pandas as pd
import seaborn as sns

from i18n_charts import (
    SUPPORTED_LOCALES,
    CHART_TEXT,
    SUMMARY_TEXT,
    apply_locale_font,
    apply_latin_xticklabels,
    account_type_label,
    content_type_color,
    content_type_label,
    fmt_dot,
    google_category_label,
    google_keyword_label,
)
from paths import DATA_DIR, REPORT_DIR, ensure_report_dir
from summary_narrative import (
    build_summary_tables,
    rename_summary_columns,
    write_summary_markdown,
)

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_PIE_SMALL_SLICE_THRESHOLD = 3.0
_PIE_WEDGE_PROPS = {"edgecolor": "white", "linewidth": 0.5}


def _group_small_pie_slices(rows, threshold=_PIE_SMALL_SLICE_THRESHOLD):
    """Gộp lát < threshold% vào nhóm Khác."""
    kept = []
    other = 0.0
    for content_type, value in rows:
        if value >= threshold and content_type != "Khác":
            kept.append((content_type, value))
        else:
            other += value
    if other > 0:
        merged = False
        for i, (content_type, value) in enumerate(kept):
            if content_type == "Khác":
                kept[i] = ("Khác", value + other)
                merged = True
                break
        if not merged:
            kept.append(("Khác", other))
    kept.sort(key=lambda item: -item[1])
    return kept


def _pie_autopct(pct):
    if pct >= _PIE_SMALL_SLICE_THRESHOLD:
        return f"{pct:.1f}%"
    return ""


def _plot_pie_facets(facets, locale, locale_dir, title_key, filename, figsize):
    """Vẽ lưới pie chart; facets = [(subplot_title, [(content_type, pct), ...]), ...]."""
    if not facets:
        return

    txt = CHART_TEXT[locale]
    sns.set_theme(style="whitegrid")
    apply_locale_font(locale)

    n = len(facets)
    ncols = min(3, n)
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    if n == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    all_types = sorted(
        {ct for _, rows in facets for ct, _ in rows},
        key=lambda ct: -max(pct for _, rs in facets for c, pct in rs if c == ct),
    )

    for ax, (subtitle, rows) in zip(axes, facets):
        sizes = [pct for _, pct in rows]
        colors = [content_type_color(ct) for ct, _ in rows]
        _, _, autotexts = ax.pie(
            sizes,
            labels=None,
            autopct=_pie_autopct,
            startangle=90,
            colors=colors,
            wedgeprops=_PIE_WEDGE_PROPS,
            radius=0.72,
            pctdistance=1.18,
        )
        for autotext in autotexts:
            if autotext.get_text():
                autotext.set_fontsize(8)
        ax.set_title(subtitle, fontsize=11)

    for ax in axes[len(facets):]:
        ax.axis("off")

    legend_handles = [
        Patch(
            facecolor=content_type_color(ct),
            edgecolor="white",
            label=content_type_label(ct, locale),
        )
        for ct in all_types
    ]
    fig.legend(
        handles=legend_handles,
        title=txt["google_content_types_xlabel"],
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        fontsize=9,
    )
    fig.suptitle(txt[title_key], fontsize=14, y=1.02)
    plt.tight_layout()
    out = locale_dir / filename
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → [{locale}] {out.name}")


def _draw_bar_chart(
    df, x, y, locale, locale_dir, title_key, xlabel_key, ylabel_key, filename,
    rotate=45, latin_xticks=False,
):
    txt = CHART_TEXT[locale]
    sns.set_theme(style="whitegrid")
    apply_locale_font(locale)

    plt.figure(figsize=(12, 7))
    ax = sns.barplot(data=df, x=x, y=y, palette="viridis", hue=x, legend=False)
    plt.title(txt[title_key], fontsize=14)
    plt.xlabel(txt[xlabel_key])
    plt.ylabel(txt[ylabel_key])
    plt.xticks(rotation=rotate, ha="right")
    if latin_xticks:
        apply_latin_xticklabels(ax, locale)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_dot))
    for container in ax.containers:
        ax.bar_label(container, labels=[fmt_dot(v.get_height()) for v in container], padding=3)
    plt.tight_layout()
    out = locale_dir / filename
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"  → [{locale}] {out.name}")


def _plot_channels(df_ch, locale, locale_dir):
    if df_ch.empty:
        return
    top = df_ch.nlargest(15, "so_luong_video")
    _draw_bar_chart(
        top, "ten_tai_khoan", "so_luong_video",
        locale, locale_dir,
        "channel_top15_title", "channel_top15_xlabel", "channel_top15_ylabel",
        "channel_top15.png",
        latin_xticks=True,
    )

    type_counts = df_ch.groupby("loai_tai_khoan")["so_luong_video"].sum().reset_index()
    type_counts = type_counts.copy()
    type_counts["label"] = type_counts["loai_tai_khoan"].apply(
        lambda s: account_type_label(s, locale)
    )
    _draw_bar_chart(
        type_counts, "label", "so_luong_video",
        locale, locale_dir,
        "channel_account_types_title", "channel_account_types_xlabel", "channel_account_types_ylabel",
        "channel_account_types.png",
        rotate=20,
    )


def _plot_google_content(df_ct, locale, locale_dir):
    if df_ct.empty or "content_type" not in df_ct.columns:
        return
    summary = df_ct.groupby("content_type").size().reset_index(name="so_ket_qua")
    summary = summary.copy()
    summary["label"] = summary["content_type"].apply(
        lambda v: content_type_label(v, locale)
    )
    _draw_bar_chart(
        summary, "label", "so_ket_qua",
        locale, locale_dir,
        "google_content_types_title", "google_content_types_xlabel", "google_content_types_ylabel",
        "google_content_types.png",
        rotate=30,
    )


def _plot_year_trend(df_yr, locale, locale_dir):
    if df_yr.empty:
        return
    txt = CHART_TEXT[locale]
    sns.set_theme(style="whitegrid")
    apply_locale_font(locale)

    plot_df = df_yr[df_yr["nam"] >= 2000].copy()
    if plot_df.empty:
        return

    plt.figure(figsize=(14, 6))
    ax = sns.lineplot(data=plot_df, x="nam", y="so_ket_qua", marker="o")
    plt.title(txt["google_year_trend_title"], fontsize=14)
    plt.xlabel(txt["google_year_trend_xlabel"])
    plt.ylabel(txt["google_year_trend_ylabel"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_dot))
    plt.xlim(2000, plot_df["nam"].max())
    plt.xticks(rotation=45)
    plt.tight_layout()
    out = locale_dir / "google_year_trend.png"
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"  → [{locale}] {out.name}")


def _plot_v7_keyword_content(df_v7_kw, locale, locale_dir):
    if df_v7_kw.empty or "core_keyword" not in df_v7_kw.columns:
        return

    facets = []
    for core in df_v7_kw["core_keyword"].unique():
        sub = df_v7_kw[df_v7_kw["core_keyword"] == core]
        rows = list(zip(sub["content_type"], sub["ty_le_pct"]))
        facets.append((
            google_keyword_label(core, locale),
            _group_small_pie_slices(rows),
        ))

    _plot_pie_facets(
        facets,
        locale,
        locale_dir,
        "google_keyword_content_types_title",
        "google_keyword_content_types.png",
        figsize=(16, 10),
    )


def _plot_v7_year_content(df_v7_yr, locale, locale_dir):
    if df_v7_yr.empty or "nam" not in df_v7_yr.columns:
        return
    txt = CHART_TEXT[locale]
    plot_df = df_v7_yr[df_v7_yr["nam"] >= 2000].copy()
    if plot_df.empty:
        return
    plot_df["type_display"] = plot_df["content_type"].apply(
        lambda v: content_type_label(v, locale)
    )

    sns.set_theme(style="whitegrid")
    apply_locale_font(locale)

    pivot = (
        plot_df.pivot_table(index="nam", columns="type_display", values="so_ket_qua", aggfunc="sum")
        .fillna(0)
        .sort_index()
    )
    if pivot.empty:
        return

    plt.figure(figsize=(14, 8))
    ax = pivot.plot(kind="bar", stacked=True, colormap="tab20", width=0.85)
    plt.title(txt["google_year_content_trend_title"], fontsize=14)
    plt.xlabel(txt["google_year_content_trend_xlabel"])
    plt.ylabel(txt["google_year_content_trend_ylabel"])
    plt.xticks(rotation=45, ha="right")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_dot))
    plt.legend(title=txt["google_content_types_xlabel"], bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    out = locale_dir / "google_year_content_trend.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → [{locale}] {out.name}")


def _plot_top_keywords(df_kw, locale, locale_dir):
    if df_kw.empty:
        return
    txt = CHART_TEXT[locale]
    plot_df = df_kw.copy()
    plot_df["keyword_display"] = plot_df["keyword"].apply(
        lambda k: google_keyword_label(k, locale)
    )
    if "category" in plot_df.columns:
        plot_df["category_display"] = plot_df["category"].apply(
            lambda c: google_category_label(c, locale)
        )

    sns.set_theme(style="whitegrid")
    apply_locale_font(locale)

    plt.figure(figsize=(14, 8))
    hue_col = "category_display" if "category_display" in plot_df.columns else None
    ax = sns.barplot(
        data=plot_df,
        x="keyword_display",
        y="ty_le_xuat_hien",
        hue=hue_col,
        palette="Set2" if hue_col else "viridis",
        dodge=False,
    )
    if hue_col:
        plt.legend(title=txt.get("google_top_keywords_hue", "Category"), bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.title(txt["google_top_keywords_title"], fontsize=14)
    plt.xlabel(txt["google_top_keywords_xlabel"])
    plt.ylabel(txt["google_top_keywords_ylabel"])
    plt.xticks(rotation=60, ha="right")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_dot))
    for container in ax.containers:
        ax.bar_label(container, labels=[fmt_dot(v.get_height()) for v in container], padding=3)
    plt.tight_layout()
    out = locale_dir / "google_top_keywords.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → [{locale}] {out.name}")


def _df_to_html_table(df, title, locale):
    st = SUMMARY_TEXT[locale]
    if df is None or df.empty:
        return f"<h2>{title}</h2><p><em>{st['no_data']}</em></p>"
    display_df = rename_summary_columns(df, locale)
    return f"<h2>{title}</h2>\n{display_df.to_html(index=False, border=0, classes='tbl')}"


def _write_summary_html(tables, locale, locale_dir):
    st = SUMMARY_TEXT[locale]
    css = """
    body { font-family: Arial, sans-serif; margin: 2rem; }
    h1 { color: #333; }
    .tbl { border-collapse: collapse; width: 100%; margin-bottom: 2rem; }
    .tbl th, .tbl td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    .tbl th { background: #f0f0f0; }
    """
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        f"<title>{st['page_title']}</title><style>{css}</style></head><body>",
        f"<h1>{st['page_heading']}</h1>",
    ]
    for title, df in tables:
        parts.append(_df_to_html_table(df, title, locale))
    parts.append("</body></html>")
    out = locale_dir / "summary.html"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"[OK] [{locale}] {out}")


def main():
    ensure_report_dir()

    ch_file = DATA_DIR / "v6_channel_stats.csv"
    ct_file = DATA_DIR / "v6_google_content_types.csv"
    yr_file = DATA_DIR / "v6_google_year_trend.csv"
    kw_file = DATA_DIR / "v6_google_top_keywords.csv"
    v7_kw_file = DATA_DIR / "v7_google_keyword_content_types.csv"
    v7_yr_file = DATA_DIR / "v7_google_year_content_trend.csv"

    df_ch = pd.read_csv(ch_file) if ch_file.exists() else pd.DataFrame()
    df_ct = pd.read_csv(ct_file) if ct_file.exists() else pd.DataFrame()
    df_yr = pd.read_csv(yr_file) if yr_file.exists() else pd.DataFrame()
    df_kw = pd.read_csv(kw_file) if kw_file.exists() else pd.DataFrame()
    df_v7_kw = pd.read_csv(v7_kw_file) if v7_kw_file.exists() else pd.DataFrame()
    df_v7_yr = pd.read_csv(v7_yr_file) if v7_yr_file.exists() else pd.DataFrame()

    if df_ch.empty and df_ct.empty and df_v7_kw.empty:
        print("[!] Chưa có dữ liệu kênh/Google. Chạy step5 và step6 trước.")
        return

    for locale in SUPPORTED_LOCALES:
        locale_dir = REPORT_DIR / locale
        locale_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[*] Đang vẽ biểu đồ kênh & Google [{locale}]...")
        _plot_channels(df_ch, locale, locale_dir)
        _plot_google_content(df_ct, locale, locale_dir)
        _plot_year_trend(df_yr, locale, locale_dir)
        _plot_top_keywords(df_kw, locale, locale_dir)
        _plot_v7_keyword_content(df_v7_kw, locale, locale_dir)
        _plot_v7_year_content(df_v7_yr, locale, locale_dir)
        tables = build_summary_tables(
            df_ch, df_ct, df_yr, df_kw, locale, df_v7_kw, df_v7_yr,
        )
        _write_summary_html(tables, locale, locale_dir)
        write_summary_markdown(
            df_ch, df_ct, df_yr, df_kw, locale, locale_dir / "summary.md",
            df_v7_kw, df_v7_yr,
        )

    print(f"\n[OK] Biểu đồ kênh & Google → output/report/{{vi,en,zh}}/")


if __name__ == "__main__":
    main()
