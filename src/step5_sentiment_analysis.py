"""BƯỚC 5 (V5): Phân tích cảm xúc và trích xuất keyword.
- Dùng PhoBERT đánh giá sentiment (tích cực, tiêu cực, trung tính) cho comment.
- Trích xuất keyword phổ biến (tính cách Quan Vũ).
"""

import pandas as pd
from pathlib import Path
from tqdm import tqdm
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from normalize import normalize, tokenize_for_phobert
from lexicon import LEXICON_POS, LEXICON_NEG, HISTORY_DOMAIN_KEYWORDS, QUESTION_PATTERNS

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODEL_NAME = "wonrax/phobert-base-vietnamese-sentiment"

def load_model():
    print(f"[*] Đang tải mô hình {MODEL_NAME}...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.to(device)
    model.eval()
    return tokenizer, model, device

def analyze_sentiment(texts, tokenizer, model, device, batch_size=32):
    results = []
    # Map label của wonrax/phobert-base-vietnamese-sentiment: 0: NEG, 1: POS, 2: NEU
    label_map = {0: "tiêu cực", 1: "tích cực", 2: "trung tính"}
    
    CONF_THRESHOLD = 0.60
    CONF_THRESHOLD_NEG = 0.75
    DOMAIN_THRESHOLD = 0.90
    
    for i in tqdm(range(0, len(texts), batch_size), desc="Sentiment Analysis"):
        batch_texts = texts[i:i+batch_size]
        batch_results = [None] * len(batch_texts)
        
        batch_to_predict = []
        indices_to_predict = []
        
        for idx, t in enumerate(batch_texts):
            words = t.split()
            t_lower = t.lower()
            
            # 1. Lexicon Shortcut (V2 & V3)
            if len(words) <= 8:
                is_pos = any(p in t_lower for p in LEXICON_POS)
                is_neg = any(n in t_lower for n in LEXICON_NEG)
                if is_pos and not is_neg:
                    batch_results[idx] = {"sentiment": "tích cực", "score_pos": 0.95, "score_neu": 0.05, "score_neg": 0.0, "source": "lexicon"}
                    continue
                elif is_neg and not is_pos:
                    batch_results[idx] = {"sentiment": "tiêu cực", "score_pos": 0.0, "score_neu": 0.05, "score_neg": 0.95, "source": "lexicon"}
                    continue
            
            batch_to_predict.append(t)
            indices_to_predict.append(idx)
            
        if batch_to_predict:
            tokenized_batch = [tokenize_for_phobert(t) for t in batch_to_predict]
            inputs = tokenizer(tokenized_batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model(**inputs)
                probs = F.softmax(outputs.logits, dim=1).cpu().numpy()
                
            for local_idx, prob in zip(indices_to_predict, probs):
                p_neg, p_pos, p_neu = float(prob[0]), float(prob[1]), float(prob[2])
                max_id = int(prob.argmax())
                label = label_map[max_id]
                score = float(prob[max_id])
                source = "model"
                
                t_lower = batch_texts[local_idx].lower()
                words = t_lower.split()
                
                # 2. Confidence gating
                if label == "tiêu cực" and score < CONF_THRESHOLD_NEG:
                    label = "trung tính"
                    source = "low_conf"
                elif label in ["tích cực", "trung tính"] and score < CONF_THRESHOLD:
                    label = "trung tính"
                    source = "low_conf"
                    
                # 3. Margin check
                if label in ["tiêu cực", "tích cực"] and abs(p_pos - p_neg) < 0.15:
                    label = "trung tính"
                    source = "low_conf_margin"

                # 4. V3 Post-processing Heuristics
                if label == "tiêu cực":
                    # Heuristic 1: Question -> NEU
                    if "?" in t_lower or any(q in t_lower for q in QUESTION_PATTERNS):
                        label = "trung tính"
                        source = "heuristic_question"
                    
                    # Heuristic 3: Domain history -> raise threshold
                    domain_count = sum(1 for kw in HISTORY_DOMAIN_KEYWORDS if kw in t_lower)
                    if domain_count >= 2 and p_neg < DOMAIN_THRESHOLD:
                        label = "trung tính"
                        source = "heuristic_domain"
                    
                    # Heuristic 4: Short neutral
                    if len(words) <= 3 and p_neg < 0.95:
                        label = "trung tính"
                        source = "heuristic_short"
                        
                    # Heuristic 5: Mixed sentiment
                    if p_pos > 0.15 and p_neg > 0.15:
                        label = "trung tính"
                        source = "heuristic_mixed"
                
                batch_results[local_idx] = {
                    "sentiment": label,
                    "score_pos": round(p_pos, 4),
                    "score_neu": round(p_neu, 4),
                    "score_neg": round(p_neg, 4),
                    "source": source
                }
                
        results.extend(batch_results)
        
    return results

def extract_keywords(df):
    """Trích xuất danh sách các từ xuất hiện nhiều trong comment (n-grams/keywords)."""
    print("[*] Đang trích xuất keyword...")
    from collections import Counter
    from underthesea import word_tokenize
    
    # Keyword tính cách mẫu liên quan đến Quan Vũ
    TARGET_TRAITS = [
        "trượng nghĩa", "yêu nước", "nóng tính", "nhân nghĩa", 
        "kiêu ngạo", "trung thành", "anh hùng", "dũng mãnh", "trung nghĩa",
        "hào kiệt", "trung thần", "nghĩa khí", "võ thánh", "tín nghĩa"
    ]
    
    word_counts = Counter()
    
    for text in tqdm(df['normalized_text'], desc="Extract Keywords"):
        if not text:
            continue
        words = word_tokenize(text)
        # Lọc stopwords cơ bản và các từ ngắn
        words = [w.lower() for w in words if len(w) > 1]
        word_counts.update(words)
        
        # Thêm 2-grams (bigrams) để bắt các từ ghép nếu underthesea tách sai
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        word_counts.update(bigrams)
        
    extracted = []
    for trait in TARGET_TRAITS:
        count = word_counts.get(trait, 0)
        # Nếu chưa tìm thấy thì thử đếm chuỗi thay vì token
        if count == 0:
            count = df['normalized_text'].str.contains(trait).sum()
        extracted.append({"keyword": trait, "count": count})
        
    df_kw = pd.DataFrame(extracted)
    df_kw = df_kw.sort_values(by="count", ascending=False)
    return df_kw

def main():
    in_file = DATA_DIR / "v5_comments_raw.csv"
    if not in_file.exists():
        print(f"[!] Không tìm thấy file {in_file}")
        return
        
    df = pd.read_csv(in_file)
    print(f"[*] Đọc {len(df)} comments từ {in_file.name}")
    
    # Chuẩn hóa
    print("[*] Đang chuẩn hóa text...")
    df['normalized_text'] = df['text'].astype(str).apply(lambda x: normalize(x))
    
    # Xóa dòng trống
    df = df[df['normalized_text'].str.strip() != ""]
    print(f"[*] Số lượng comments hợp lệ: {len(df)}")
    
    if len(df) == 0:
        print("[!] Không có comment hợp lệ để phân tích.")
        return
        
    tokenizer, model, device = load_model()
    
    sentiments_data = analyze_sentiment(df['normalized_text'].tolist(), tokenizer, model, device)
    
    df['sentiment'] = [row['sentiment'] for row in sentiments_data]
    df['score_pos'] = [row['score_pos'] for row in sentiments_data]
    df['score_neu'] = [row['score_neu'] for row in sentiments_data]
    df['score_neg'] = [row['score_neg'] for row in sentiments_data]
    df['source'] = [row['source'] for row in sentiments_data]
    
    out_labeled = DATA_DIR / "v5_comments_labeled.csv"
    df.to_csv(out_labeled, index=False, encoding="utf-8-sig")
    print(f"[OK] Đã lưu kết quả phân tích cảm xúc vào {out_labeled.name}")
    
    df_kw = extract_keywords(df)
    out_kw = DATA_DIR / "v5_extracted_keywords.csv"
    df_kw.to_csv(out_kw, index=False, encoding="utf-8-sig")
    print(f"[OK] Đã lưu danh sách keyword vào {out_kw.name}")

if __name__ == "__main__":
    main()
