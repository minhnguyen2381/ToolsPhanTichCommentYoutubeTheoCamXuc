"""Wrapper tìm kiếm web qua ddgs (Bing / Brave / DuckDuckGo).

googlesearch-python scrape trực tiếp Google thường bị chặn (0 kết quả).
ddgs ổn định hơn cho pipeline khảo sát keyword.
"""

import time
from dataclasses import dataclass
from typing import Iterator, List, Optional

try:
    from ddgs import DDGS
except ImportError as e:
    raise ImportError(
        "Thiếu package ddgs. Chạy: pip install ddgs"
    ) from e

BACKEND_CHAIN = ("bing", "auto", "brave", "duckduckgo")


@dataclass
class GoogleSearchResult:
    title: str
    url: str
    description: str


def _ddgs_region(region: str, lang: str) -> str:
    if "-" in region:
        return region
    if region == "vn":
        return "vn-vi"
    if lang == "vi":
        return f"{region}-vi" if region else "vn-vi"
    return region or "wt-wt"


def _map_item(item: dict) -> Optional[GoogleSearchResult]:
    url = (item.get("href") or item.get("url") or "").strip()
    if not url:
        return None
    return GoogleSearchResult(
        title=item.get("title") or "",
        url=url,
        description=item.get("body") or item.get("description") or "",
    )


def _fetch_backend(
    query: str,
    num_results: int,
    region: str,
    lang: str,
    backend: str,
) -> List[GoogleSearchResult]:
    raw = DDGS().text(
        query,
        region=_ddgs_region(region, lang),
        max_results=num_results,
        backend=backend,
    )
    out: List[GoogleSearchResult] = []
    seen: set[str] = set()
    for item in raw:
        mapped = _map_item(item)
        if mapped and mapped.url not in seen:
            seen.add(mapped.url)
            out.append(mapped)
            if len(out) >= num_results:
                break
    return out


def iter_google_search(
    query: str,
    num_results: int = 100,
    lang: str = "vi",
    region: str = "vn",
    sleep_interval: float = 2.0,
    retries: int = 3,
    backoff: float = 2.0,
) -> Iterator[GoogleSearchResult]:
    """Yield kết quả tìm kiếm web. Thử lần lượt Bing → auto → Brave → DuckDuckGo."""
    last_err: Optional[Exception] = None

    for backend in BACKEND_CHAIN:
        for attempt in range(retries):
            try:
                if sleep_interval > 0:
                    time.sleep(sleep_interval if attempt == 0 else backoff * (2 ** attempt))
                results = _fetch_backend(query, num_results, region, lang, backend)
                if results:
                    print(
                        f"  [*] Backend '{backend}': {len(results)} kết quả cho '{query}'"
                    )
                    yield from results
                    return
                break
            except Exception as e:
                last_err = e
                msg = str(e).lower()
                retryable = any(
                    k in msg
                    for k in ("429", "timeout", "timed out", "connection", "blocked")
                )
                if attempt < retries - 1 and retryable:
                    wait = backoff * (2 ** attempt)
                    print(f"  [!] {backend} lỗi, thử lại sau {wait:.0f}s: {str(e)[:80]}")
                    time.sleep(wait)
                    continue
                break

    msg = (
        f"  [!] Không thu được kết quả cho '{query}' — "
        "thử lại sau hoặc kiểm tra mạng/VPN."
    )
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))
    if last_err:
        raise last_err
