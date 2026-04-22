"""BƯỚC 2.1 + 2.2: Lấy danh sách video trong playlist và crawl comment (yt-dlp + ycd)."""
import os
import time
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from youtube_client import list_playlist_videos, iter_comments

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

PLAYLIST_ID = os.getenv("PLAYLIST_ID", "PLlvlc45o3QQcwtas1taX7VlLyZ6Advf_3")
MAX_COMMENTS_PER_VIDEO = 2000


def main():
    print(f"[*] Lấy danh sách video trong playlist {PLAYLIST_ID}")
    video_ids = list_playlist_videos(PLAYLIST_ID)
    print(f"  → {len(video_ids)} video")

    pd.DataFrame({"videoId": video_ids}).to_csv(
        DATA_DIR / "playlist_videos.csv", index=False, encoding="utf-8-sig"
    )

    all_comments = []
    for idx, vid in enumerate(video_ids, 1):
        print(f"[{idx}/{len(video_ids)}] Crawl {vid}")
        cmts = list(iter_comments(vid, max_comments=MAX_COMMENTS_PER_VIDEO))
        print(f"  → {len(cmts)} comments")
        all_comments.extend(cmts)
        time.sleep(0.1)

    df = pd.DataFrame(all_comments)
    df.to_csv(DATA_DIR / "comments_raw.csv",
              index=False, encoding="utf-8-sig")
    print(f"\n[OK] Tổng {len(df)} comment, lưu tại data/comments_raw.csv")


if __name__ == "__main__":
    main()
