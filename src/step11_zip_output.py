"""BƯỚC 11: Nén output/data + output/report thành file zip.

Output: zip_exporter/output_YYYYMMDD_HHMMSS.zip (bên trong có data/ và report/).
Xóa zip cũ hơn ZIP_RETENTION_DAYS (1–30 ngày) trong zip_exporter/.
"""

import io
import os
import sys
import time

from dotenv import load_dotenv

from paths import ZIP_EXPORTER_DIR, zip_output

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Số ngày giữ zip trong zip_exporter/ (1–30). Có thể ghi đè bằng ZIP_RETENTION_DAYS trong .env
ZIP_RETENTION_DAYS = 7
MIN_ZIP_RETENTION_DAYS = 1
MAX_ZIP_RETENTION_DAYS = 30


def get_retention_days() -> int:
    load_dotenv()
    raw = os.getenv("ZIP_RETENTION_DAYS", str(ZIP_RETENTION_DAYS))
    try:
        days = int(raw)
    except ValueError:
        print(
            f"[WARN] ZIP_RETENTION_DAYS='{raw}' không hợp lệ, "
            f"dùng mặc định {ZIP_RETENTION_DAYS} ngày."
        )
        return ZIP_RETENTION_DAYS
    if not MIN_ZIP_RETENTION_DAYS <= days <= MAX_ZIP_RETENTION_DAYS:
        print(
            f"[WARN] ZIP_RETENTION_DAYS={days} ngoài khoảng "
            f"{MIN_ZIP_RETENTION_DAYS}-{MAX_ZIP_RETENTION_DAYS}, "
            f"dùng mặc định {ZIP_RETENTION_DAYS} ngày."
        )
        return ZIP_RETENTION_DAYS
    return days


def cleanup_old_zips(retention_days: int) -> int:
    """Xóa *.zip trong zip_exporter/ cũ hơn retention_days. Trả về số file đã xóa."""
    if not ZIP_EXPORTER_DIR.exists():
        return 0

    cutoff = time.time() - retention_days * 86400
    removed = 0
    for zip_path in sorted(ZIP_EXPORTER_DIR.glob("*.zip")):
        if zip_path.stat().st_mtime < cutoff:
            zip_path.unlink()
            removed += 1
            print(f"[*] Đã xóa zip cũ: {zip_path.name}")
    return removed


def main():
    retention_days = get_retention_days()
    zip_path = zip_output()
    removed = cleanup_old_zips(retention_days)
    print(f"[OK] Đã nén output → {zip_path}")
    if removed:
        print(f"[OK] Đã dọn {removed} zip cũ hơn {retention_days} ngày.")
    else:
        print(f"[*] Không có zip cũ hơn {retention_days} ngày cần xóa.")


if __name__ == "__main__":
    main()
