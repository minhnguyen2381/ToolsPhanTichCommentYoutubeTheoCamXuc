"""BƯỚC 2.1 + 2.2: Lấy danh sách video trong playlist và crawl comment."""
import os
import time
from pathlib import Path
import pandas as pd
from googleapiclient.errors import HttpError
from youtube_client import get_client, safe_execute

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

PLAYLIST_ID = os.getenv("PLAYLIST_ID", "PLlvlc45o3QQcwtas1taX7VlLyZ6Advf_3")


def get_playlist_videos(youtube, playlist_id):
    ids, token = [], None
    while True:
        res = safe_execute(youtube.playlistItems().list(
            part="contentDetails", playlistId=playlist_id,
            maxResults=50, pageToken=token,
        ))
        ids.extend(i["contentDetails"]["videoId"] for i in res["items"])
        token = res.get("nextPageToken")
        if not token:
            break
    return ids


def get_comments(youtube, video_id, max_pages=20):
    comments, token, pages = [], None, 0
    while pages < max_pages:
        try:
            res = safe_execute(youtube.commentThreads().list(
                part="snippet,replies", videoId=video_id,
                maxResults=100, pageToken=token, textFormat="plainText",
            ))
        except HttpError as e:
            reason = str(e)
            print(f"  [!] Bỏ qua {video_id}: {reason[:100]}")
            break
        for item in res["items"]:
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "videoId": video_id,
                "commentId": item["snippet"]["topLevelComment"]["id"],
                "author": top["authorDisplayName"],
                "text": top["textDisplay"],
                "likes": top["likeCount"],
                "publishedAt": top["publishedAt"],
            })
        token = res.get("nextPageToken")
        pages += 1
        if not token:
            break
        time.sleep(0.1)
    return comments


def main():
    youtube = get_client()
    print(f"[*] Lấy danh sách video trong playlist {PLAYLIST_ID}")
    video_ids = get_playlist_videos(youtube, PLAYLIST_ID)
    print(f"  → {len(video_ids)} video")

    pd.DataFrame({"videoId": video_ids}).to_csv(
        DATA_DIR / "playlist_videos.csv", index=False, encoding="utf-8-sig"
    )

    all_comments = []
    for idx, vid in enumerate(video_ids, 1):
        print(f"[{idx}/{len(video_ids)}] Crawl {vid}")
        cmts = get_comments(youtube, vid)
        print(f"  → {len(cmts)} comments")
        all_comments.extend(cmts)
        time.sleep(0.1)

    df = pd.DataFrame(all_comments)
    df.to_csv(DATA_DIR / "comments_raw.csv",
              index=False, encoding="utf-8-sig")
    print(f"\n[OK] Tổng {len(df)} comment, lưu tại data/comments_raw.csv")


if __name__ == "__main__":
    main()
