"""Wrapper thay thế YouTube Data API v3 bằng yt-dlp + youtube-comment-downloader.

Không cần API key. Dùng cho các thao tác read-only:
- search_videos(query, max_results)
- get_video_stats(video_ids)
- list_playlist_videos(playlist_id)
- iter_comments(video_id, max_comments)
"""
import re
import time
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR


import os

def _clean_cookie_file():
    """Tự động dọn dẹp ký tự BOM và định dạng CRLF để tránh lỗi Netscape format cho yt-dlp."""
    cookie_path = os.path.join(os.path.dirname(__file__), "cookies.txt")
    if not os.path.exists(cookie_path):
        return
    try:
        with open(cookie_path, 'rb') as f:
            data = f.read()
            
        modified = False
        # Xóa BOM tàng hình của Windows
        if data.startswith(b'\xef\xbb\xbf'):
            data = data[3:]
            modified = True
            
        # Chuẩn hóa xuống dòng từ Windows (CRLF) sang Linux (LF)
        if b'\r\n' in data:
            data = data.replace(b'\r\n', b'\n')
            modified = True
            
        # Chỉ ghi đè lại nếu có dính "sạn"
        if modified:
            with open(cookie_path, 'wb') as f:
                f.write(data)
    except Exception as e:
        print(f"[!] Warning: Lỗi khi dọn dẹp file cookie: {e}")

# Tự động chạy quét dọn rác trước khi khởi tạo yt-dlp
_clean_cookie_file()

_BASE_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "noprogress": True,
    "extractor_args": {"youtube": {"lang": ["vi", "en"]}},
    "cookiefile": os.path.join(os.path.dirname(__file__), "cookies.txt"),  # Đọc cookie từ src/cookies.txt
    "ignore_no_formats_error": True,  # Bỏ qua lỗi format vì mình chỉ cần lấy thông tin metadata (view, like)
}


def safe_call(fn, *args, retries=3, backoff=1.0, **kwargs):
    """Retry với exponential backoff cho lỗi mạng tạm thời."""
    last = None
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except DownloadError as e:
            last = e
            msg = str(e).lower()
            if any(k in msg for k in ("http error 429", "http error 5", "timed out", "temporarily")):
                time.sleep(backoff * (2 ** attempt))
                continue
            raise
        except Exception as e:
            last = e
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise
    if last:
        raise last


def _ydl(opts=None):
    cfg = dict(_BASE_OPTS)
    if opts:
        cfg.update(opts)
    return YoutubeDL(cfg)


def _iso_date(upload_date):
    if not upload_date or len(upload_date) != 8:
        return ""
    return f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}"


def search_videos(query, max_results=50):
    """Tìm kiếm video theo keyword, trả list videoId (order theo độ liên quan)."""
    url = f"ytsearch{max_results}:{query}"
    opts = {"extract_flat": True, "default_search": "ytsearch"}
    with _ydl(opts) as ydl:
        info = safe_call(ydl.extract_info, url, download=False)
    entries = info.get("entries") or []
    ids = []
    for e in entries:
        if not e:
            continue
        vid = e.get("id")
        if vid:
            ids.append(vid)
    return ids


def get_video_stats(video_ids, sleep=0.2):
    """Lấy metadata + thống kê cho từng video. Trả list[dict]."""
    rows = []
    with _ydl() as ydl:
        for i, vid in enumerate(video_ids):
            try:
                info = safe_call(
                    ydl.extract_info,
                    f"https://www.youtube.com/watch?v={vid}",
                    download=False,
                )
            except Exception as e:
                print(f"  [!] Bỏ qua {vid}: {str(e)[:100]}")
                continue
            rows.append({
                "videoId": info.get("id", vid),
                "title": info.get("title", ""),
                "channel": info.get("channel") or info.get("uploader", ""),
                "publishedAt": _iso_date(info.get("upload_date", "")),
                "views": int(info.get("view_count") or 0),
                "likes": int(info.get("like_count") or 0),
                "comments": int(info.get("comment_count") or 0),
            })
            if sleep:
                time.sleep(sleep)
    return rows


def list_playlist_videos(playlist_id):
    """Liệt kê videoId trong playlist (không fetch metadata chi tiết)."""
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    opts = {"extract_flat": True}
    with _ydl(opts) as ydl:
        info = safe_call(ydl.extract_info, url, download=False)
    entries = info.get("entries") or []
    return [e["id"] for e in entries if e and e.get("id")]


_LIKES_RE = re.compile(r"^\s*([\d.,]+)\s*([KkMmBb]?)\s*$")


def _parse_likes(val):
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).strip()
    if not s:
        return 0
    m = _LIKES_RE.match(s)
    if not m:
        try:
            return int(s.replace(",", "").replace(".", ""))
        except ValueError:
            return 0
    num = float(m.group(1).replace(",", ""))
    suffix = m.group(2).lower()
    mult = {"": 1, "k": 1_000, "m": 1_000_000, "b": 1_000_000_000}[suffix]
    return int(num * mult)


def iter_comments(video_id, max_comments=2000):
    """Yield top-level comments của video. Bắt lỗi comments disabled → yield rỗng."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    downloader = YoutubeCommentDownloader()
    try:
        stream = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)
    except Exception as e:
        print(f"  [!] Không lấy được comments {video_id}: {str(e)[:100]}")
        return
    count = 0
    for c in stream:
        if c.get("reply"):
            continue
        yield {
            "videoId": video_id,
            "commentId": c.get("cid", ""),
            "author": c.get("author", ""),
            "text": c.get("text", ""),
            "likes": _parse_likes(c.get("votes")),
            "publishedAt": c.get("time_parsed") or c.get("time", ""),
        }
        count += 1
        if count >= max_comments:
            break
