# Tools Phân Tích Comment YouTube — Chủ đề Quan Vũ

Bộ công cụ Python phục vụ 2 mục tiêu:

1. **Khảo sát mức độ phổ biến** của các từ khoá *Quan Vũ, Quan Vân Trường, Quan Công, Quan Thánh* trên YouTube (số video, lượt xem, like, comment).
2. **Phân tích sentiment** comment của 15 video trong playlist [`PLlvlc45o3QQcwtas1taX7VlLyZ6Advf_3`](https://www.youtube.com/playlist?list=PLlvlc45o3QQcwtas1taX7VlLyZ6Advf_3) — phân loại Tích cực / Trung tính / Tiêu cực và tính tỷ lệ.

> Tài liệu gốc đặc tả giải pháp: [GIAI_PHAP_PYTHON.md](solutions/v1_sentiment/GIAI_PHAP_PYTHON.md)

---

## Mục Lục

| Tài liệu | Nội dung |
|----------|----------|
| [docs/INSTALL.md](docs/INSTALL.md) | Cài đặt môi trường, lấy API key |
| [docs/USAGE.md](docs/USAGE.md) | Hướng dẫn chạy từng bước + toàn bộ pipeline |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Giải thích kiến trúc & từng file code |
| [docs/QUOTA.md](docs/QUOTA.md) | Quản lý quota YouTube Data API |
| [docs/SENTIMENT_MODEL.md](docs/SENTIMENT_MODEL.md) | So sánh PhoBERT / XLM-R / rule-based |
| [docs/PREPROCESSING.md](docs/PREPROCESSING.md) | Tiền xử lý văn bản tiếng Việt |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Lỗi thường gặp & cách xử lý |
| [docs/ETHICS.md](docs/ETHICS.md) | Đạo đức dữ liệu, GDPR, bias |

---

## Bắt đầu nhanh (TL;DR)

```bash
# 1. Clone & vào thư mục
git clone <repo-url> ToolsPhanTichCommentYoutube
cd ToolsPhanTichCommentYoutube

# 2. Tạo venv
python -m venv .venv
source .venv/Scripts/activate    # Windows Git Bash
# hoặc: .\.venv\Scripts\Activate.ps1 (PowerShell)

# 3. Cài thư viện
pip install -r requirements.txt

# 4. Tạo file .env từ template
cp .env.example .env
# rồi mở .env, dán YOUTUBE_API_KEY thật vào

# 5. Chạy toàn bộ pipeline
python src/run_all.py
```

Chi tiết từng bước: [docs/INSTALL.md](docs/INSTALL.md) → [docs/USAGE.md](docs/USAGE.md).

---

## Cấu trúc thư mục

```
ToolsPhanTichCommentYoutube/
├── .env.example              # Template biến môi trường
├── .gitignore
├── requirements.txt          # Pin phiên bản thư viện
├── README.md                 # ← bạn đang đọc
├── GIAI_PHAP_PYTHON.md       # Đặc tả giải pháp gốc
├── src/
│   ├── youtube_client.py     # Wrapper YouTube Data API
│   ├── step1_keyword_stats.py
│   ├── step2_crawl_comments.py
│   ├── step3_sentiment.py
│   ├── visualize.py
│   └── run_all.py            # Chạy tuần tự cả 4 bước
├── data/                     # CSV thô + đã xử lý (sinh khi chạy)
├── report/                   # HTML / PNG biểu đồ (sinh khi chạy)
└── docs/                     # Tài liệu chi tiết
    ├── INSTALL.md
    ├── USAGE.md
    ├── ARCHITECTURE.md
    ├── QUOTA.md
    ├── SENTIMENT_MODEL.md
    ├── PREPROCESSING.md
    ├── TROUBLESHOOTING.md
    └── ETHICS.md
```

---

## Stack công nghệ

| Thành phần | Công nghệ |
|------------|-----------|
| Ngôn ngữ | Python 3.10+ |
| API | YouTube Data API v3 (qua `google-api-python-client`) |
| Tiền xử lý | `underthesea`, `emoji`, regex |
| Sentiment | PhoBERT (`wonrax/phobert-base-vietnamese-sentiment`) qua `transformers` + `torch` |
| Phân tích bảng | `pandas` |
| Biểu đồ | `plotly` (HTML) + `matplotlib` (PNG) |

---

## Lưu ý quan trọng

1. **Quota API** chỉ 10.000 units/ngày — xem [docs/QUOTA.md](docs/QUOTA.md) để ước lượng & tiết kiệm.
2. **Lần đầu chạy step3** sẽ download model PhoBERT (~500 MB) từ HuggingFace. Cần internet.
3. **PhoBERT có sai số ~15-20% với câu mỉa mai/châm biếm** — nên kết hợp cột `score` để lọc.
4. **Đạo đức**: ẩn `authorDisplayName` khi public báo cáo — xem [docs/ETHICS.md](docs/ETHICS.md).
5. **Một số video có thể tắt comment** (`commentsDisabled`) — script tự skip, không cần can thiệp.

---

## Roadmap (gợi ý 5 ngày)

| Ngày | Việc cần làm | Tham chiếu |
|------|--------------|-----------|
| 1 | Setup môi trường, lấy API key | [INSTALL.md](docs/INSTALL.md) |
| 2 | Chạy Bước 1 — keyword stats | [USAGE.md](docs/USAGE.md) |
| 3 | Crawl comment playlist | [QUOTA.md](docs/QUOTA.md) |
| 4 | Tích hợp PhoBERT, kiểm tra mẫu | [SENTIMENT_MODEL.md](docs/SENTIMENT_MODEL.md) |
| 5 | Vẽ biểu đồ, viết báo cáo | [USAGE.md](docs/USAGE.md) |

---

## Mở rộng

- **Topic Modeling** với BERTopic để xem khán giả thường bàn luận về khía cạnh nào của Quan Vũ (võ nghệ, lòng trung nghĩa, cái chết tại Mạch Thành...).
- **Crawl reply** chứ không chỉ top-level comment.
- **Async crawl** với `asyncio + aiohttp` để tăng tốc nhiều video.

Chi tiết: [docs/ARCHITECTURE.md § Điểm mở rộng](docs/ARCHITECTURE.md#4-điểm-mở-rộng).

---

## Trích dẫn

- **YouTube Data API v3** — Google.
- **PhoBERT**: Nguyen, D. Q., & Nguyen, A. T. (2020). *PhoBERT: Pre-trained language models for Vietnamese*. EMNLP Findings.
- **Underthesea**: <https://github.com/undertheseanlp/underthesea>.

---

## Giấy phép

Mã nguồn dùng cho mục đích học tập / nghiên cứu cá nhân. Tuân thủ [YouTube API Services Terms of Service](https://developers.google.com/youtube/terms/api-services-terms-of-service) khi sử dụng dữ liệu thu thập.
