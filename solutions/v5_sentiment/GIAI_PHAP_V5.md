# Giải pháp V5 - Cải tiến quy trình phân tích dữ liệu Quan Vũ

## Mục tiêu
Nâng cấp toàn bộ luồng cào dữ liệu và phân tích dữ liệu Youtube liên quan đến Quan Vũ (Quan Công, Quan Vân Trường, Quan Thánh).
Tập trung vào 6 bước rõ ràng từ việc cào diện rộng 3000 video, lọc rác, phân loại chủ đề, cho đến phân tích sentiment trong playlist mẫu và tính cách của Quan Vũ.

## Chi tiết các bước (STEPS) trong luồng mới (v5)

**Bước 1 — Cào 3000 video Youtube và phân loại** (`src/step1_keyword_stats.py`)
- Tìm kiếm các video liên quan đến các từ khoá: Quan Vũ, Quan Công, Quan Vân Trường, Quan Thánh...
- Mỗi từ khoá dự kiến lấy ~500 video -> Tổng cộng thu thập gần 3000 video.
- Thu thập thông tin: tiêu đề, lượt xem, lượt bình luận, ngày đăng, v.v. để thống kê độ phổ biến.

**Bước 2 - Lọc data rác từ 3000 dữ liệu và chỉ lấy những vấn đề liên quan** (`src/step2_filter_3000_videos.py`)
- Làm sạch dữ liệu từ kết quả của Bước 1.
- Loại bỏ các video không khả dụng (video bị chặn, không xem được).
- Loại bỏ các video không liên quan đến chủ đề chính.
- Output: Danh sách video đã được làm sạch và chuẩn hóa.

**Bước 3 - Phân loại video và vẽ biểu đồ 3000 video youtube** (`src/step3_visualize_3000_video.py`)
- Phân loại các video (đã lọc ở Bước 2) theo các chủ đề:
  + Phân tích lịch sử
  + Lý do cái chết
  + Tín ngưỡng
  + Kịch cải lương tiếng Trung
  + Khác...
- Vẽ biểu đồ thể hiện sự phân bổ của 3000 video theo các chủ đề này, biểu đồ tổng quan về lượt xem, bình luận.

**Bước 4 — Crawl comment playlist** (`src/step4_crawl_comments.py`)
- Cào dữ liệu bình luận từ các video trong playlist mẫu (để phân tích sâu về keyword/tính cách).
- Làm sạch text comment trước khi chuyển qua bước phân tích tiếp theo.

**Bước 5 — Phân tích sentiment trên mẫu video playlist** (`src/step5_sentiment_analysis.py`)
- Tiến hành phân tích cảm xúc (Sentiment Analysis) trên tập comment của Bước 4 (Dùng PhoBERT hoặc từ điển cảm xúc).
- Trích xuất ra các keyword hay xuất hiện trong comment của các video thuộc playlist này.

**Bước 6 — Phân loại tính cách và vẽ biểu đồ** (`src/step6_visualize.py`)
- Từ các keyword đã phân tích ở Bước 5, lọc ra các keyword liên quan đến tính cách của Quan Vũ:
  + Ví dụ: trượng nghĩa, yêu nước, nóng tính, nhân nghĩa, kiêu ngạo, v.v.
- Tính toán tỷ lệ phần trăm các tính cách này được nhắc đến trong các comment/video.
- Trực quan hóa (Vẽ biểu đồ):
  + Biểu đồ Sentiment tổng thể.
  + Biểu đồ tỷ lệ (Pie chart/Bar chart) các tính cách đặc trưng của Quan Vũ.

## Kế hoạch triển khai mã nguồn (Implementation Plan)

1. **Cập nhật `src/step1_keyword_stats.py`**
   - Thay đổi logic `yt-dlp` để search với các từ khoá mục tiêu.
   - Giới hạn số lượng trả về mỗi từ khoá để đạt được 3000 video.
   - Lưu kết quả ra file `data/v5_3000_videos_raw.csv`.

2. **Tạo mới `src/step2_filter_3000_videos.py`**
   - Đọc từ `v5_3000_videos_raw.csv`.
   - Lọc bỏ các dòng lỗi, video không xem được hoặc tiêu đề không chứa key chính.
   - Lưu ra file `v5_3000_videos_filtered.csv`.

3. **Tạo mới `src/step3_visualize_3000_video.py`**
   - Đọc dữ liệu từ `v5_3000_videos_filtered.csv`.
   - Viết các regex/keyword rules để map từng video vào các category (Lịch sử, Cái chết, Tín ngưỡng, Cải lương...).
   - Dùng `matplotlib` / `seaborn` / `plotly` vẽ biểu đồ phân bổ chủ đề, lưu tại thư mục `report/v5/`.

4. **Cập nhật / tạo `src/step4_crawl_comments.py`**
   - Lấy danh sách video từ playlist mục tiêu.
   - Cào comment cho mỗi video và lưu lại thành `data/v5_comments_raw.csv`.

5. **Cập nhật / tạo `src/step5_sentiment_analysis.py`**
   - Phân tích cảm xúc bằng PhoBERT.
   - Trích xuất các n-grams hoặc keyword phổ biến từ nội dung comment bằng các thư viện NLP (như `underthesea` hoặc tf-idf cơ bản).
   - Lưu kết quả ra `data/v5_comments_labeled.csv` và `data/v5_extracted_keywords.csv`.

6. **Tạo mới `src/step6_visualize.py`**
   - Tính tỷ lệ các keyword mô tả tính cách Quan Vũ (map danh sách keyword tính cách).
   - Vẽ các biểu đồ tỷ lệ phần trăm tính cách và kết quả sentiment.
   - Lưu biểu đồ ở dạng ảnh / html tại `report/v5/`.

7. **Cập nhật `src/run_all.py` (hoặc tạo script chạy riêng v5)**
   - Cấu hình mảng `STEPS` với 6 module mới trên.
   - Tổ chức gọi thực thi tuần tự các bước, handle error nếu một bước bị lỗi.
