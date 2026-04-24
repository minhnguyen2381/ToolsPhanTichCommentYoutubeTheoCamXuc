"""BƯỚC 3 (V2): Phân loại sentiment với PhoBERT + lexicon shortcut + confidence gating.

Cải tiến so với V1 (xem `solutions/v2_sentiment/GIAI_PHAP_V2.md`):
- Verify `id2label` thay vì hardcode thứ tự nhãn.
- Tiền xử lý mới (`normalize.py`): emoji-as-token, teencode map, gộp ký tự lặp.
- Lexicon shortcut cho câu ngắn (≤ 5 token) để né dao động của model.
- Confidence gating: low confidence / margin nhỏ → gán NEU.
- Batch inference (mặc định 32) thay vì 1 câu/lần.
- Tuỳ chọn: phục hồi dấu, ensemble với visobert (env flag).
- Cột mới trong CSV: `source`, `score_neu`, `score_pos`, `score_neg`.
"""
import os
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import normalize, tokenize_for_phobert  # noqa: E402
from lexicon import LEXICON_POS, LEXICON_NEG  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODEL_NAME = "wonrax/phobert-base-vietnamese-sentiment"
ENSEMBLE_MODEL_NAME = "5CD-AI/Vietnamese-Sentiment-visobert"

USE_DIACRITIC_RESTORE = os.getenv("USE_DIACRITIC_RESTORE", "0") == "1"
USE_ENSEMBLE = os.getenv("USE_ENSEMBLE", "0") == "1"
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.60"))
MARGIN_THRESHOLD = float(os.getenv("MARGIN_THRESHOLD", "0.15"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
MAX_LEN = int(os.getenv("MAX_LEN", "256"))


# ---------------------------------------------------------------------------
# Lexicon shortcut
# ---------------------------------------------------------------------------
def lexicon_lookup(normalized_text: str):
    """Trả về (label, score) nếu match lexicon, ngược lại None.

    Chỉ áp dụng cho câu ngắn (≤ 5 token sau split khoảng trắng).
    """
    if not normalized_text:
        return None
    tokens = normalized_text.split()
    if len(tokens) > 5:
        return None
    txt = normalized_text.strip()
    if txt in LEXICON_POS:
        return ("POS", 0.95)
    if txt in LEXICON_NEG:
        return ("NEG", 0.95)
    # match token-level cho câu rất ngắn (1-2 token)
    if len(tokens) <= 2:
        for tk in tokens:
            if tk in LEXICON_POS:
                return ("POS", 0.90)
            if tk in LEXICON_NEG:
                return ("NEG", 0.90)
    return None


# ---------------------------------------------------------------------------
# Model loader
# ---------------------------------------------------------------------------
def load_model(model_name: str):
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name).eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    id2label = {int(k): v.upper() for k, v in model.config.id2label.items()}
    print(f"[*] Load {model_name} trên {device}; id2label = {id2label}")
    return tok, model, device, id2label


def build_predictor():
    import torch
    import torch.nn.functional as F

    tok_a, model_a, device, id2label_a = load_model(MODEL_NAME)
    tok_b = model_b = id2label_b = None
    if USE_ENSEMBLE:
        try:
            tok_b, model_b, _, id2label_b = load_model(ENSEMBLE_MODEL_NAME)
        except Exception as e:
            print(f"[!] Không load được model ensemble, tắt: {e}")

    LABEL_ORDER = ["NEG", "NEU", "POS"]

    def _probs_in_order(probs, id2label):
        """Re-order probs theo [NEG, NEU, POS] dựa trên id2label thật của model."""
        out = [0.0, 0.0, 0.0]
        for idx, name in id2label.items():
            name_u = name.upper()
            if name_u in LABEL_ORDER:
                out[LABEL_ORDER.index(name_u)] = float(probs[idx])
        return out

    @torch.no_grad()
    def _infer_batch(texts, tok, model, id2label):
        enc = tok(texts, return_tensors="pt", padding=True,
                  truncation=True, max_length=MAX_LEN).to(device)
        logits = model(**enc).logits
        probs = F.softmax(logits, dim=-1).cpu().tolist()
        return [_probs_in_order(p, id2label) for p in probs]

    def predict_batch(texts):
        """Trả về list (label, score, source, [neg, neu, pos]) cho mỗi text."""
        results = []
        # tách text rỗng để khỏi qua model
        valid_idx, valid_texts = [], []
        for i, t in enumerate(texts):
            if t and t.strip():
                valid_idx.append(i)
                valid_texts.append(t)
            results.append(("NEU", 0.0, "empty", [0.0, 1.0, 0.0]))
        if not valid_texts:
            return results

        probs_a = _infer_batch(valid_texts, tok_a, model_a, id2label_a)
        if model_b is not None:
            probs_b = _infer_batch(valid_texts, tok_b, model_b, id2label_b)
            merged = [
                [(a + b) / 2 for a, b in zip(pa, pb)]
                for pa, pb in zip(probs_a, probs_b)
            ]
            source_tag = "model+ensemble"
        else:
            merged = probs_a
            source_tag = "model"

        for local_i, abs_i in enumerate(valid_idx):
            p = merged[local_i]
            top_val = max(p)
            top_idx = p.index(top_val)
            label = LABEL_ORDER[top_idx]
            sorted_p = sorted(p, reverse=True)
            margin_pos_neg = abs(p[2] - p[0])
            source = source_tag
            if top_val < CONF_THRESHOLD:
                label = "NEU"
                source = "low_conf→NEU"
            elif label in {"POS", "NEG"} and margin_pos_neg < MARGIN_THRESHOLD:
                label = "NEU"
                source = "low_margin→NEU"
            results[abs_i] = (label, top_val, source, p)
        return results

    return predict_batch


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def main():
    src = DATA_DIR / "comments_raw.csv"
    if not src.exists():
        raise SystemExit(f"Không tìm thấy {src}. Chạy step2 trước.")

    df = pd.read_csv(src)
    n = len(df)
    print(f"[*] Tiền xử lý {n} comment (use_diacritic_restore={USE_DIACRITIC_RESTORE})...")

    normalized = [normalize(t, use_diacritic_restore=USE_DIACRITIC_RESTORE)
                  for t in tqdm(df["text"].fillna(""), desc="Normalize")]
    df["normalized"] = normalized

    # Lexicon shortcut trước
    labels = [None] * n
    scores = [0.0] * n
    sources = [""] * n
    p_neg = [0.0] * n
    p_neu = [0.0] * n
    p_pos = [0.0] * n

    pending_idx = []
    for i, t in enumerate(normalized):
        hit = lexicon_lookup(t)
        if hit is not None:
            lb, sc = hit
            labels[i] = lb
            scores[i] = sc
            sources[i] = "lexicon"
            p_pos[i] = 1.0 if lb == "POS" else 0.0
            p_neg[i] = 1.0 if lb == "NEG" else 0.0
            p_neu[i] = 1.0 if lb == "NEU" else 0.0
        else:
            pending_idx.append(i)
    print(f"[*] Lexicon shortcut bắt được {n - len(pending_idx)}/{n} comment.")

    # Tokenize cho phần còn lại + batch inference
    predict_batch = build_predictor()
    pending_texts = [tokenize_for_phobert(normalized[i]) for i in pending_idx]

    for batch_start in tqdm(range(0, len(pending_idx), BATCH_SIZE), desc="Sentiment"):
        batch_abs = pending_idx[batch_start:batch_start + BATCH_SIZE]
        batch_texts = pending_texts[batch_start:batch_start + BATCH_SIZE]
        out = predict_batch(batch_texts)
        for abs_i, (lb, sc, src_tag, probs) in zip(batch_abs, out):
            labels[abs_i] = lb
            scores[abs_i] = sc
            sources[abs_i] = src_tag
            p_neg[abs_i], p_neu[abs_i], p_pos[abs_i] = probs

    df["label"] = labels
    df["score"] = scores
    df["source"] = sources
    df["score_neg"] = p_neg
    df["score_neu"] = p_neu
    df["score_pos"] = p_pos
    df.to_csv(DATA_DIR / "comments_labeled.csv",
              index=False, encoding="utf-8-sig")

    report = df.groupby(["videoId", "label"]).size().unstack(fill_value=0)
    for col in ["POS", "NEU", "NEG"]:
        if col not in report.columns:
            report[col] = 0
    report["total"] = report[["POS", "NEU", "NEG"]].sum(axis=1)
    for col in ["POS", "NEU", "NEG"]:
        report[f"{col}_pct"] = (report[col] / report["total"] * 100).round(2)
    report.to_csv(DATA_DIR / "sentiment_report.csv", encoding="utf-8-sig")

    print("\n=== Báo cáo sentiment (V2) ===")
    print(report.to_string())
    src_counts = pd.Series(sources).value_counts()
    print("\n=== Phân phối nguồn nhãn ===")
    print(src_counts.to_string())


if __name__ == "__main__":
    main()
