# Giải pháp V4 — Phân tích keyword tính cách Quan Vũ trên YouTube

## Tổng quan

V4 tập trung vào phân tích **keyword tính cách** của Quan Vũ trong comments YouTube,
thay vì sentiment chung như V1–V3.

## Luồng xử lý

1. **Step 1** (`src/step1_keyword_stats.py`): Search 500 video/keyword × 6 keyword,
   phân loại chủ đề (lịch sử, nguyên nhân chết, tín ngưỡng, kịch cải lương, khác)
2. **Step 2** (`src/step2_crawl_comments.py`): Crawl comments từ top 30 video,
   trích xuất keyword phổ biến
3. **Step 3** (`src/step3_sentiment.py`): Lọc keyword tính cách (30 tích cực + 20 tiêu cực),
   tính tỷ lệ %
4. **Visualize** (`src/visualize.py`): 7 biểu đồ (2 cũ + 5 mới)

## Cách chạy

```bash
python src/step1_keyword_stats.py
python src/step2_crawl_comments.py
python src/step3_sentiment.py
python src/visualize.py
```
