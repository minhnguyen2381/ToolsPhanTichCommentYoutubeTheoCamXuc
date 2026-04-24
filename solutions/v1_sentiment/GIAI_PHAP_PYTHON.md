# Tư Vấn Giải Pháp Python: Phân Tích Video & Comment YouTube về Quan Vũ

> **Mục tiêu dự án**
> - **B1:** Khảo sát mức độ phổ biến của các từ khoá *Quan Vũ, Quan Vân Trường, Quan Công, Quan Thánh* trên YouTube (số lượng video, lượt xem, like, comment).
> - **B2:** Lấy comment của 15 video trong playlist `PLlvlc45o3QQcwtas1taX7VlLyZ6Advf_3`, phân loại **Tích cực / Trung tính / Tiêu cực** và tính tỷ lệ.

---

## 1. Kiến Trúc Tổng Thể

```
┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│  YouTube Data API v3 │ ───► │  Crawler (Python)    │ ───► │  Lưu CSV / SQLite    │
└──────────────────────┘      └──────────────────────┘      └──────────────────────┘
                                         │
                                         ▼
                              ┌──────────────────────┐      ┌──────────────────────┐
                              │  Sentiment Analyzer  │ ───► │  Báo cáo + Biểu đồ   │
                              │  (PhoBERT / VADER)   │      │  (Matplotlib/Plotly) │
                              └──────────────────────┘      └──────────────────────┘
```

---

## 2. Chuẩn Bị Môi Trường

### 2.1. Lấy YouTube Data API Key
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Tạo project → bật **YouTube Data API v3**.
3. Tạo **API Key**, lưu vào file `.env`:
   ```
   YOUTUBE_API_KEY=AIzaSy....
   ```

### 2.2. Cài thư viện
```bash
pip install google-api-python-client python-dotenv pandas \
            transformers torch underthesea emoji \
            matplotlib seaborn plotly tqdm
```

| Thư viện | Vai trò |
|----------|---------|
| `google-api-python-client` | Gọi YouTube Data API v3 |
| `pandas` | Xử lý dữ liệu dạng bảng |
| `underthesea` | Tách từ tiếng Việt |
| `transformers` + `torch` | Chạy mô hình PhoBERT / XLM-RoBERTa cho sentiment tiếng Việt |
| `emoji` | Chuẩn hoá / loại bỏ emoji |
| `matplotlib`, `plotly` | Vẽ biểu đồ |

---

## 3. BƯỚC 1 — Khảo Sát Độ Phổ Biến Từ Khoá

### 3.1. Logic
- Với mỗi keyword, gọi `search.list` để đếm tổng số kết quả (`pageInfo.totalResults`).
- Lấy top-N video → gọi `videos.list` để lấy `viewCount`, `likeCount`, `commentCount`.
- Tổng hợp thành bảng so sánh.

### 3.2. Code mẫu (`step1_keyword_stats.py`)

```python
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

KEYWORDS = ["Quan Vũ", "Quan Vân Trường", "Quan Công", "Quan Thánh"]


def search_keyword(kw, max_results=50):
   res = youtube.search().list(
      q=kw, part="id,snippet", type="video",
      maxResults=max_results, regionCode="VN",
      relevanceLanguage="vi"
   ).execute()
   total = res["pageInfo"]["totalResults"]
   video_ids = [item["id"]["videoId"] for item in res["items"]]
   return total, video_ids


def get_video_stats(video_ids):
   stats = youtube.videos().list(
      part="statistics,snippet", id=",".join(video_ids)
   ).execute()
   rows = []
   for v in stats["items"]:
      s = v["statistics"]
      rows.append({
         "videoId": v["id"],
         "title": v["snippet"]["title"],
         "channel": v["snippet"]["channelTitle"],
         "views": int(s.get("viewCount", 0)),
         "likes": int(s.get("likeCount", 0)),
         "comments": int(s.get("commentCount", 0)),
      })
   return pd.DataFrame(rows)


summary = []
for kw in KEYWORDS:
   total, ids = search_keyword(kw)
   df = get_video_stats(ids)
   summary.append({
      "keyword": kw,
      "total_results": total,
      "top50_total_views": df["views"].sum(),
      "top50_avg_views": df["views"].mean(),
      "top50_total_likes": df["likes"].sum(),
   })
   df.to_csv(f"data/keyword_{kw}.csv", index=False, encoding="utf-8-sig")

pd.DataFrame(summary).to_csv("../../data/keyword_summary.csv", index=False, encoding="utf-8-sig")
```

### 3.3. Output mong muốn
| keyword | total_results | top50_total_views | top50_avg_views | top50_total_likes |
|---------|---------------|-------------------|-----------------|-------------------|
| Quan Vũ | 1,200,000 | 25,300,000 | 506,000 | 410,000 |
| Quan Vân Trường | 350,000 | 8,100,000 | 162,000 | 95,000 |
| ... | ... | ... | ... | ... |

---

## 4. BƯỚC 2 — Phân Tích Sentiment Comment Playlist

### 4.1. Lấy danh sách 15 video trong playlist
```python
def get_playlist_videos(playlist_id):
    ids, token = [], None
    while True:
        res = youtube.playlistItems().list(
            part="contentDetails", playlistId=playlist_id,
            maxResults=50, pageToken=token
        ).execute()
        ids.extend([i["contentDetails"]["videoId"] for i in res["items"]])
        token = res.get("nextPageToken")
        if not token: break
    return ids

PLAYLIST_ID = "PLlvlc45o3QQcwtas1taX7VlLyZ6Advf_3"
video_ids = get_playlist_videos(PLAYLIST_ID)
```

### 4.2. Crawl toàn bộ comment
```python
def get_comments(video_id, max_pages=20):
    comments, token, pages = [], None, 0
    while pages < max_pages:
        try:
            res = youtube.commentThreads().list(
                part="snippet,replies", videoId=video_id,
                maxResults=100, pageToken=token, textFormat="plainText"
            ).execute()
        except Exception as e:
            print(f"Lỗi {video_id}: {e}"); break
        for item in res["items"]:
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "videoId": video_id,
                "author": top["authorDisplayName"],
                "text": top["textDisplay"],
                "likes": top["likeCount"],
                "publishedAt": top["publishedAt"],
            })
        token = res.get("nextPageToken")
        pages += 1
        if not token: break
    return comments
```

### 4.3. Tiền xử lý văn bản tiếng Việt
```python
import re, emoji
from underthesea import word_tokenize

def clean_text(t):
    t = emoji.replace_emoji(t, replace=" ")
    t = re.sub(r"http\S+", " ", t)
    t = re.sub(r"[^\wÀ-ỹ\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return word_tokenize(t, format="text")
```

### 4.4. Phân loại sentiment — 3 lựa chọn

| Phương án | Ưu điểm | Nhược điểm | Khuyến nghị |
|-----------|---------|------------|-------------|
| **A. PhoBERT fine-tuned** (`wonrax/phobert-base-vietnamese-sentiment`) | Chính xác cao cho tiếng Việt, hỗ trợ 3 nhãn POS/NEU/NEG | Cần GPU để nhanh | ⭐ **Khuyên dùng** |
| **B. XLM-RoBERTa multilingual** | Đa ngôn ngữ, không cần tách từ | Nặng (~1GB) | Khi có dữ liệu pha tiếng |
| **C. Rule-based + từ điển VnSentiWordNet** | Nhẹ, không cần GPU | Độ chính xác thấp với mỉa mai/teen-code | Làm baseline |

**Code mẫu với PhoBERT:**
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch, torch.nn.functional as F

MODEL = "wonrax/phobert-base-vietnamese-sentiment"
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL).eval()
LABELS = ["NEG", "POS", "NEU"]   # theo config của model

@torch.no_grad()
def predict(text):
    inputs = tok(text, return_tensors="pt", truncation=True, max_length=256)
    logits = model(**inputs).logits
    probs = F.softmax(logits, dim=-1)[0]
    idx = probs.argmax().item()
    return LABELS[idx], float(probs[idx])
```

### 4.5. Tổng hợp & xuất báo cáo
```python
df["clean"] = df["text"].apply(clean_text)
df[["label", "score"]] = df["clean"].apply(lambda x: pd.Series(predict(x)))

report = (df.groupby(["videoId", "label"])
            .size().unstack(fill_value=0))
report["total"] = report.sum(axis=1)
for col in ["POS", "NEU", "NEG"]:
    report[f"{col}_pct"] = (report[col] / report["total"] * 100).round(2)

report.to_csv("data/sentiment_report.csv", encoding="utf-8-sig")
```

### 4.6. Trực quan hoá
```python
import plotly.express as px
fig = px.bar(report.reset_index(),
             x="videoId", y=["POS_pct", "NEU_pct", "NEG_pct"],
             title="Tỷ lệ Sentiment 15 video Playlist Quan Vũ",
             barmode="stack")
fig.write_html("report/sentiment_chart.html")
```

---

## 5. Cấu Trúc Thư Mục Đề Xuất

```
ToolsPhanTichCommentYoutube/
├── .env                    # API key
├── requirements.txt
├── README.md
├── src/
│   ├── youtube_client.py   # Wrapper API
│   ├── step1_keyword_stats.py
│   ├── step2_crawl_comments.py
│   ├── step3_sentiment.py
│   └── visualize.py
├── data/                   # CSV thô + đã xử lý
└── report/                 # HTML / PNG biểu đồ
```

---

## 6. Lưu Ý Khi Triển Khai

1. **Quota API:** YouTube Data API miễn phí **10.000 units/ngày**.
   - `search.list` = 100 units, `commentThreads.list` = 1 unit, `videos.list` = 1 unit.
   - → Bước 1 (4 keyword × search) ≈ 400 units; Bước 2 crawl comment rất rẻ.
2. **Rate limit:** dùng `time.sleep(0.1)` giữa các call để tránh 403.
3. **Comment bị tắt:** bắt exception `commentsDisabled`, ghi log rồi bỏ qua.
4. **Tiếng Việt không dấu / teen-code:** cân nhắc bước chuẩn hoá bằng `vncorenlp` hoặc dictionary.
5. **Mỉa mai / châm biếm:** PhoBERT vẫn có sai số ~15-20% với câu mỉa mai → cho thêm cột `score` (độ tin cậy) để lọc thủ công các comment biên.
6. **Đạo đức dữ liệu:** ẩn `authorDisplayName` khi public báo cáo.

---

## 7. Roadmap Đề Xuất (5 ngày)

| Ngày | Việc cần làm |
|------|--------------|
| 1 | Setup môi trường, lấy API key, viết `youtube_client.py` |
| 2 | Hoàn thành Bước 1 — keyword stats + biểu đồ |
| 3 | Crawl comment playlist (15 video), lưu CSV |
| 4 | Tích hợp PhoBERT, chạy phân loại, kiểm tra mẫu |
| 5 | Vẽ biểu đồ, viết báo cáo Markdown/PDF |

---

## 8. Kết Luận

- **Stack đề xuất:** *Python 3.10 + YouTube Data API v3 + PhoBERT + Pandas + Plotly*.
- **Điểm mạnh:** miễn phí, có thể tái sử dụng cho các chủ đề khác bằng cách đổi keyword/playlist.
- **Mở rộng tương lai:** thêm topic modeling (BERTopic) để xem khán giả thường bàn luận về **khía cạnh nào** của Quan Vũ (võ nghệ, lòng trung nghĩa, cái chết tại Mạch Thành...).
