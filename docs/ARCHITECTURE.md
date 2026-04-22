# Kiến Trúc & Giải Thích Code

## 1. Sơ đồ dữ liệu

```
YouTube API ──► step1_keyword_stats.py ──► data/keyword_*.csv + keyword_summary.csv
             ──► step2_crawl_comments.py ──► data/playlist_videos.csv + comments_raw.csv
                                             │
                                             ▼
                 step3_sentiment.py ──► data/comments_labeled.csv + sentiment_report.csv
                                             │
                                             ▼
                 visualize.py ──► report/*.html + *.png
```

## 2. Giải thích từng file

### `src/youtube_client.py`
- Đóng gói việc tạo client API + retry.
- `get_client()`: đọc `YOUTUBE_API_KEY` từ `.env`, dựng `googleapiclient` service.
- `safe_execute(request)`: retry với exponential backoff cho các lỗi 403/429/5xx tạm thời.

### `src/step1_keyword_stats.py`
- Với mỗi keyword trong `KEYWORDS`:
  1. Gọi `search.list(q=keyword, regionCode="VN", relevanceLanguage="vi")` → lấy top-50 video + `totalResults`.
  2. Gọi `videos.list(statistics,snippet)` trên 50 IDs → thu view/like/comment.
  3. Lưu `keyword_<tên>.csv`.
- Tổng hợp toàn bộ sang `keyword_summary.csv`.

### `src/step2_crawl_comments.py`
- `get_playlist_videos(playlist_id)`: phân trang `playlistItems.list` lấy toàn bộ videoId.
- `get_comments(video_id)`: phân trang `commentThreads.list` lấy tối đa `max_pages=20` × 100 = 2000 top-level comments.
- Bắt `HttpError` để bỏ qua video tắt comment (`commentsDisabled`).

### `src/step3_sentiment.py`
- `clean_text`: gỡ emoji, URL, HTML tag, ký tự đặc biệt → `underthesea.word_tokenize` trả chuỗi đã tách từ (vd: `"tôi yêu_nước"`).
- `build_predictor`: nạp model PhoBERT (`wonrax/phobert-base-vietnamese-sentiment`), auto phát hiện GPU.
- `predict(text)`: trả `(label, score)` trong `{POS, NEU, NEG}`.
- Gom theo video ra `sentiment_report.csv` với tỷ lệ phần trăm.

> Xem thêm: [SENTIMENT_MODEL.md](SENTIMENT_MODEL.md) so sánh 3 phương án PhoBERT / XLM-R / rule-based.

### `src/visualize.py`
- `chart_keyword_summary`: bar chart so sánh tổng lượt xem và tổng kết quả.
- `chart_sentiment`: stacked-bar từng video + pie chart tổng.
- Xuất HTML (tương tác được) và PNG (đưa vào báo cáo Word/PDF).

### `src/run_all.py`
- Script tiện dụng chạy tuần tự cả 4 bước.

## 3. Luồng dữ liệu chi tiết

### Cột của `comments_raw.csv`
| Cột | Ý nghĩa |
|-----|---------|
| `videoId` | ID video |
| `commentId` | ID comment gốc |
| `author` | Tên hiển thị người bình luận |
| `text` | Nội dung comment (plainText) |
| `likes` | Số like |
| `publishedAt` | ISO-8601 timestamp |

### Cột của `comments_labeled.csv`
Giống trên + 3 cột:
- `clean`: văn bản sau tiền xử lý.
- `label`: `POS | NEU | NEG`.
- `score`: xác suất lớp cao nhất (0–1).

### Cột của `sentiment_report.csv`
| Cột | Ý nghĩa |
|-----|---------|
| `videoId` | index |
| `POS`, `NEU`, `NEG` | số comment mỗi nhãn |
| `total` | tổng comment |
| `POS_pct`, `NEU_pct`, `NEG_pct` | tỷ lệ % |

## 4. Điểm mở rộng

- **Topic modeling**: thêm BERTopic trên `df["clean"]` để gom chủ đề.
- **Replies**: hiện chỉ lấy `topLevelComment`; mở rộng sang `replies`.
- **Streaming**: đổi sang `asyncio + aiohttp` để crawl nhiều video song song.
