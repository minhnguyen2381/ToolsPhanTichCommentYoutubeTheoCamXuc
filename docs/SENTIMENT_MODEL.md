# Mô Hình Sentiment cho Tiếng Việt

## 1. So sánh 3 phương án

| | A. PhoBERT fine-tuned | B. XLM-RoBERTa | C. Rule-based |
|---|---|---|---|
| Repo / nguồn | `wonrax/phobert-base-vietnamese-sentiment` | `cardiffnlp/twitter-xlm-roberta-base-sentiment` | VnSentiWordNet |
| Kích thước | ~500 MB | ~1.1 GB | <10 MB |
| Cần GPU? | Khuyến nghị | Khuyến nghị | Không |
| Độ chính xác (VN) | ~85–88% | ~78% | ~65% |
| Xử lý mỉa mai | Trung bình | Trung bình | Yếu |
| Hỗ trợ teen-code | Khá | Khá | Yếu |
| Khuyến nghị | ⭐ Mặc định | Khi có dữ liệu pha tiếng Anh | Baseline / chạy nhanh |

## 2. Tại sao chọn PhoBERT?

- Pre-train trên 20GB văn bản tiếng Việt → hiểu cú pháp + từ ghép tốt hơn mBERT/XLM-R.
- Đã được fine-tune sẵn cho 3 nhãn `POS / NEU / NEG`, không cần train lại.
- Tốc độ ổn: ~50 comment/giây trên RTX 3060, ~5 comment/giây trên CPU i5.

## 3. Lưu ý khi diễn giải kết quả

- Cột `score` là độ tự tin của model. **Lọc `score < 0.6`** nếu muốn chỉ giữ dự đoán chắc chắn.
- PhoBERT yếu với **mỉa mai/châm biếm** (~15-20% sai số). Ví dụ:
  - "Quan Vũ giỏi quá ha, để mất Kinh Châu thôi" → model có thể gán POS.
- Với teen-code (vd: "Quan vu chx j ahihi") nên có bước normalize riêng (xem [PREPROCESSING.md](PREPROCESSING.md)).

## 4. Tự fine-tune (tuỳ chọn)

Nếu cần độ chính xác cao hơn:

1. Gắn nhãn thủ công ~500–1000 comment.
2. Dùng `transformers.Trainer` với `vinai/phobert-base` làm backbone.
3. Tham khảo notebook chính thức: <https://github.com/VinAIResearch/PhoBERT>.

## 5. Thay đổi model

Trong `src/step3_sentiment.py`:

```python
MODEL_NAME = "wonrax/phobert-base-vietnamese-sentiment"
LABELS = ["NEG", "POS", "NEU"]
```

Đổi thành model khác (vd: `5CD-AI/Vietnamese-Sentiment-visobert`) và **kiểm tra thứ tự `LABELS`** khớp với `model.config.id2label`.
