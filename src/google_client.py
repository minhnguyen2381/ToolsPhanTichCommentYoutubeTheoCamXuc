"""Wrapper googlesearch-python — tìm kiếm Google với retry và rate-limit."""

import time
from dataclasses import dataclass
from typing import Iterator, Optional

from googlesearch import search


@dataclass
class GoogleSearchResult:
    title: str
    url: str
    description: str


def iter_google_search(
    query: str,
    num_results: int = 100,
    lang: str = "vi",
    region: str = "vn",
    sleep_interval: float = 2.0,
    retries: int = 3,
    backoff: float = 2.0,
) -> Iterator[GoogleSearchResult]:
    """Yield kết quả Google Search. Retry khi lỗi mạng tạm thời."""
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            count = 0
            for item in search(
                query,
                num_results=num_results,
                lang=lang,
                region=region,
                advanced=True,
                sleep_interval=sleep_interval,
                unique=True,
            ):
                title = getattr(item, "title", "") or ""
                url = getattr(item, "url", "") or ""
                description = getattr(item, "description", "") or ""
                if not url:
                    continue
                yield GoogleSearchResult(title=title, url=url, description=description)
                count += 1
                if count >= num_results:
                    return
            return
        except Exception as e:
            last_err = e
            msg = str(e).lower()
            if attempt < retries - 1 and any(
                k in msg for k in ("429", "timeout", "timed out", "connection", "blocked")
            ):
                wait = backoff * (2 ** attempt)
                print(f"  [!] Google search lỗi, thử lại sau {wait:.0f}s: {str(e)[:80]}")
                time.sleep(wait)
                continue
            raise
    if last_err:
        raise last_err
