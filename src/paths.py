"""Đường dẫn output dùng chung cho toàn bộ pipeline."""
from __future__ import annotations

import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
DATA_DIR = OUTPUT_DIR / "data"
REPORT_DIR = OUTPUT_DIR / "report"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ensure_report_dir() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def zip_output() -> Path:
    """Nén output/data + output/report thành output_YYYYMMDD_HHMMSS.zip tại repo root."""
    if not OUTPUT_DIR.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục {OUTPUT_DIR}. Chạy pipeline trước.")

    files = [p for p in OUTPUT_DIR.rglob("*") if p.is_file()]
    if not files:
        raise FileNotFoundError(f"Thư mục {OUTPUT_DIR} trống, không có gì để nén.")

    zip_name = f"output_{datetime.now():%Y%m%d_%H%M%S}.zip"
    zip_path = ROOT / zip_name

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            arcname = file_path.relative_to(OUTPUT_DIR).as_posix()
            zf.write(file_path, arcname=arcname)

    total_bytes = sum(f.stat().st_size for f in files)
    size_mb = total_bytes / (1024 * 1024)
    print(f"[*] Đã nén {len(files)} file ({size_mb:.2f} MB) → {zip_path.name}")
    return zip_path
