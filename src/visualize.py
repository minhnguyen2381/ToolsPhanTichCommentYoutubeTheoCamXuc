"""BƯỚC 4 (V4): Vẽ biểu đồ báo cáo — toàn bộ kết quả từ step 1-3.

Bao gồm cả chart cũ (keyword, sentiment) và chart V4 mới
(topic distribution, top keywords, personality).
Label: chuyển videoId → tên video rút gọn.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORT_DIR = Path(__file__).resolve().parent.parent / "report"
REPORT_DIR.mkdir(exist_ok=True)

MAX_TITLE_LEN = 50


# ---------------------------------------------------------------------------
# Helper: load video titles từ v4_video_topics.csv
# ---------------------------------------------------------------------------
def _load_video_titles():
    """Đọc v4_video_topics.csv → dict {videoId: title_rút_gọn}."""
    src = DATA_DIR / "v4_video_topics.csv"
    if not src.exists():
        return {}
    df = pd.read_csv(src)
    titles = {}
    for _, row in df.iterrows():
        vid = str(row.get("videoId", ""))
        title = str(row.get("title", vid))
        if len(title) > MAX_TITLE_LEN:
            title = title[:MAX_TITLE_LEN] + "…"
        titles[vid] = title
    return titles


def _map_video_labels(df, col="videoId"):
    """Thêm cột 'video_label' = tên video rút gọn."""
    titles = _load_video_titles()
    df = df.copy()
    df["video_label"] = df[col].apply(
        lambda vid: titles.get(str(vid), str(vid))
    )
    return df


# ---------------------------------------------------------------------------
# Chart cũ (giữ tương thích) — CẬP NHẬT label
# ---------------------------------------------------------------------------
def chart_keyword_summary():
    """Chart cũ: tổng views/comments top-50 theo keyword."""
    src = DATA_DIR / "keyword_summary.csv"
    if not src.exists():
        print(f"[!] Thiếu {src}, bỏ qua.")
        return
    df = pd.read_csv(src)
    fig = px.bar(df, x="keyword", y="top50_total_views",
                 title="Tổng lượt xem top-50 video theo từ khoá",
                 text="top50_total_views",
                 labels={"keyword": "Từ khoá", "top50_total_views": "Lượt xem"})
    fig.write_html(REPORT_DIR / "keyword_views.html")

    fig2 = px.bar(df, x="keyword", y="top50_total_comments",
                  title="Tổng bình luận top-50 video theo từ khoá",
                  text="top50_total_comments",
                  labels={"keyword": "Từ khoá", "top50_total_comments": "Bình luận"})
    fig2.write_html(REPORT_DIR / "keyword_total_comments.html")
    print("[OK] report/keyword_views.html + keyword_total_comments.html")


def chart_sentiment():
    """Chart cũ: tỷ lệ sentiment, label = tên video."""
    src = DATA_DIR / "sentiment_report.csv"
    if not src.exists():
        print(f"[!] Thiếu {src}, bỏ qua.")
        return
    df = pd.read_csv(src)
    df = _map_video_labels(df, "videoId")

    fig = px.bar(df, x="video_label", y=["POS_pct", "NEU_pct", "NEG_pct"],
                 title="Tỷ lệ Sentiment theo video",
                 barmode="stack",
                 labels={"video_label": "Tên video", "value": "Tỷ lệ (%)",
                         "variable": "Sentiment"})
    fig.write_html(REPORT_DIR / "sentiment_chart.html")

    totals = df[["POS", "NEU", "NEG"]].sum()
    plt.figure(figsize=(6, 6))
    plt.pie(totals, labels=totals.index, autopct="%1.1f%%",
            colors=["#4CAF50", "#9E9E9E", "#F44336"])
    plt.title("Tổng thể sentiment toàn playlist")
    plt.savefig(REPORT_DIR / "sentiment_pie.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[OK] report/sentiment_chart.html + sentiment_pie.png")


# ---------------------------------------------------------------------------
# Chart V4 mới
# ---------------------------------------------------------------------------
def chart_v4_keyword_summary():
    """Grouped bar: views + comments theo keyword (V4, max 500)."""
    src = DATA_DIR / "v4_keyword_summary.csv"
    if not src.exists():
        print(f"[!] Thiếu {src}, bỏ qua.")
        return
    df = pd.read_csv(src)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Lượt xem", x=df["keyword"], y=df["total_views"],
        text=df["total_views"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Bình luận", x=df["keyword"], y=df["total_comments"],
        text=df["total_comments"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
    ))
    fig.update_layout(
        title="Tổng lượt xem & bình luận theo từ khoá (V4 — max 500 video)",
        barmode="group",
        xaxis_title="Từ khoá",
        yaxis_title="Số lượng",
        font=dict(size=13),
    )
    fig.write_html(REPORT_DIR / "v4_keyword_summary.html")
    print("[OK] report/v4_keyword_summary.html")


def chart_v4_topic_distribution():
    """Pie chart + bar chart phân bố chủ đề video."""
    src = DATA_DIR / "v4_video_topics.csv"
    if not src.exists():
        print(f"[!] Thiếu {src}, bỏ qua.")
        return
    df = pd.read_csv(src)
    topic_stats = df.groupby("topic").agg(
        số_video=("videoId", "count"),
        tổng_views=("views", "sum"),
    ).reset_index()

    # Pie chart — số video mỗi chủ đề
    fig_pie = px.pie(
        topic_stats, names="topic", values="số_video",
        title="Phân bố chủ đề video về Quan Vũ",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_traces(textinfo="label+percent+value",
                          textfont_size=14)
    fig_pie.update_layout(font=dict(size=13))
    fig_pie.write_html(REPORT_DIR / "v4_topic_pie.html")

    # Bar chart — views theo chủ đề
    fig_bar = px.bar(
        topic_stats.sort_values("tổng_views", ascending=True),
        x="tổng_views", y="topic", orientation="h",
        title="Tổng lượt xem theo chủ đề",
        text="tổng_views",
        labels={"topic": "Chủ đề", "tổng_views": "Lượt xem"},
        color="topic",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_bar.update_layout(showlegend=False, font=dict(size=13),
                          margin=dict(l=150))
    fig_bar.write_html(REPORT_DIR / "v4_topic_views.html")
    print("[OK] report/v4_topic_pie.html + v4_topic_views.html")


def chart_v4_top_keywords():
    """Horizontal bar: top 30 keyword phổ biến trong comments."""
    src = DATA_DIR / "v4_keyword_frequency.csv"
    if not src.exists():
        print(f"[!] Thiếu {src}, bỏ qua.")
        return
    df = pd.read_csv(src).head(30)

    fig = px.bar(
        df.sort_values("count", ascending=True),
        x="count", y="keyword", orientation="h",
        title="Top 30 keyword phổ biến trong comments",
        text="percentage",
        labels={"keyword": "Keyword", "count": "Số lần xuất hiện"},
        color="count",
        color_continuous_scale="Viridis",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        height=max(500, len(df) * 28),
        font=dict(size=13),
        margin=dict(l=180),
        coloraxis_showscale=False,
    )
    fig.write_html(REPORT_DIR / "v4_top_keywords.html")
    print("[OK] report/v4_top_keywords.html")


def chart_v4_personality():
    """Horizontal bar: % keyword tính cách Quan Vũ."""
    src = DATA_DIR / "v4_personality_keywords.csv"
    if not src.exists():
        print(f"[!] Thiếu {src}, bỏ qua.")
        return
    df = pd.read_csv(src)

    fig = px.bar(
        df.sort_values("count", ascending=True),
        x="count", y="display_name", orientation="h",
        color="category",
        title="Keyword tính cách Quan Vũ trong comments YouTube",
        text="percentage",
        labels={"count": "Số lần xuất hiện", "display_name": "Tính cách",
                "category": "Phân loại"},
        color_discrete_map={"Tích cực": "#4CAF50", "Tiêu cực": "#F44336"},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        height=max(400, len(df) * 30),
        yaxis={"categoryorder": "total ascending"},
        font=dict(size=13),
        margin=dict(l=200),
    )
    fig.write_html(REPORT_DIR / "v4_personality_barchart.html")
    print("[OK] report/v4_personality_barchart.html")


def chart_v4_personality_pie():
    """Donut chart: tích cực vs tiêu cực."""
    src = DATA_DIR / "v4_personality_keywords.csv"
    if not src.exists():
        print(f"[!] Thiếu {src}, bỏ qua.")
        return
    df = pd.read_csv(src)

    pos_count = df[df["category"] == "Tích cực"]["count"].sum()
    neg_count = df[df["category"] == "Tiêu cực"]["count"].sum()

    fig = go.Figure(data=[go.Pie(
        labels=["Tích cực", "Tiêu cực"],
        values=[pos_count, neg_count],
        marker=dict(colors=["#4CAF50", "#F44336"]),
        textinfo="label+percent+value",
        textfont=dict(size=16),
        hole=0.3,
    )])
    fig.update_layout(
        title="Tỷ lệ nhận xét tích cực vs tiêu cực về tính cách Quan Vũ",
        font=dict(size=14),
    )
    fig.write_html(REPORT_DIR / "v4_personality_pie.html")
    print("[OK] report/v4_personality_pie.html")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=== Chart cũ ===")
    chart_keyword_summary()
    chart_sentiment()

    print("\n=== Chart V4 ===")
    chart_v4_keyword_summary()
    chart_v4_topic_distribution()
    chart_v4_top_keywords()
    chart_v4_personality()
    chart_v4_personality_pie()

    print(f"\n[DONE] Toàn bộ biểu đồ đã xuất vào {REPORT_DIR}")


if __name__ == "__main__":
    main()
