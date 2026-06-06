"""BƯỚC 5 (V6): Thống kê kênh YouTube đăng ≥2 video liên quan Quan Vũ.

Input:  output/data/v5_3000_videos_filtered.csv (fallback cleaned / raw)
Output: output/data/v6_channel_stats.csv
"""

import io
import re
import sys

import pandas as pd
from tqdm import tqdm

from paths import DATA_DIR, ensure_data_dir
from youtube_client import get_channel_info, get_video_channel_metadata

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

V6_KEYWORDS = [
    "quan công",
    "quan vũ",
    "quan thánh",
    "quan thánh đế quân",
    "quan vân trường",
]

MIN_VIDEOS_PER_CHANNEL = 2

OFFICIAL_CHANNEL_PATTERNS = [
    r"\bofficial\b",
    r"\bđền\b",
    r"\bchùa\b",
    r"bảo tàng",
    r"\bmuseum\b",
    r"\bphim\b",
    r"\btv\b",
    r"television",
    r"văn hóa",
    r"\bubnd\b",
    r"sở vh",
    r"thánh đường",
    r"giáo xứ",
    r"nhà nước",
    r"truyền hình",
    r"documentary",
    r"history channel",
]
_OFFICIAL_RE = re.compile("|".join(OFFICIAL_CHANNEL_PATTERNS), re.IGNORECASE)


def _normalize(s):
    if not isinstance(s, str):
        return ""
    return s.lower().strip()


def title_matches_v6(title):
    t = _normalize(title)
    return any(kw in t for kw in V6_KEYWORDS)


def classify_account_type(channel_name, is_verified=False):
    if is_verified:
        return "chinh_thong"
    if channel_name and _OFFICIAL_RE.search(channel_name):
        return "chinh_thong"
    return "ca_nhan"


def _resolve_input_file():
    for name in (
        "v5_3000_videos_filtered.csv",
        "v5_3000_videos_cleaned.csv",
        "v5_3000_videos_raw.csv",
    ):
        path = DATA_DIR / name
        if path.exists():
            return path
    return None


def _channel_group_key(row):
    cid = row.get("channel_id")
    if isinstance(cid, str) and cid.strip():
        return f"id:{cid.strip()}"
    ch = row.get("channel")
    if isinstance(ch, str) and ch.strip():
        return f"name:{ch.strip().lower()}"
    return None


def main():
    ensure_data_dir()
    in_file = _resolve_input_file()
    if in_file is None:
        print("[!] Không tìm thấy file video. Chạy step1→step3 trước.")
        return

    df = pd.read_csv(in_file)
    print(f"[*] Đọc {len(df)} video từ {in_file.name}")

    df = df.dropna(subset=["title"]).copy()
    df_v6 = df[df["title"].apply(title_matches_v6)].copy()
    if df_v6.empty:
        print("[!] Không có video nào khớp keyword V6.")
        return

    print(f"[*] {len(df_v6)} video khớp keyword V6")

    total_videos = len(df_v6)
    df_v6["_group"] = df_v6.apply(_channel_group_key, axis=1)
    df_v6 = df_v6.dropna(subset=["_group"])

    grouped = df_v6.groupby("_group", sort=False)
    channel_rows = []
    for group_key, grp in grouped:
        if len(grp) < MIN_VIDEOS_PER_CHANNEL:
            continue
        sample = grp.iloc[0]
        channel_rows.append({
            "group_key": group_key,
            "ten_tai_khoan": sample.get("channel", ""),
            "so_luong_video": len(grp),
            "channel_id": sample.get("channel_id", "") if "channel_id" in grp.columns else "",
            "channel_url": sample.get("channel_url", "") if "channel_url" in grp.columns else "",
            "channel_is_verified": bool(sample.get("channel_is_verified", False))
            if "channel_is_verified" in grp.columns
            else False,
            "sample_video_id": sample.get("videoId", ""),
        })

    if not channel_rows:
        print(f"[!] Không có kênh nào đăng ≥{MIN_VIDEOS_PER_CHANNEL} video.")
        return

    print(f"[*] {len(channel_rows)} kênh có ≥{MIN_VIDEOS_PER_CHANNEL} video — đang lấy metadata...")

    results = []
    for row in tqdm(channel_rows, desc="Kênh"):
        meta = None
        if row.get("channel_url"):
            meta = get_channel_info(row["channel_url"])
        if meta is None and row.get("sample_video_id"):
            meta = get_video_channel_metadata(row["sample_video_id"])

        channel_name = row["ten_tai_khoan"]
        is_verified = row["channel_is_verified"]
        channel_id = row.get("channel_id", "")
        channel_url = row.get("channel_url", "")

        if meta:
            channel_name = meta.get("channel") or channel_name
            is_verified = meta.get("channel_is_verified", is_verified)
            channel_id = meta.get("channel_id") or channel_id
            channel_url = meta.get("channel_url") or channel_url

        so_luong = row["so_luong_video"]
        ty_le = round(so_luong / total_videos * 100, 2)

        results.append({
            "ten_tai_khoan": channel_name,
            "loai_tai_khoan": classify_account_type(channel_name, is_verified),
            "so_luong_video": so_luong,
            "ty_le_pct": ty_le,
            "channel_id": channel_id,
            "channel_url": channel_url,
        })

    out_df = pd.DataFrame(results).sort_values("so_luong_video", ascending=False)
    out_file = DATA_DIR / "v6_channel_stats.csv"
    out_df.to_csv(out_file, index=False, encoding="utf-8-sig")

    print(f"\n=== THỐNG KÊ KÊNH (≥{MIN_VIDEOS_PER_CHANNEL} video) ===")
    print(out_df[["ten_tai_khoan", "loai_tai_khoan", "so_luong_video", "ty_le_pct"]].to_string(index=False))
    print(f"\n[OK] Đã lưu {len(out_df)} kênh vào {out_file.name}")


if __name__ == "__main__":
    main()
