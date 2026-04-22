# Tiền Xử Lý Văn Bản Tiếng Việt

## 1. Pipeline trong `clean_text`

```
raw text
   │
   ▼  emoji.replace_emoji        → bỏ emoji
   ▼  re.sub(r"http\S+", " ")    → bỏ URL
   ▼  re.sub(r"<[^>]+>", " ")    → bỏ HTML tag
   ▼  re.sub(r"[^\wÀ-ỹ\s]", " ") → bỏ ký tự đặc biệt
   ▼  re.sub(r"\s+", " ")        → gộp khoảng trắng
   ▼  .lower()                   → viết thường
   ▼  underthesea.word_tokenize  → tách từ với "_"
   │
   ▼ "tôi yêu_nước việt_nam"
```

## 2. Tại sao tách từ?

PhoBERT được train trên dữ liệu đã segment bằng VnCoreNLP → dấu `_` nối các từ ghép. Nếu bỏ qua bước này, độ chính xác giảm 5–10%.

## 3. Mở rộng: chuẩn hoá teen-code

Tự build dictionary `data/teencode.json`:
```json
{
  "ko": "không",
  "k": "không",
  "dc": "được",
  "ahihi": "",
  "vc": "vãi",
  "wa": "quá"
}
```

Hàm chuẩn hoá:
```python
import json
TEEN = json.load(open("data/teencode.json", encoding="utf-8"))

def normalize_teen(text):
    return " ".join(TEEN.get(w, w) for w in text.split())
```

Chèn trước `word_tokenize`.

## 4. Bỏ dấu hay giữ dấu?

**Giữ dấu**. PhoBERT phụ thuộc vào dấu tiếng Việt. Nếu input không dấu (vd: "quan vu rat gioi"), nên dùng thêm thư viện như `vietnamese-tone-recovery` để khôi phục.

## 5. Deduplicate

Comment spam thường lặp. Sau khi `clean`, dedupe theo `(videoId, clean)`:
```python
df = df.drop_duplicates(subset=["videoId", "clean"])
```
