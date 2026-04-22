"""BƯỚC 3: Tiền xử lý + phân loại sentiment bằng PhoBERT."""
import re
from pathlib import Path
import pandas as pd
import emoji
from tqdm import tqdm
from underthesea import word_tokenize

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODEL_NAME = "wonrax/phobert-base-vietnamese-sentiment"
LABELS = ["NEG", "POS", "NEU"]


def clean_text(t: str) -> str:
    if not isinstance(t, str):
        return ""
    t = emoji.replace_emoji(t, replace=" ")
    t = re.sub(r"http\S+", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"[^\wÀ-ỹ\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    if not t:
        return ""
    return word_tokenize(t, format="text")


def build_predictor():
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    import torch.nn.functional as F

    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"[*] Chạy model trên {device}")

    @torch.no_grad()
    def predict(text: str):
        if not text:
            return "NEU", 0.0
        inputs = tok(text, return_tensors="pt",
                     truncation=True, max_length=256).to(device)
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1)[0]
        idx = int(probs.argmax().item())
        return LABELS[idx], float(probs[idx])

    return predict


def main():
    src = DATA_DIR / "comments_raw.csv"
    if not src.exists():
        raise SystemExit(f"Không tìm thấy {src}. Chạy step2 trước.")

    df = pd.read_csv(src)
    print(f"[*] Tiền xử lý {len(df)} comment...")
    df["clean"] = [clean_text(t) for t in tqdm(df["text"].fillna(""))]

    predict = build_predictor()
    labels, scores = [], []
    for text in tqdm(df["clean"], desc="Sentiment"):
        lb, sc = predict(text)
        labels.append(lb)
        scores.append(sc)
    df["label"] = labels
    df["score"] = scores
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

    print("\n=== Báo cáo sentiment ===")
    print(report.to_string())


if __name__ == "__main__":
    main()
