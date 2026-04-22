# Quản Lý Quota YouTube Data API v3

## 1. Giới hạn mặc định

- **10.000 units / ngày / project** (reset 00:00 Pacific Time).
- Yêu cầu thêm quota qua form trên Google Cloud Console (có thể chờ vài ngày).

## 2. Chi phí từng endpoint

| Endpoint | Units / call |
|----------|--------------|
| `search.list` | **100** |
| `videos.list` | 1 |
| `playlistItems.list` | 1 |
| `commentThreads.list` | 1 |
| `channels.list` | 1 |

## 3. Ước tính cho dự án

### Bước 1 — Keyword stats
- 4 keyword × 1 `search.list` = **400 units**
- 4 × 1 `videos.list` = **4 units**
- **Tổng: ~404 units**

### Bước 2 — Crawl playlist (15 video)
- 1 `playlistItems.list` = **1 unit**
- 15 × ~5 pages `commentThreads.list` = **~75 units**
- **Tổng: ~76 units**

→ Một lần chạy đầy đủ tiêu tốn **~500 units** (5% quota ngày).

## 4. Mẹo tiết kiệm quota

1. **Cache kết quả**: lưu CSV, không crawl lại khi dev.
2. **Hạn chế `search.list`**: mỗi call tốn 100 units — nhiều nhất trong pipeline.
3. **Pagination hợp lý**: `max_pages=20` trong `step2` là giới hạn an toàn.
4. **Chạy đêm VN**: trùng rush-hour bên Mỹ ít → ít lỗi 403.

## 5. Khi hết quota

- Lỗi: `quotaExceeded` (HTTP 403).
- Chờ reset (00:00 PT ~ 15:00 VN) hoặc dùng API key của project khác.
- Cân nhắc xin tăng quota (form [Google Cloud](https://support.google.com/youtube/contact/yt_api_form)).

## 6. Monitoring

Vào Google Cloud Console → **APIs & Services → YouTube Data API v3 → Quotas** để xem mức tiêu thụ realtime.
