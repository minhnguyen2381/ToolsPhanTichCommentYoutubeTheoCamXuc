# Đạo Đức Dữ Liệu & Tuân Thủ

## 1. YouTube Terms of Service

- API key cá nhân chỉ dùng cho mục đích **nghiên cứu / cá nhân**.
- Không redistribute dữ liệu thô comment dưới dạng public dataset (vi phạm ToS YouTube).
- Cache local tối đa 30 ngày, sau đó refresh hoặc xoá.

## 2. Bảo vệ danh tính người dùng

Khi public báo cáo (blog, slide, paper):

- **Ẩn `authorDisplayName`**: thay bằng `user_<hash>`.
  ```python
  import hashlib
  df["author"] = df["author"].apply(
      lambda x: "user_" + hashlib.md5(x.encode()).hexdigest()[:8]
  )
  ```
- Không trích dẫn nguyên văn comment có thông tin cá nhân (số điện thoại, email, địa chỉ).
- Nếu trích dẫn để minh hoạ, parafrase lại.

## 3. Bias của model

PhoBERT có thể bị bias theo:
- **Phương ngữ**: train chủ yếu trên văn bản miền Bắc.
- **Domain**: kém chính xác với comment về tôn giáo, chính trị.

Khi báo cáo, ghi rõ: *"Kết quả sentiment được sinh tự động bằng PhoBERT, có sai số ~15%, không thay thế đánh giá của con người."*

## 4. GDPR / Nghị định 13/2023

Nếu sử dụng cho tổ chức:
- Comment có thể chứa dữ liệu cá nhân → áp dụng nghĩa vụ thông báo / xoá khi yêu cầu.
- Lưu trong môi trường nội bộ, không upload lên drive public.

## 5. Trung thực học thuật

Khi viết khoá luận / báo cáo, trích dẫn:
- YouTube Data API v3 (Google).
- PhoBERT: Nguyen, D. Q., & Nguyen, A. T. (2020). *PhoBERT: Pre-trained language models for Vietnamese*.
- Underthesea: <https://github.com/undertheseanlp/underthesea>.
