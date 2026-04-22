"""BƯỚC 4: Vẽ biểu đồ báo cáo."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORT_DIR = Path(__file__).resolve().parent.parent / "report"
REPORT_DIR.mkdir(exist_ok=True)


def chart_keyword_summary():
    src = DATA_DIR / "keyword_summary.csv"
    if not src.exists():
        print(f"[!] Thiếu {src}, bỏ qua keyword chart.")
        return
    df = pd.read_csv(src)
    fig = px.bar(df, x="keyword", y="top50_total_views",
                 title="Tổng lượt xem top-50 video theo từ khoá",
                 text="top50_total_views")
    fig.write_html(REPORT_DIR / "keyword_views.html")

    fig2 = px.bar(df, x="keyword", y="total_results",
                  title="Tổng số video tìm được trên YouTube")
    fig2.write_html(REPORT_DIR / "keyword_total_results.html")
    print("[OK] Đã xuất report/keyword_*.html")


def chart_sentiment():
    src = DATA_DIR / "sentiment_report.csv"
    if not src.exists():
        print(f"[!] Thiếu {src}, bỏ qua sentiment chart.")
        return
    df = pd.read_csv(src)
    fig = px.bar(df, x="videoId", y=["POS_pct", "NEU_pct", "NEG_pct"],
                 title="Tỷ lệ Sentiment theo video (playlist Quan Vũ)",
                 barmode="stack")
    fig.write_html(REPORT_DIR / "sentiment_chart.html")

    totals = df[["POS", "NEU", "NEG"]].sum()
    plt.figure(figsize=(6, 6))
    plt.pie(totals, labels=totals.index, autopct="%1.1f%%",
            colors=["#4CAF50", "#9E9E9E", "#F44336"])
    plt.title("Tổng thể sentiment toàn playlist")
    plt.savefig(REPORT_DIR / "sentiment_pie.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[OK] Đã xuất report/sentiment_chart.html + sentiment_pie.png")


def main():
    chart_keyword_summary()
    chart_sentiment()


if __name__ == "__main__":
    main()
