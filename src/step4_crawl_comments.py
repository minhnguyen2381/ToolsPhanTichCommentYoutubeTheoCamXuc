"""BƯỚC 4 (V5): Cào comment từ playlist.
Lấy danh sách video từ playlist mục tiêu.
Cào comment cho mỗi video và lưu lại thành data/v5_comments_raw.csv.
"""

import os
import time
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

from youtube_client import list_playlist_videos, iter_comments

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def main():
    load_dotenv()
    # Playlist ID mặc định như CLAUDE.md nếu không có trong .env
    playlist_id = os.getenv("PLAYLIST_ID", "PLlvlc45o3QQcwtas1taX7VlLyZ6Advf_3")
    
    print(f"\n[*] Bắt đầu crawl comment cho playlist: {playlist_id}")
    try:
        video_ids = list_playlist_videos(playlist_id)
    except Exception as e:
        print(f"[!] Lỗi khi lấy playlist: {e}")
        return
        
    print(f"[*] Tìm thấy {len(video_ids)} videos trong playlist.")
    
    if not video_ids:
        print("[!] Không có video để cào comment.")
        return
        
    all_comments = []
    
    for i, vid in enumerate(video_ids):
        print(f"  → Đang cào video {i+1}/{len(video_ids)}: {vid}")
        comments = list(iter_comments(vid, max_comments=2000))
        all_comments.extend(comments)
        print(f"    Đã cào {len(comments)} comments.")
        time.sleep(1)
        
    if not all_comments:
        print("[!] Không thu thập được comment nào.")
        return
        
    df = pd.DataFrame(all_comments)
    out_file = DATA_DIR / "v5_comments_raw.csv"
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    
    print(f"\n[OK] Đã cào tổng cộng {len(df)} comments và lưu vào {out_file.name}")

if __name__ == "__main__":
    main()
