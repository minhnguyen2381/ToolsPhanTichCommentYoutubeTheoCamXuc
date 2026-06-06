"""BƯỚC 11: Nén output/data + output/report thành file zip.

Output: output_YYYYMMDD_HHMMSS.zip tại repo root (bên trong có data/ và report/).
"""

import io
import sys

from paths import zip_output

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def main():
    zip_path = zip_output()
    print(f"[OK] Đã nén output → {zip_path}")


if __name__ == "__main__":
    main()
