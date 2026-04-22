# Troubleshooting

## 1. `RuntimeError: Thiếu YOUTUBE_API_KEY`
- Kiểm tra file `.env` đã có `YOUTUBE_API_KEY=AIza...` (không có dấu nháy).
- Đảm bảo chạy script từ thư mục gốc dự án để `python-dotenv` tìm được `.env`.

## 2. `HttpError 403: quotaExceeded`
- Hết quota 10.000 units/ngày. Xem [QUOTA.md](QUOTA.md).
- Chờ reset (15:00 VN) hoặc đổi API key.

## 3. `HttpError 403: commentsDisabled`
- Video tắt comment. `step2` đã bắt exception và bỏ qua, không cần làm gì.

## 4. `ssl.SSLCertVerificationError` trên Windows
- Cập nhật certificate: `pip install --upgrade certifi`.
- Hoặc cài lại Python với option *"Install certificates"*.

## 5. PhoBERT chạy chậm
- Bật GPU: cài `torch` bản CUDA đúng phiên bản driver.
- Giảm `max_length` từ 256 → 128 nếu comment ngắn.
- Batch hoá: gom 16–32 input vào một lần `tok(...)` thay vì 1.

## 6. `OSError: Can't load tokenizer`
- Mạng chặn HuggingFace. Set proxy hoặc tải model thủ công:
  ```bash
  huggingface-cli download wonrax/phobert-base-vietnamese-sentiment
  ```

## 7. `UnicodeEncodeError` khi mở CSV trên Excel
- File đã được lưu `utf-8-sig` để Excel hiển thị đúng tiếng Việt. Nếu vẫn lỗi, mở qua **Data → From Text/CSV** và chọn encoding **65001 (UTF-8)**.

## 8. `underthesea` cài lỗi trên Python 3.12
- Hạ về Python 3.10 hoặc 3.11. `underthesea` chưa support tốt 3.12.

## 9. `MemoryError` khi load model
- Máy <4 GB RAM không đủ. Đổi sang model nhẹ hơn:
  ```python
  MODEL_NAME = "5CD-AI/Vietnamese-Sentiment-visobert"
  ```

## 10. Crawl ra 0 comment
- Kiểm tra `PLAYLIST_ID` đúng chưa, playlist có public không.
- Một số video trong playlist có thể đã bị xoá / chuyển private.
