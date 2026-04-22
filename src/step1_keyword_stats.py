"""BƯỚC 1: Khảo sát độ phổ biến của từ khoá trên YouTube."""
import os
import time
from pathlib import Path
import pandas as pd
from youtube_client import get_client, safe_execute

KEYWORDS = ["Quan Vũ", "Quan Vân Trường", "Quan Công", "Quan Thánh"]
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def search_keyword(youtube, kw, max_results=50):
    res = safe_execute(youtube.search().list(
        q=kw, part="id,snippet", type="video",
        maxResults=max_results, regionCode="VN",
        relevanceLanguage="vi",
    ))
    total = res["pageInfo"]["totalResults"]
    video_ids = [item["id"]["videoId"] for item in res["items"]
                 if item["id"].get("videoId")]
    return total, video_ids


def get_video_stats(youtube, video_ids):
    if not video_ids:
        return pd.DataFrame()
    res = safe_execute(youtube.videos().list(
        part="statistics,snippet", id=",".join(video_ids),
    ))
    rows = []
    for v in res["items"]:
        s = v["statistics"]
        rows.append({
            "videoId": v["id"],
            "title": v["snippet"]["title"],
            "channel": v["snippet"]["channelTitle"],
            "publishedAt": v["snippet"]["publishedAt"],
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0)),
        })
    return pd.DataFrame(rows)


def main():
    youtube = get_client()
    summary = []
    for kw in KEYWORDS:
        print(f"[*] Tìm kiếm: {kw}")
        total, ids = search_keyword(youtube, kw)
        df = get_video_stats(youtube, ids)
        safe_name = kw.replace(" ", "_")
        df.to_csv(DATA_DIR / f"keyword_{safe_name}.csv",
                  index=False, encoding="utf-8-sig")
        summary.append({
            "keyword": kw,
            "total_results": total,
            "top50_total_views": int(df["views"].sum()) if not df.empty else 0,
            "top50_avg_views": int(df["views"].mean()) if not df.empty else 0,
            "top50_total_likes": int(df["likes"].sum()) if not df.empty else 0,
            "top50_total_comments": int(df["comments"].sum()) if not df.empty else 0,
        })
        time.sleep(0.2)

    out = pd.DataFrame(summary)
    out.to_csv(DATA_DIR / "keyword_summary.csv",
               index=False, encoding="utf-8-sig")
    print("\n=== Tóm tắt ===")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
