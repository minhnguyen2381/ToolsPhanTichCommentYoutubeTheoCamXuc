"""Wrapper cho YouTube Data API v3."""
import os
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()


def get_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise RuntimeError(
            "Thiếu YOUTUBE_API_KEY trong file .env. "
            "Xem hướng dẫn ở README.md mục Cài đặt."
        )
    return build("youtube", "v3", developerKey=api_key)


def safe_execute(request, retries=3, backoff=1.0):
    for attempt in range(retries):
        try:
            return request.execute()
        except HttpError as e:
            if e.resp.status in (403, 429, 500, 503) and attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise
