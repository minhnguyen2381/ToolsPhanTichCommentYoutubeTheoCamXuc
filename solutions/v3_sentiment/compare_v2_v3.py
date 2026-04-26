"""So sánh kết quả V2 (hiện tại) với V3 heuristics trên comments_labeled.csv.

Script này KHÔNG chạy model lại — chỉ áp dụng V3 post-processing heuristics
lên kết quả V2 đã có để xem bao nhiêu comment bị flip.
"""
import sys
import re
sys.path.insert(0, "src")
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
from lexicon import HISTORY_DOMAIN_KEYWORDS, QUESTION_PATTERNS

CONF_THRESHOLD_NEG = 0.75
DOMAIN_THRESHOLD = 0.90

_QUESTION_MARK_RE = re.compile(r"\?")

def count_domain_hits(text):
    count = 0
    for kw in HISTORY_DOMAIN_KEYWORDS:
        if kw in text:
            count += 1
    return count

def is_question(text):
    if _QUESTION_MARK_RE.search(text):
        return True
    for pat in QUESTION_PATTERNS:
        if pat in text:
            return True
    return False

def is_name_listing(text):
    tokens = text.split()
    if len(tokens) < 3:
        return False
    hits = count_domain_hits(text)
    if hits >= 3 and hits >= len(tokens) * 0.3:
        return True
    return False

def apply_v3_postprocess(row):
    label = row["label"]
    norm = str(row.get("normalized", ""))
    p_neg = row["score_neg"]
    p_neu = row["score_neu"]
    p_pos = row["score_pos"]
    source = row["source"]

    if label != "NEG":
        return label, source

    # Rule 1: NEG confidence threshold
    if p_neg < CONF_THRESHOLD_NEG:
        return "NEU", "low_conf_neg→NEU"

    # Rule 2: Question
    if is_question(norm):
        return "NEU", "question→NEU"

    # Rule 3: Listing
    if is_name_listing(norm):
        return "NEU", "listing→NEU"

    # Rule 4: Domain history
    hits = count_domain_hits(norm)
    if hits >= 2 and p_neg < DOMAIN_THRESHOLD:
        return "NEU", "domain→NEU"

    # Rule 5: Mixed sentiment
    if p_pos > 0.15 and p_neg > 0.15 and p_neg < 0.85:
        return "NEU", "mixed→NEU"

    # Rule 6: Short neutral
    tokens = norm.split()
    if len(tokens) <= 3 and p_neg < 0.95:
        return "NEU", "short→NEU"

    return label, source


def main():
    df = pd.read_csv("data/comments_labeled.csv")

    print("=" * 70)
    print("SO SÁNH V2 vs V3 HEURISTICS")
    print("=" * 70)

    print(f"\n--- V2 (hiện tại) ---")
    print(df["label"].value_counts().to_string())

    # Apply V3
    flipped = []
    new_labels = []
    new_sources = []
    for _, row in df.iterrows():
        new_label, new_source = apply_v3_postprocess(row)
        new_labels.append(new_label)
        new_sources.append(new_source)
        if new_label != row["label"]:
            flipped.append({
                "text": str(row.get("text", ""))[:100],
                "v2_label": row["label"],
                "v3_label": new_label,
                "v3_source": new_source,
                "score_neg": row["score_neg"],
            })

    df["v3_label"] = new_labels
    df["v3_source"] = new_sources

    print(f"\n--- V3 (sau post-processing) ---")
    print(df["v3_label"].value_counts().to_string())

    print(f"\n--- Tổng số comment bị flip: {len(flipped)} ---")

    # Group by reason
    reasons = {}
    for f in flipped:
        r = f["v3_source"]
        reasons[r] = reasons.get(r, 0) + 1

    print(f"\n--- Phân bố lý do flip ---")
    for r, c in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  {r}: {c}")

    print(f"\n--- Chi tiết các comment bị flip (top 40) ---")
    for i, f in enumerate(flipped[:40]):
        print(f"[{i+1}] {f['v2_label']}→{f['v3_label']} ({f['v3_source']}) score_neg={f['score_neg']:.3f}")
        print(f"     {f['text']}")
        print()

    # Summary
    v2_neg = len(df[df["label"] == "NEG"])
    v3_neg = len(df[df["v3_label"] == "NEG"])
    print(f"\n{'='*70}")
    print(f"V2 NEG: {v2_neg} ({v2_neg/len(df)*100:.1f}%)")
    print(f"V3 NEG: {v3_neg} ({v3_neg/len(df)*100:.1f}%)")
    print(f"Giảm:   {v2_neg - v3_neg} comment ({(v2_neg-v3_neg)/v2_neg*100:.1f}% NEG bị loại)")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
