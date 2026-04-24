"""Random sample 200 comment để gán nhãn tay → đo accuracy/F1 của V2.

Cách dùng:
  1. python src/eval_sample.py            # tạo data/eval_sample.csv (cột `gold` rỗng)
  2. Mở CSV, điền cột `gold` với POS/NEU/NEG cho từng dòng.
  3. python src/eval_sample.py --score    # đọc lại file đã gán → in accuracy + confusion matrix.
"""
import argparse
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SAMPLE_PATH = DATA_DIR / "eval_sample.csv"
SAMPLE_SIZE = 200
SEED = 42
LABELS = ["POS", "NEU", "NEG"]


def make_sample():
    src = DATA_DIR / "comments_labeled.csv"
    if not src.exists():
        raise SystemExit(f"Không tìm thấy {src}. Chạy step3 trước.")
    df = pd.read_csv(src)
    n = min(SAMPLE_SIZE, len(df))
    sample = df.sample(n=n, random_state=SEED).copy()
    keep_cols = [c for c in ["videoId", "text", "label", "score", "source"]
                 if c in sample.columns]
    sample = sample[keep_cols]
    sample["gold"] = ""  # cột để gán tay
    sample.to_csv(SAMPLE_PATH, index=False, encoding="utf-8-sig")
    print(f"[+] Đã tạo {SAMPLE_PATH} ({n} dòng). Hãy gán cột `gold` với POS/NEU/NEG.")


def score_sample():
    if not SAMPLE_PATH.exists():
        raise SystemExit(f"Không tìm thấy {SAMPLE_PATH}. Chạy không có --score trước.")
    df = pd.read_csv(SAMPLE_PATH)
    df["gold"] = df["gold"].astype(str).str.strip().str.upper()
    df = df[df["gold"].isin(LABELS)].copy()
    if df.empty:
        raise SystemExit("Chưa có dòng nào được gán nhãn `gold`.")
    df["label"] = df["label"].astype(str).str.upper()
    n = len(df)
    correct = (df["label"] == df["gold"]).sum()
    acc = correct / n
    print(f"\nTotal annotated: {n}")
    print(f"Accuracy: {acc:.3f} ({correct}/{n})\n")

    # Confusion matrix
    cm = pd.crosstab(df["gold"], df["label"], rownames=["gold"],
                     colnames=["pred"], dropna=False)
    for lb in LABELS:
        if lb not in cm.columns:
            cm[lb] = 0
        if lb not in cm.index:
            cm.loc[lb] = 0
    cm = cm.loc[LABELS, LABELS]
    print("Confusion matrix (rows=gold, cols=pred):")
    print(cm.to_string())

    # Macro precision/recall/F1
    print("\nPer-class metrics:")
    f1s = []
    for lb in LABELS:
        tp = int(cm.loc[lb, lb])
        fp = int(cm[lb].sum() - tp)
        fn = int(cm.loc[lb].sum() - tp)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        f1s.append(f1)
        print(f"  {lb}: P={prec:.3f}  R={rec:.3f}  F1={f1:.3f}")
    print(f"\nMacro-F1: {sum(f1s) / len(f1s):.3f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", action="store_true",
                        help="Đọc eval_sample.csv đã gán → in metrics.")
    args = parser.parse_args()
    if args.score:
        score_sample()
    else:
        make_sample()


if __name__ == "__main__":
    main()
