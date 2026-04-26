"""BƯỚC 3 (V3): Phân loại sentiment — domain-aware + post-processing heuristics.

Cải tiến so với V2 (xem `solutions/v3_sentiment/GIAI_PHAP_V3.md`):
- CONF_THRESHOLD_NEG riêng biệt (0.75) — NEG cần tự tin hơn.
- Lexicon shortcut mở rộng ≤ 8 token + từ lóng khen.
- Post-processing: question detection, history domain, listing detection.
- Cột mới: `source` ghi rõ lý do flip (vd: `question→NEU`, `domain→NEU`).
"""
import os
import re
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import normalize, tokenize_for_phobert  # noqa: E402
from lexicon import (  # noqa: E402
    LEXICON_POS, LEXICON_NEG,
    HISTORY_DOMAIN_KEYWORDS, QUESTION_PATTERNS,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODEL_NAME = "wonrax/phobert-base-vietnamese-sentiment"
ENSEMBLE_MODEL_NAME = "5CD-AI/Vietnamese-Sentiment-visobert"

USE_DIACRITIC_RESTORE = os.getenv("USE_DIACRITIC_RESTORE", "0") == "1"
USE_ENSEMBLE = os.getenv("USE_ENSEMBLE", "0") == "1"
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.60"))
CONF_THRESHOLD_NEG = float(os.getenv("CONF_THRESHOLD_NEG", "0.75"))
DOMAIN_THRESHOLD = float(os.getenv("DOMAIN_THRESHOLD", "0.90"))
MARGIN_THRESHOLD = float(os.getenv("MARGIN_THRESHOLD", "0.15"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
MAX_LEN = int(os.getenv("MAX_LEN", "256"))
LEXICON_MAX_TOKENS = int(os.getenv("LEXICON_MAX_TOKENS", "8"))


# ---------------------------------------------------------------------------
# Lexicon shortcut (V3: mở rộng lên 8 token)
# ---------------------------------------------------------------------------
def lexicon_lookup(normalized_text: str):
    """Trả về (label, score) nếu match lexicon, ngược lại None.

    V3: tăng giới hạn từ 5 → LEXICON_MAX_TOKENS (default 8).
    """
    if not normalized_text:
        return None
    tokens = normalized_text.split()
    if len(tokens) > LEXICON_MAX_TOKENS:
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
# Post-processing heuristics (V3 MỚI)
# ---------------------------------------------------------------------------
_QUESTION_MARK_RE = re.compile(r"\?")


def _count_domain_hits(normalized_text: str) -> int:
    """Đếm số lượng HISTORY_DOMAIN_KEYWORDS xuất hiện trong text."""
    count = 0
    for kw in HISTORY_DOMAIN_KEYWORDS:
        if kw in normalized_text:
            count += 1
    return count


def _is_question(normalized_text: str) -> bool:
    """Phát hiện câu hỏi dựa trên dấu ? và pattern."""
    if _QUESTION_MARK_RE.search(normalized_text):
        return True
    for pat in QUESTION_PATTERNS:
        if pat in normalized_text:
            return True
    return False


def _is_name_listing(normalized_text: str) -> bool:
    """Phát hiện comment chỉ liệt kê tên nhân vật (ít động từ/tính từ sentiment)."""
    tokens = normalized_text.split()
    if len(tokens) < 3:
        return False
    domain_hits = _count_domain_hits(normalized_text)
    # Nếu > 50% tokens là tên nhân vật → listing
    if domain_hits >= 3 and domain_hits >= len(tokens) * 0.3:
        return True
    return False


def postprocess_label(label: str, score: float, probs: list,
                      normalized_text: str, source: str):
    """Áp dụng V3 heuristics sau khi model predict.

    Trả về (label, source) đã được điều chỉnh.
    Chỉ can thiệp khi label == "NEG".

    probs = [neg, neu, pos]
    """
    if label != "NEG":
        return label, source

    p_neg, p_neu, p_pos = probs

    # --- Rule 1: NEG confidence threshold cao hơn ---
    if p_neg < CONF_THRESHOLD_NEG:
        return "NEU", "low_conf_neg→NEU"

    # --- Rule 2: Question detection → NEU ---
    if _is_question(normalized_text):
        return "NEU", "question→NEU"

    # --- Rule 3: Name listing → NEU ---
    if _is_name_listing(normalized_text):
        return "NEU", "listing→NEU"

    # --- Rule 4: Domain history → nâng ngưỡng ---
    domain_hits = _count_domain_hits(normalized_text)
    if domain_hits >= 2 and p_neg < DOMAIN_THRESHOLD:
        return "NEU", "domain→NEU"

    # --- Rule 5: Mixed sentiment → NEU ---
    if p_pos > 0.15 and p_neg > 0.15 and p_neg < 0.85:
        return "NEU", "mixed→NEU"

    # --- Rule 6: Short neutral → NEU ---
    tokens = normalized_text.split()
    if len(tokens) <= 3 and p_neg < 0.95:
        return "NEU", "short→NEU"

    return label, source


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
            margin_pos_neg = abs(p[2] - p[0])
            source = source_tag

            # --- V2 confidence gating (áp dụng cho POS/NEU) ---
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

    # Lexicon shortcut trước (V3: mở rộng lên 8 token)
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
            # V3: post-processing heuristics
            lb, src_tag = postprocess_label(
                lb, sc, probs, normalized[abs_i], src_tag
            )
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

    print("\n=== Báo cáo sentiment (V3) ===")
    print(report.to_string())
    src_counts = pd.Series(sources).value_counts()
    print("\n=== Phân phối nguồn nhãn ===")
    print(src_counts.to_string())


if __name__ == "__main__":
    main()
