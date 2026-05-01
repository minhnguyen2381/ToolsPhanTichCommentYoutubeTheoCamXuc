"""BƯỚC 6 (V5): Trực quan hóa kết quả phân tích comment.
- Vẽ biểu đồ Sentiment tổng thể.
- Vẽ biểu đồ tỷ lệ tính cách đặc trưng của Quan Vũ.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORT_DIR = Path(__file__).resolve().parent.parent / "report" / "v5"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def plot_sentiment(df_labeled):
    print("[*] Đang vẽ biểu đồ Sentiment...")
    sentiment_counts = df_labeled['sentiment'].value_counts()
    
    plt.figure(figsize=(8, 6))
    sns.set_theme(style="whitegrid")
    
    colors = sns.color_palette("pastel")[0:len(sentiment_counts)]
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', 
            startangle=140, colors=colors, wedgeprops={'edgecolor': 'black'})
    plt.title("Phân bố Cảm xúc Bình luận (Sentiment)", fontsize=16)
    
    out_file = REPORT_DIR / "sentiment_distribution.png"
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"  → Đã lưu {out_file.name}")

def plot_keywords(df_kw):
    print("[*] Đang vẽ biểu đồ Tính cách...")
    
    # Lọc chỉ lấy các tính cách có count > 0
    df_kw = df_kw[df_kw['count'] > 0]
    
    if len(df_kw) == 0:
        print("[!] Không có dữ liệu tính cách để vẽ biểu đồ.")
        return
        
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    
    ax = sns.barplot(x="count", y="keyword", data=df_kw, palette="coolwarm", hue="keyword", legend=False)
    plt.title("Mức độ phổ biến của các tính cách mô tả Quan Vũ", fontsize=16)
    plt.xlabel("Số lần xuất hiện")
    plt.ylabel("Tính cách / Đặc điểm")
    
    # In số lên đỉnh cột
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f', padding=3)
    
    out_file = REPORT_DIR / "personality_traits.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"  → Đã lưu {out_file.name}")

def main():
    labeled_file = DATA_DIR / "v5_comments_labeled.csv"
    kw_file = DATA_DIR / "v5_extracted_keywords.csv"
    
    if labeled_file.exists():
        df_labeled = pd.read_csv(labeled_file)
        if not df_labeled.empty and 'sentiment' in df_labeled.columns:
            plot_sentiment(df_labeled)
    else:
        print(f"[!] Không tìm thấy {labeled_file.name}")
        
    if kw_file.exists():
        df_kw = pd.read_csv(kw_file)
        if not df_kw.empty:
            plot_keywords(df_kw)
    else:
        print(f"[!] Không tìm thấy {kw_file.name}")

if __name__ == "__main__":
    main()
