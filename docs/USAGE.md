# Hướng Dẫn Sử Dụng

## Cách 1 — Chạy từng bước (khuyến nghị khi dev)

```bash
# Đảm bảo đã activate venv và có .env
cd src

# Bước 1: khảo sát keyword (~400 quota units)
python step1_keyword_stats.py

# Bước 2: lấy danh sách + crawl comment (~80 units)
python step2_crawl_comments.py

# Bước 3: phân tích sentiment (offline sau khi tải model lần đầu)
python step3_sentiment.py

# Bước 4: vẽ biểu đồ
python visualize.py
```

## Cách 2 — Chạy toàn bộ

```bash
python src/run_all.py
```

## Output sau khi chạy xong

```
data/
├── keyword_Quan_Vũ.csv
├── keyword_Quan_Vân_Trường.csv
├── keyword_Quan_Công.csv
├── keyword_Quan_Thánh.csv
├── keyword_summary.csv          ← bảng tổng hợp Bước 1
├── playlist_videos.csv          ← 15 video ID
├── comments_raw.csv             ← comment thô
├── comments_labeled.csv         ← comment đã gán nhãn
└── sentiment_report.csv         ← bảng % theo video

report/
├── keyword_views.html           ← biểu đồ tổng view theo keyword
├── keyword_total_results.html
├── sentiment_chart.html         ← stacked bar 15 video
└── sentiment_pie.png            ← pie tổng thể
```

## Tuỳ biến

### Đổi danh sách keyword
Sửa biến `KEYWORDS` trong `src/step1_keyword_stats.py`.

### Đổi playlist
Sửa biến `PLAYLIST_ID` trong `.env` hoặc trực tiếp trong `src/step2_crawl_comments.py`.

### Đổi model sentiment
Sửa `MODEL_NAME` trong `src/step3_sentiment.py` — xem [SENTIMENT_MODEL.md](SENTIMENT_MODEL.md).

### Giới hạn comment crawl
Trong `step2`, hàm `get_comments(video_id, max_pages=20)` — mỗi page = 100 comment.

## Mở báo cáo HTML

Plotly export ra HTML standalone (không cần server). Mở thẳng bằng browser:
```bash
start report/sentiment_chart.html      # Windows
xdg-open report/sentiment_chart.html   # Linux
open report/sentiment_chart.html       # macOS
```
