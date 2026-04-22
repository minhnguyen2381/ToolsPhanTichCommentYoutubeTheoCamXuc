# Quota — Không áp dụng

Pipeline đã chuyển sang dùng `yt-dlp` + `youtube-comment-downloader`, **không gọi YouTube Data API v3**, nên không bị giới hạn 10.000 units/ngày của Google Cloud.

## Đánh đổi

| Hạng mục | API v3 (cũ) | yt-dlp + ycd (mới) |
|----------|-------------|--------------------|
| Cần API key | Có (Google Cloud) | Không |
| Giới hạn quota | 10.000 units/ngày | Không có quota cứng |
| Tốc độ lấy stats | Batch 50 video / 1 call | Phải gọi từng video |
| Trường `total_results` | Có | **Không** (đã bỏ) |
| Rủi ro bị chặn IP | Thấp | Có (nếu chạy quá nhiều/quá nhanh) |

## Khi bị chặn / bot detection

YouTube đôi khi yêu cầu xác thực nếu phát hiện scraping bất thường. Triệu chứng: yt-dlp trả lỗi `Sign in to confirm you're not a bot`.

Cách xử lý:
1. Giảm tần suất / thêm `time.sleep` giữa các call.
2. Dùng cookies trình duyệt:
   ```bash
   yt-dlp --cookies-from-browser chrome <url>
   ```
   (Áp dụng cho code: thêm `cookiesfrombrowser=("chrome",)` vào `_BASE_OPTS` trong `src/youtube_client.py`.)
3. Đổi IP / dùng VPN nếu IP bị flag.

## Mẹo tiết kiệm thời gian

1. **Cache CSV**: dữ liệu đã crawl thì không crawl lại khi dev.
2. Hạn chế chạy lại `step1` — kết quả search ổn định trong vài ngày.
3. Có thể giảm `MAX_COMMENTS_PER_VIDEO` trong `step2_crawl_comments.py` nếu chỉ cần lấy mẫu.
