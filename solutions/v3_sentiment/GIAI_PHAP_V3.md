# Giải pháp V3 — Giảm False-Negative trong phân loại sentiment

> Mục tiêu: giảm tỉ lệ NEG sai (28.8% → ~15%) bằng domain-aware heuristics và cải thiện tiền xử lý.
> **Sửa trực tiếp vào `src/`** — cùng cách tiếp cận với V2.

---

## 1. Vấn đề quan sát ở V2

Dù V2 đã cải thiện đáng kể so với V1 (verify id2label, lexicon shortcut, confidence gating), phân tích `comments_labeled.csv` cho thấy **NEG vẫn chiếm 28.8%** (277/962) — cao hơn thực tế.

### Phân bố kết quả V2

| Label | Count | % |
|-------|-------|------|
| POS   | 350   | 36.4 |
| NEU   | 335   | 34.8 |
| NEG   | 277   | 28.8 |

Đáng chú ý:
- **100% NEG** đến từ model (không từ lexicon hay low_conf)
- NEG avg `score_neg` = 0.953 — model rất tự tin nhưng **sai**
- 246/277 NEG có `score_neg > 0.9`

### 5 nguyên nhân chính

| # | Nguyên nhân | Tỷ lệ | Ví dụ |
|---|-------------|--------|-------|
| 1 | **Domain Tam Quốc** — từ vựng chiến tranh (chém, chết, thua) trong ngữ cảnh bàn luận lịch sử | ~50% NEG | `"trưong phi"` → NEG 0.985 |
| 2 | **Comment không dấu** — telex/romanized | 8.3% NEG | `"Xin tiep tuc duy tri"` → NEG 0.986 |
| 3 | **Câu hỏi trung tính** bị gán NEG | ~10% NEG | `"Cho hỏi cây thanh long đại đao làm bằng gì?"` → NEG 0.944 |
| 4 | **Từ lóng khen** ("dữ", "ghê") bị hiểu tiêu cực | ~5% NEG | `"Quá dữ"` → NEG 0.987 |
| 5 | **Liệt kê tên nhân vật** không có sentiment | ~5% NEG | `"Nhất Lữ Nhì Triệu Ba Điển Vi..."` → NEG 0.987 |

---

## 2. Kiến trúc V3

```
text thô
   │
   ▼
[normalize V2]  ─►  (giữ nguyên pipeline V2)
   │
   ▼
[lexicon shortcut V3]  ─►  MỞ RỘNG: thêm từ lóng khen ("dữ", "ghê", "điên")
   │                        + tăng giới hạn lên ≤ 8 token
   ▼
[PhoBERT inference]
   │
   ▼
[confidence gating V3]  ─►  CONF_THRESHOLD_NEG riêng = 0.75
   │                        (thay vì dùng chung 0.60 cho cả 3 class)
   ▼
[post-processing V3]    ─►  5 heuristics mới:
   │                        1. Question detection → NEU
   │                        2. Listing/name-only → NEU
   │                        3. Domain history keywords → nâng ngưỡng NEG
   │                        4. Short neutral phrases → NEU
   │                        5. Mixed sentiment → NEU
   ▼
nhãn cuối + score
```

---

## 3. Chi tiết thay đổi

### 3.1. Mở rộng Lexicon (`lexicon.py`)

Thêm từ lóng khen kiểu Nam Bộ vào `LEXICON_POS`:
```python
"quá dữ", "dữ quá", "ghê quá", "quá ghê", "điên quá", "kinh quá",
"sốc quá", "dữ", "ghê", "kinh", "điên",  # 1 token = cảm thán khen
```

Thêm domain-specific keywords:
```python
HISTORY_DOMAIN_KEYWORDS = {
    "quan vũ", "quan công", "tào tháo", "lưu bị", "trương phi",
    "triệu vân", "lữ bố", "tam quốc", ...
}
```

### 3.2. Confidence Threshold riêng cho NEG (`step3_sentiment.py`)

```python
CONF_THRESHOLD_NEG = 0.75   # NEG cần tự tin hơn mới được giữ
CONF_THRESHOLD     = 0.60   # POS/NEU giữ nguyên
```

### 3.3. Post-processing Heuristics (`step3_sentiment.py`)

5 rules áp dụng **sau** khi model predict:

1. **Question → NEU**: nếu text chứa `?` hoặc pattern hỏi → chuyển NEG sang NEU
2. **Name listing → NEU**: nếu text chủ yếu là tên riêng/liệt kê → chuyển NEG → NEU
3. **Domain history → raise threshold**: nếu text chứa ≥2 `HISTORY_DOMAIN_KEYWORDS`, cần `score_neg ≥ 0.90` mới giữ NEG
4. **Short neutral → NEU**: câu ngắn (≤3 token) mà model gán NEG với score < 0.95 → NEU
5. **Mixed sentiment → NEU**: nếu `score_pos > 0.15` và `score_neg > 0.15` → NEU (mâu thuẫn)

### 3.4. Mở rộng phạm vi Lexicon shortcut

Tăng giới hạn token từ ≤5 lên ≤8 để bắt thêm các câu khen/chê rõ ràng nhưng dài hơn.

---

## 4. Thay đổi trong `src/`

```
src/
├── lexicon.py           ← SỬA: thêm LEXICON_POS lóng, thêm HISTORY_DOMAIN_KEYWORDS
├── step3_sentiment.py   ← SỬA: thêm post-processing, CONF_THRESHOLD_NEG
└── normalize.py         ← KHÔNG ĐỔI
```

---

## 5. Cấu hình mới (biến môi trường)

| ENV | Default | Tác dụng |
|---|---|---|
| `CONF_THRESHOLD_NEG` | `0.75` | Ngưỡng riêng cho nhãn NEG |
| `DOMAIN_THRESHOLD` | `0.90` | Ngưỡng NEG khi phát hiện domain lịch sử |
| `LEXICON_MAX_TOKENS` | `8` | Giới hạn token cho lexicon shortcut |

(Các biến V2 giữ nguyên)

---

## 6. Rủi ro & cảnh báo

- **Heuristics có thể over-correct**: câu thật sự NEG trong ngữ cảnh Tam Quốc có thể bị flip sang NEU
- **Question pattern false positive**: câu "tại sao lại tệ vậy?" là NEG thật nhưng có thể bị gán NEU
- **Cần ground truth**: 200 nhãn tay để đo F1 vẫn là TODO
