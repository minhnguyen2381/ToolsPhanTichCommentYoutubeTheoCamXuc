"""BƯỚC 6 (V5): Trực quan hóa kết quả phân tích comment.
- Vẽ biểu đồ Sentiment tổng thể.
- Vẽ biểu đồ tỷ lệ tính cách đặc trưng của Quan Vũ.
- Xuất đa ngôn ngữ: vi, en, zh → report/v5/<locale>/
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys, io
from i18n_charts import (
    SUPPORTED_LOCALES, SENTIMENT_LABELS, KEYWORD_LABELS,
    CHART_TEXT, apply_locale_font,
)

# Fix encoding trên Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORT_DIR = Path(__file__).resolve().parent.parent / "report" / "v5"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def plot_sentiment(df_labeled, locale: str, report_dir):
    """Vẽ biểu đồ Sentiment cho một locale cụ thể."""
    print(f"  [*] Đang vẽ biểu đồ Sentiment [{locale}]...")
    
    sns.set_theme(style="whitegrid")
    apply_locale_font(locale)
    
    sentiment_counts = df_labeled['sentiment'].value_counts()
    
    # Dịch nhãn sentiment theo locale
    labels_map = SENTIMENT_LABELS[locale]
    translated_labels = [labels_map.get(s, s) for s in sentiment_counts.index]
    
    plt.figure(figsize=(8, 6))
    colors = sns.color_palette("pastel")[0:len(sentiment_counts)]
    plt.pie(sentiment_counts, labels=translated_labels, autopct='%1.1f%%', 
            startangle=140, colors=colors, wedgeprops={'edgecolor': 'black'})
    
    txt = CHART_TEXT[locale]
    plt.title(txt["sentiment_title"], fontsize=16)
    
    out_file = report_dir / "sentiment_distribution.png"
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"    → Đã lưu {out_file}")

def plot_keywords(df_kw, locale: str, report_dir):
    """Vẽ biểu đồ tính cách cho một locale cụ thể."""
    print(f"  [*] Đang vẽ biểu đồ Tính cách [{locale}]...")
    
    # Lọc chỉ lấy các tính cách có count > 0
    df_kw = df_kw[df_kw['count'] > 0].copy()
    
    if len(df_kw) == 0:
        print("  [!] Không có dữ liệu tính cách để vẽ biểu đồ.")
        return
    
    sns.set_theme(style="whitegrid")
    apply_locale_font(locale)
    
    # Dịch keyword labels theo locale
    kw_map = KEYWORD_LABELS[locale]
    df_kw["keyword_display"] = df_kw["keyword"].map(kw_map).fillna(df_kw["keyword"])
        
    plt.figure(figsize=(12, 6))
    
    ax = sns.barplot(x="count", y="keyword_display", data=df_kw, palette="coolwarm",
                     hue="keyword_display", legend=False)
    
    txt = CHART_TEXT[locale]
    plt.title(txt["personality_title"], fontsize=16)
    plt.xlabel(txt["personality_xlabel"])
    plt.ylabel(txt["personality_ylabel"])
    
    # In số lên đỉnh cột (format dấu chấm phân cách hàng nghìn)
    for container in ax.containers:
        ax.bar_label(container, labels=[f"{int(v.get_width()):,}".replace(",", ".") for v in container], padding=3)
    
    out_file = report_dir / "personality_traits.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"    → Đã lưu {out_file}")

def main():
    labeled_file = DATA_DIR / "v5_comments_labeled.csv"
    kw_file = DATA_DIR / "v5_extracted_keywords.csv"
    
    # Đọc dữ liệu một lần
    df_labeled = None
    df_kw = None
    
    if labeled_file.exists():
        df_labeled = pd.read_csv(labeled_file)
        if df_labeled.empty or 'sentiment' not in df_labeled.columns:
            df_labeled = None
    else:
        print(f"[!] Không tìm thấy {labeled_file.name}")
        
    if kw_file.exists():
        df_kw = pd.read_csv(kw_file)
        if df_kw.empty:
            df_kw = None
    else:
        print(f"[!] Không tìm thấy {kw_file.name}")
    
    # Vẽ biểu đồ cho từng locale
    for locale in SUPPORTED_LOCALES:
        locale_dir = REPORT_DIR / locale
        locale_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[*] Đang vẽ biểu đồ [{locale}]...")
        
        if df_labeled is not None:
            plot_sentiment(df_labeled, locale, locale_dir)
        
        if df_kw is not None:
            plot_keywords(df_kw, locale, locale_dir)
        
        print(f"  → Hoàn tất [{locale}]")
    
    print(f"\n[OK] Đã xuất biểu đồ đa ngôn ngữ ra {REPORT_DIR}")

if __name__ == "__main__":
    main()
