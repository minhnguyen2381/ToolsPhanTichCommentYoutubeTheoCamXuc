# V2 Sentiment — Hướng dẫn nhanh

Giải pháp nâng cấp cho `src/step3_sentiment.py`. **Không ghi đè V1** — đặt trong `solutions/v2_sentiment/` để chạy song song và so sánh.

## Cấu trúc

```
solutions/v2_sentiment/
├── GIAI_PHAP_V2.md         ← phân tích vấn đề V1 + thiết kế V2 (đọc trước)
├── README.md               ← file này
├── normalize.py            ← chuẩn hoá text, teencode, emoji, elongation
├── lexicon.py              ← whitelist POS/NEG cho câu ngắn
├── step3_sentiment_v2.py   ← script chính (drop-in)
└── eval_sample.py          ← random sample → gán tay → đo accuracy/F1
```

## Cách chạy

```bash
# Bật venv của project
source .venv/Scripts/activate

# Chạy V2 (đọc data/comments_raw.csv, ghi ra data/comments_labeled_v2.csv)
python solutions/v2_sentiment/step3_sentiment_v2.py

# (Tuỳ chọn) bật phục hồi dấu cho comment telex
USE_DIACRITIC_RESTORE=1 python solutions/v2_sentiment/step3_sentiment_v2.py

# (Tuỳ chọn) bật ensemble với visobert (nặng ~1GB)
USE_ENSEMBLE=1 python solutions/v2_sentiment/step3_sentiment_v2.py
```

## Đo chất lượng

```bash
# Bước 1: tạo file 200 sample để gán tay
python solutions/v2_sentiment/eval_sample.py --sample 200

# Bước 2: mở data/eval_sample.csv, điền cột `gold` với POS/NEU/NEG

# Bước 3: tính accuracy / macro-F1 / confusion matrix
python solutions/v2_sentiment/eval_sample.py --score
```

## Biến môi trường

| ENV | Default | |
|---|---|---|
| `USE_DIACRITIC_RESTORE` | 0 | Phục hồi dấu cho text telex |
| `USE_ENSEMBLE` | 0 | Trung bình prob với visobert |
| `CONF_THRESHOLD` | 0.60 | Dưới ngưỡng → NEU |
| `MARGIN_THRESHOLD` | 0.15 | `|p_POS - p_NEG|` dưới ngưỡng → NEU |
| `BATCH_SIZE` | 32 | Inference batch |

## Lưu ý

- Lần đầu chạy ensemble sẽ tải thêm ~1GB model.
- File output là `comments_labeled_v2.csv` (không đè bản V1) — `visualize.py` mặc định đọc bản V1; nếu muốn vẽ V2, đổi đường dẫn trong `visualize.py` hoặc copy đè thủ công sau khi xác nhận tốt hơn.
- Tham khảo lý do thiết kế từng bước trong `GIAI_PHAP_V2.md`.
