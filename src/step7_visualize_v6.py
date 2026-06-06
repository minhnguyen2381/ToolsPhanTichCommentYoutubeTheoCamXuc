"""BƯỚC 7: Trực quan hóa thống kê kênh YouTube và khảo sát Google.

Input:  output/data/v6_*.csv
Output: output/report/<locale>/*.png, output/report/<locale>/summary.html, summary.md (vi, en, zh)
"""

import io
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

from i18n_charts import (
    SUPPORTED_LOCALES,
    CHART_TEXT,
    SUMMARY_TEXT,
    apply_locale_font,
    account_type_label,
    fmt_dot,
)
from paths import DATA_DIR, REPORT_DIR, ensure_report_dir
from summary_narrative import (
    build_summary_tables,
    rename_summary_columns,
    write_summary_markdown,
)

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def _draw_bar_chart(df, x, y, locale, locale_dir, title_key, xlabel_key, ylabel_key, filename, rotate=45):
    txt = CHART_TEXT[locale]
    sns.set_theme(style="whitegrid")
    apply_locale_font(locale)

    plt.figure(figsize=(12, 7))
    ax = sns.barplot(data=df, x=x, y=y, palette="viridis", hue=x, legend=False)
    plt.title(txt[title_key], fontsize=14)
    plt.xlabel(txt[xlabel_key])
    plt.ylabel(txt[ylabel_key])
    plt.xticks(rotation=rotate, ha="right")
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
    _draw_bar_chart(
        summary, "content_type", "so_ket_qua",
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

    plt.figure(figsize=(14, 6))
    ax = sns.lineplot(data=df_yr, x="nam", y="so_ket_qua", marker="o")
    plt.title(txt["google_year_trend_title"], fontsize=14)
    plt.xlabel(txt["google_year_trend_xlabel"])
    plt.ylabel(txt["google_year_trend_ylabel"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_dot))
    plt.xticks(rotation=45)
    plt.tight_layout()
    out = locale_dir / "google_year_trend.png"
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"  → [{locale}] {out.name}")


def _plot_top_keywords(df_kw, locale, locale_dir):
    if df_kw.empty:
        return
    _draw_bar_chart(
        df_kw, "keyword", "ty_le_xuat_hien",
        locale, locale_dir,
        "google_top_keywords_title", "google_top_keywords_xlabel", "google_top_keywords_ylabel",
        "google_top_keywords.png",
        rotate=60,
    )


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

    df_ch = pd.read_csv(ch_file) if ch_file.exists() else pd.DataFrame()
    df_ct = pd.read_csv(ct_file) if ct_file.exists() else pd.DataFrame()
    df_yr = pd.read_csv(yr_file) if yr_file.exists() else pd.DataFrame()
    df_kw = pd.read_csv(kw_file) if kw_file.exists() else pd.DataFrame()

    if df_ch.empty and df_ct.empty:
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
        _write_summary_html(build_summary_tables(df_ch, df_ct, df_yr, df_kw, locale), locale, locale_dir)
        write_summary_markdown(df_ch, df_ct, df_yr, df_kw, locale, locale_dir / "summary.md")

    print(f"\n[OK] Biểu đồ kênh & Google → output/report/{{vi,en,zh}}/")


if __name__ == "__main__":
    main()
