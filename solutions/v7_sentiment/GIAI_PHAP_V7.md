# Giải pháp V7 — Phân loại nội dung & xu thế năm Google

## Mục tiêu

Bổ sung cho spec V6 mục **II.2** và **II.3** (khảo sát web search 5 keyword cốt lõi Quan):

1. **Mục 2:** Liệt kê các keyword Quan Vũ / Quan Công / Quan Thánh / Quan Thánh Đế Quân / Quan Vân Trường xuất hiện dưới dạng nội dung nào (sách, nghiên cứu, báo cáo, học thuật, giải trí, điện ảnh, tin tức…).
2. **Mục 3:** Bảng đánh giá xu thế — tỷ lệ bài đăng theo **năm (2000–nay)** và theo **loại nội dung**.

Kế thừa pipeline V6 (`step6_google_search.py`, `google_content_classifier.py`), không thay đổi luồng YouTube/sentiment.

## 5 keyword cốt lõi

| STT | Keyword | Query search (ghép Tam quốc) |
|-----|---------|------------------------------|
| 1 | Quan Vũ | Quan Vũ Tam quốc |
| 2 | Quan Công | Quan Công Tam quốc diễn nghĩa |
| 3 | Quan Thánh | Quan Thánh Tam quốc |
| 4 | Quan Thánh Đế Quân | Quan Thánh Đế Quân Tam quốc |
| 5 | Quan Vân Trường | Quan Vân Trường Tam quốc |

## Nguồn dữ liệu

- **Crawl hybrid:** 5 query cốt lõi (50 kết quả/query) + merge hàng từ `v6_google_results_raw.csv` nếu query map được về keyword cốt lõi.
- **Tái phân tích:** `--v7-only` hoặc `--reclassify-only` đọc raw có sẵn, không crawl lại.

## Loại nội dung (phân loại)

Dùng classifier 3 tầng (`google_content_classifier.py`): domain → keyword signal → query intent.

Các nhóm chính: Tin tức, Bách khoa, Văn học, Giáo dục, Tín ngưỡng, Lịch sử, Giải trí, Điện ảnh, Game, Sách, Blog, Hình ảnh, Thương mại, Du lịch, MXH, Nghiên cứu, Học thuật, Báo cáo, Khác.

## Output CSV

### `v7_google_keyword_content_types.csv` (mục 2)

```
core_keyword, content_type, so_ket_qua, ty_le_pct
```

Mẫu:

| core_keyword | content_type | so_ket_qua | ty_le_pct |
|--------------|--------------|------------|-----------|
| Quan Vũ | Tin tức | 12 | 24.0 |
| Quan Vũ | Giải trí | 8 | 16.0 |
| Quan Công | Văn học | 5 | 10.0 |

### `v7_google_year_content_trend.csv` (mục 3)

```
nam, content_type, so_ket_qua, ty_le_pct
```

Mẫu:

| nam | content_type | so_ket_qua | ty_le_pct |
|-----|--------------|------------|-----------|
| 2024 | Tin tức | 15 | 12.5 |
| 2024 | Giải trí | 10 | 8.3 |
| 2025 | Tin tức | 22 | 18.2 |

`ty_le_pct` tính trên tổng lượt đếm (mỗi năm trong text có thể đếm nhiều lần nếu một SERP nhắc nhiều năm).

### `v7_google_results_enriched.csv` (chi tiết nội bộ)

```
keyword, core_keyword, title, url, domain, content_type, nam
```

## Lệnh chạy

```bash
# Crawl đầy đủ V6 + sinh output V7
python src/step6_google_search.py

# Chỉ build V7 từ raw V6 có sẵn
python src/step6_google_search.py --v7-only

# Phân loại lại V6 + V7 từ raw
python src/step6_google_search.py --reclassify-only

# Biểu đồ & báo cáo (gồm section V7)
python src/step7_visualize_v6.py
```

## Giới hạn

- **Năm** trích từ title/description SERP (regex `20xx`), không phải ngày xuất bản thực.
- Phân loại dựa rule domain/keyword; có thể bổ sung `DOMAIN_RULES` khi gặp site mới.
