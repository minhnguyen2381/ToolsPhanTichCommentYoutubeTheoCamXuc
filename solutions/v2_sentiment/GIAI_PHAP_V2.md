# Giải pháp V2 — Cải thiện phân loại sentiment (`step3_sentiment.py`)

> Mục tiêu: giảm tỉ lệ nhãn sai (đặc biệt nhãn NEG bị gán nhầm) trong pipeline phân tích bình luận YouTube tiếng Việt.
> **Áp dụng trực tiếp vào `src/`** — không tạo thư mục riêng, không fork script.

---

## 1. Vấn đề quan sát được ở V1

Khi rà soát `data/comments_labeled.csv` (sản phẩm của V1):

| Hiện tượng | Ví dụ |
|---|---|
| Câu khen ngắn bị gán NEG | `"Hay wa"` → NEG (0.99); `"Hay quá"` → NEG (0.97) |
| Cùng nội dung, nhãn ngược nhau khi đảo từ | `"quá hay"` → POS / `"hay quá"` → NEG |
| Comment không dấu (telex) bị đẩy về NEG | `"Toan la dien vien gao coi … Xin tiep tuc duy tri"` → NEG |
| Câu hỏi / câu trung tính bị gán NEG | `"Cho hỏi cây thanh long đại đao làm bằng gì vậy"` → NEG |
| Cảm thán "ghê", "dữ", "kinh" (khen kiểu lóng) bị hiểu tiêu cực | `"Quá dữ"` → NEG |
| Confidence thấp (<0.7) vẫn được "đóng nhãn" cứng | nhiều dòng score 0.5–0.65 |

### Nguyên nhân gốc
1. **Thứ tự `LABELS` hardcode** — nếu `id2label` của model khác giả định thì toàn bộ kết quả lệch.
2. **Mất dấu** — PhoBERT được train trên text có dấu, comment telex hành xử ngoài phân phối.
3. **Tiền xử lý làm nghèo tín hiệu** — emoji bị xoá, dấu câu bị xoá, teencode không chuẩn hoá, từ kéo dài (`hayyy`, `quááá`) không gộp.
4. **Không có ngưỡng tin cậy** — score 0.51 và score 0.99 đều bị quy về một nhãn cứng.
5. **Không có lexicon "an toàn"** — câu rất ngắn (1–4 token) lệ thuộc hoàn toàn vào dao động của model.
6. **Không có ground truth** — không biết NEG cao là do dữ liệu thật sự tiêu cực hay do model lệch.

---

## 2. Kiến trúc V2

```
text thô
   │
   ▼
[normalize]  ─►  lower / unicode NFC / xoá URL+HTML / strip ký tự rác
   │            (giữ lại . ! ? và emoji)
   ▼
[demojize]   ─►  thay emoji bằng token "tích_cực"/"tiêu_cực" (map thủ công)
   │
   ▼
[teencode + elongation]  ─►  ko→không, k→không, dc/đc→được, wa→quá, j→gì, ntn→như thế nào,
   │                         (.)\1{2,} → \1   (vd: hayyy → hay)
   ▼
[restore_diacritics]     ─►  nếu tỉ lệ ký tự có dấu < 0.15 thì gọi mô hình phục hồi dấu
   │                         (tuỳ chọn — bật bằng env USE_DIACRITIC_RESTORE=1)
   ▼
[lexicon shortcut]       ─►  nếu câu ≤ 5 token và match từ khoá trong whitelist
   │                         → trả nhãn từ lexicon, BỎ QUA model
   ▼
[underthesea word_tokenize]
   │
   ▼
[PhoBERT batch inference]  ─►  batch_size=32, dùng model.config.id2label thật
   │
   ▼
[confidence gating]      ─►  max_prob < 0.6  →  NEU
   │                         |p_POS - p_NEG| < 0.15  →  NEU
   ▼
[ensemble (tuỳ chọn)]    ─►  trung bình xác suất với visobert-sentiment
   │
   ▼
nhãn cuối + score
```

---

## 3. Chi tiết các kỹ thuật

### 3.1. Verify `id2label`
Tránh hardcode `["NEG", "POS", "NEU"]`. Đọc thẳng từ model:
```python
id2label = model.config.id2label   # vd {0: 'NEG', 1: 'POS', 2: 'NEU'}
```
In một lần khi khởi động và dùng `id2label[idx]` thay cho list constant.

### 3.2. Chuẩn hoá text
- `unicodedata.normalize("NFC", t)` để gộp tổ hợp dấu.
- Giữ `! ? . ,` (PhoBERT có học các token này).
- Lowercase **trước** khi tokenize (PhoBERT tokenizer expect input "tự nhiên", lowercase chỉ làm sạch chữ in hoa lẫn lộn).
- Gộp ký tự lặp: `re.sub(r'(.)\1{2,}', r'\1\1', t)` (giữ tối đa 2 lần để bảo toàn từ như "ggg" thành "gg" — thường an toàn hơn về 1).

### 3.3. Map teencode
Một dictionary nhỏ (~50 mục) đủ phủ phần lớn comment YouTube VN:
```
ko, k, kh, hk → không
dc, đc       → được
wa           → quá
j            → gì
ntn          → như thế nào
ah, ak       → à
mn           → mọi người
mik, mh      → mình
trc          → trước
sml, vl, vcl → (giữ nguyên — là intensifier có sentiment)
```

### 3.4. Emoji → token
Thay vì xoá, dịch thành token sentiment:
```
👍 ❤ 😍 🥰 🌷 🌹 🔥 💯 👏  → " tích_cực "
👎 😡 🤬 💩 😤 😠            → " tiêu_cực "
😂 🤣 😅                     → " hài_hước "
```
Phần còn lại có thể `emoji.demojize(language='vi')` để giữ ngữ nghĩa.

### 3.5. Phục hồi dấu (tuỳ chọn)
Nếu tỉ lệ ký tự có dấu < 15% thì coi là telex/no-tone, gọi:
- `bmd1905/vietnamese-correction` (T5), hoặc
- `nguyenvulebinh/vietnamese-accent-restore`.

Bật bằng env `USE_DIACRITIC_RESTORE=1` để giữ pipeline mặc định nhẹ.

### 3.6. Lexicon shortcut cho câu ngắn
Câu ngắn (≤ 5 token sau tokenize) là nơi PhoBERT dao động nhất. Whitelist:

POS:
```
hay, quá hay, hay quá, tuyệt vời, xuất sắc, đỉnh, quá đỉnh, mê, thích,
cám ơn, cảm ơn, dễ thương, đẹp, tuyệt, chất, ngon, ổn, ok, oke, tốt,
hay wa, hay qua, tuyet voi, cam on, thich, dep, ngon
```

NEG:
```
tệ, dở, chán, thất vọng, ghét, kém, nhảm, rác, ngu, dở tệ, te, do, chan
```

Nếu match → return luôn nhãn lexicon với score 0.95 (đánh dấu source="lexicon" để debug).

### 3.7. Ngưỡng tin cậy → NEU
```python
top, second = sorted(probs, reverse=True)[:2]
if top < 0.60:
    label = "NEU"
elif (label_id_top in {POS_id, NEG_id}) and abs(p_POS - p_NEG) < 0.15:
    label = "NEU"
```
Mục đích: ngừng ép phân loại các câu mà model thật sự không chắc.

### 3.8. Batch inference
Hiện V1 forward 1 câu/lần. V2 dùng `DataLoader`/list-batching, batch_size=32 → tăng tốc 10–20× trên GPU, 3–5× trên CPU.

### 3.9. Ensemble (tuỳ chọn)
Trung bình `softmax` của 2 model cùng task:
- `wonrax/phobert-base-vietnamese-sentiment` (V1)
- `5CD-AI/Vietnamese-Sentiment-visobert` *hoặc* `uitnlp/visobert`

Bật bằng env `USE_ENSEMBLE=1` (tải nặng ~1GB).

### 3.10. Đánh giá định lượng
Thêm script `src/eval_sample.py`:
1. Random sample 200 comment.
2. Xuất ra `data/eval_sample.csv` để gán nhãn tay (cột `gold`).
3. Sau khi user gán xong → tính accuracy / macro-F1 / confusion matrix.

Đây là điều kiện cần để khẳng định V2 thật sự tốt hơn V1 chứ không chỉ "có vẻ tốt hơn".

---

## 4. Đầu ra mới

`data/comments_labeled.csv` (V2) thêm 2 cột:
| Cột | Ý nghĩa |
|---|---|
| `source` | `lexicon` / `model` / `model+ensemble` / `low_conf→NEU` |
| `score_neu`, `score_pos`, `score_neg` | xác suất từng lớp (giữ lại để debug & re-threshold sau này) |

`sentiment_report.csv` không đổi schema → `visualize.py` không cần sửa.

---

## 5. Cấu hình qua biến môi trường

| ENV | Default | Tác dụng |
|---|---|---|
| `USE_DIACRITIC_RESTORE` | `0` | Bật mô hình phục hồi dấu |
| `USE_ENSEMBLE` | `0` | Bật ensemble với visobert |
| `CONF_THRESHOLD` | `0.60` | Ngưỡng tin cậy tối thiểu để giữ nhãn POS/NEG |
| `MARGIN_THRESHOLD` | `0.15` | Khoảng cách tối thiểu giữa P(POS) và P(NEG) |
| `BATCH_SIZE` | `32` | Batch khi inference |
| `MAX_LEN` | `256` | Truncation length |

---

## 6. Thay đổi trong `src/`

Tất cả logic V2 được tích hợp trực tiếp vào các file hiện có trong `src/`:

```
src/
├── step3_sentiment.py   ← VIẾT LẠI (thay thế V1 hoàn toàn)
├── lexicon.py           ← TẠO MỚI — whitelist POS/NEG + teencode map + emoji map
├── normalize.py         ← TẠO MỚI — các hàm tiền xử lý (clean_text, map_emoji, map_teencode, …)
└── eval_sample.py       ← TẠO MỚI — random sample để gán tay & đo accuracy
```

> Không tạo thư mục con, không fork script. `step3_sentiment.py` hiện tại được **ghi đè** bằng phiên bản V2.
> Schema đầu ra của `comments_labeled.csv` mở rộng thêm cột nhưng không xoá cột cũ → `visualize.py` không cần sửa.

---

## 7. Roadmap triển khai (đề xuất ưu tiên)

| Bước | Việc | File thay đổi | Độ khó | Tác động kì vọng |
|---|---|---|---|---|
| 1 | Tạo `src/lexicon.py` (whitelist + teencode + emoji map) | `src/lexicon.py` (mới) | Rất thấp | Cơ sở cho bước 3 |
| 2 | Tạo `src/normalize.py` (clean_text mới, map_emoji, map_teencode, elongation) | `src/normalize.py` (mới) | Thấp | Tiền xử lý đúng |
| 3 | Viết lại `src/step3_sentiment.py`: verify id2label + batch inference + confidence gating + lexicon shortcut | `src/step3_sentiment.py` | Thấp | Cải thiện tổng thể |
| 4 | Tạo `src/eval_sample.py` | `src/eval_sample.py` (mới) | Trung bình | Baseline đo lường |
| 5 | Diacritic restore (tuỳ chọn, env flag) | `src/step3_sentiment.py` | Trung bình | Cứu comment telex |
| 6 | Ensemble visobert (tuỳ chọn, env flag) | `src/step3_sentiment.py` | Cao (RAM/disk) | +2–5% F1 |

---

## 8. Rủi ro & cảnh báo

- **Lexicon thiên lệch**: whitelist do người viết → có thể ép câu thành POS/NEG sai trong ngữ cảnh mỉa mai. Mitigation: chỉ áp dụng cho câu ≤ 5 token.
- **Phục hồi dấu sai ngữ nghĩa**: model có thể "đoán" sai dấu, biến câu trung tính thành tiêu cực. Mitigation: giữ tuỳ chọn tắt mặc định, log diff.
- **Ensemble tăng RAM ~2×**: cân nhắc nếu chạy trên máy <8GB RAM.
- **Vẫn cần ground truth**: mọi cải tiến trên chỉ là "có lý" cho đến khi có 200 nhãn tay để đo F1.
- **Ghi đè V1**: commit hiện tại của `step3_sentiment.py` là V1 — nên tag/branch trước khi ghi đè nếu muốn rollback dễ.
