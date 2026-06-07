"""Chẩn đoán phân loại Google content types — in phân bố và mẫu Khác."""

import io
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from google_content_classifier import classify_content, is_valid_result
from paths import DATA_DIR

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def main():
    raw_file = DATA_DIR / "v6_google_results_raw.csv"
    ct_file = DATA_DIR / "v6_google_content_types.csv"

    if ct_file.exists():
        df = pd.read_csv(ct_file, encoding="utf-8-sig")
        print(f"[*] Đọc {ct_file.name} ({len(df)} hàng)")
    elif raw_file.exists():
        df = pd.read_csv(raw_file, encoding="utf-8-sig")
        df = df[df.apply(
            lambda r: is_valid_result(r.get("url", ""), r.get("title", ""), r.get("description", "")),
            axis=1,
        )]
        df["content_type"] = df.apply(
            lambda r: classify_content(
                r.get("url", ""), r.get("title", ""), r.get("description", ""),
                r.get("domain", ""), r.get("keyword", ""),
            ),
            axis=1,
        )
        print(f"[*] Phân loại từ {raw_file.name} ({len(df)} hàng hợp lệ)")
    else:
        print("[!] Không tìm thấy dữ liệu Google. Chạy step6 trước.")
        sys.exit(1)

    total = len(df) or 1
    counts = df["content_type"].value_counts()
    khac_n = counts.get("Khác", 0)
    khac_pct = round(khac_n / total * 100, 1)

    print(f"\n=== PHÂN BỐ ({total} kết quả) ===")
    for ct, n in counts.items():
        print(f"  {ct:16s} {n:4d}  ({round(n / total * 100, 1)}%)")

    status = "OK" if khac_pct < 5 else "CẢNH BÁO"
    print(f"\n[{status}] Khác: {khac_n}/{total} = {khac_pct}% (mục tiêu < 5%)")

    khac = df[df["content_type"] == "Khác"]
    if not khac.empty:
        print(f"\n=== TOP DOMAIN TRONG KHÁC ({len(khac)} hàng) ===")
        for dom, n in khac["domain"].value_counts().head(20).items():
            print(f"  {n:3d}  {dom}")

        print("\n=== MẪU URL KHÁC (tối đa 15) ===")
        for _, r in khac.head(15).iterrows():
            title = str(r.get("title", ""))[:70]
            print(f"  [{r.get('domain', '')}] {title}")


if __name__ == "__main__":
    main()
