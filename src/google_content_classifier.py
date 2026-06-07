"""Phân loại nội dung kết quả web search Tam quốc — domain-first 3 tầng."""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlparse

# Tier 1: domain allowlist (first-match wins, thứ tự quan trọng)
DOMAIN_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Game", (
        "play.google.com", "vplay.vn", "metatamquoc.vplay.vn", "taptap.cn", "y.4399.com",
        "garena.com", "vnggames.com", "gamek.vn", "2game.vn", "tmgame99.com", "afkmobi.com",
    )),
    ("Giải trí", (
        "youtube.com", "tiktok.com", "dailymotion.com", "bilibili.com", "youku.com",
        "kla.tv", "tram3d.tv", "gangjuwang.tv", "facebook.com", "reddit.com", "spotify.com",
    )),
    ("Điện ảnh", (
        "imdb.com", "netflix.com", "letterboxd.com", "mydramalist.com",
    )),
    ("Sách", (
        "goodreads.com", "fahasa.com", "bennghe.com.vn", "wodeshucheng5.com",
    )),
    ("Văn học", (
        "wattpad.com", "thegioivanhoc.com", "thuvientrithuc.net", "hoatieu.vn",
        "truyenhayaz.com", "haibogiay.net", "noron.vn", "22biqu.com", "archive.org",
        "thuvienhactrang.vn", "cdnc.heyzine.com",
    )),
    ("Bách khoa", (
        "wikipedia.org", "wikisource.org", "baike.baidu.com", "baike.sogou.com",
        "fandom.com", "namu.wiki", "tvtropes.org", "dewiki.de", "kongming.net",
        "cne3online.com",
    )),
    ("Nghiên cứu", (
        "scholar.google", "researchgate.net", "academia.edu",
    )),
    ("Học thuật", (
        "doi.org", "ieee.org", "springer.com", "jstor.org", "semanticscholar.org",
    )),
    ("Giáo dục", (
        "studocu.vn", "lop10.vn", "vietjack.com", "loigiaihay.com", "tuyensinh247.com",
        "giaoducthoidai.vn", "tiengtrung.vn", "study.com", "scholar.dlu.edu.vn",
        "zhishishu.top", "pressbooks.pub",
    )),
    ("Tín ngưỡng", (
        "phatgiao.org.vn", "godinh.com", "hinhmoc.com", "uma.vn", "goanphat.com",
        "shaolin-kungfu.com",
    )),
    ("Lịch sử", (
        "lichsuvietnam.org", "nghiencuulichsu.com", "lishirenwu.com",
        "ancientwarhistory.com",
    )),
    ("Tin tức", (
        "baomoi.com", "danviet.vn", "cafef.vn", "soha.vn", "vnreview.vn", "24h.com.vn",
        "doanhnghiepvn.vn", "kenh14.vn", "cafebiz.vn", "nguoiduatin.vn", "tienphong.vn",
        "tuoitre.vn", "vnexpress.net", "thanhnien.vn", "dantri.com.vn", "vietnamnet.vn",
        "afamily.vn", "vanhienplus.vn", "techz.vn", "khaimo.com", "trithucmoi.org",
        "phapluatplus.baophapluat.vn", "baophapluat.vn", "ngoisao.vn", "songdep.com.vn",
        "vtc.vn", "vtv.vn", "msn.com", "ft.com", "rfi.fr", "stcn.com",
        "chinanews.com.cn", "sohu.com", "news.qq.com", "news.bjd.com.cn", "m.thepaper.cn",
        "bbc.com", "livescience.com", "sixthtone.com", "chinahighlights.com",
        "autohome.com.cn",
    )),
    ("Blog", (
        "wordpress.com", "blogspot.com", "zhuanlan.zhihu.com", "cnblogs.com",
        "spiderum.com", "toplist.vn", "lazi.vn", "redsvn.net", "monan3mien.com",
        "hipstersofthecoast.com", "reboostlab.com",
    )),
    ("Hình ảnh", (
        "pinterest.com", "shutterstock.com", "pngtree.com", "pikbest.com",
    )),
    ("Thương mại", (
        "shopee.vn", "creations.vn", "winmart.vn", "ebay.ca", "ebay.com", "amazon.com",
        "new.khodochoitreem.com",
    )),
    ("Du lịch", (
        "vinwonders.com", "tourhot24h.vn", "luavietours.com", "hoianworldheritage.org.vn",
    )),
    ("MXH", (
        "zhihu.com",
    )),
]

# Tier 2: keyword signals (accent-stripped blob)
KEYWORD_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Game", (
        "dynasty warriors", "honor of king", "王者荣耀", "omg 3q", "mobgame", "steam",
        "game online", "game tam quoc", "three kingdoms all-star",
    )),
    ("Điện ảnh", (
        "imdb", "netflix", "phim", "movie", "drama", "dien vien", "review phim", "cinema",
    )),
    ("Giải trí", (
        "cai luong", "hat boi", "tuong", "podcast", "cải lương", "hát bội", "tuồng",
    )),
    ("Sách", (
        "nxb", "mua sach", "sach noi", "sách nói",
    )),
    ("Văn học", (
        "tom tat", "truyen", "tieu thuyet", "van hoc", "doc truyen", "tóm tắt", "truyện",
        "tiểu thuyết", "văn học",
    )),
    ("Tín ngưỡng", (
        "tho quan", "quan thanh", "den tho", "tuong quan", "phong thuy", "mieu", "chua ",
        "thờ quan", "đền thờ", "tượng quan", "phong thủy", "miếu", "chùa ",
    )),
    ("Lịch sử", (
        "lich su", "chinh su", "thoi tam quoc", "di san", "lịch sử", "chính sử",
        "thời tam quốc", "di sản",
    )),
    ("Tin tức", (
        "tin tuc", "bao chi", "thoi bao", "tin tức", "báo chí",
    )),
    ("Giáo dục", (
        "thuyet trinh", "bai tap", "phan tich nhan vat", "de thi",
        "thuyết trình", "bài tập", "phân tích nhân vật", "đề thi",
    )),
    ("Nghiên cứu", (
        "nghien cuu", "nghiên cứu",
    )),
    ("Học thuật", (
        ".edu/", ".ac.vn", "doi.org", "journal", "tap chi", "tạp chí",
    )),
    ("Báo cáo", (
        ".gov", "bao cao", "whitepaper", "báo cáo",
    )),
    ("Hình ảnh", (
        "hinh xam", "poster", "wallpaper", "hình xăm",
    )),
    ("Blog", (
        "blog", "forum", "dien dan", "diễn đàn",
    )),
    ("Thương mại", (
        "mua hang", "ban hang", "shop online",
    )),
    ("Du lịch", (
        "du lich", "kham pha", "du lịch", "khám phá", "tour ",
    )),
]

# Tier 3: query-intent fallback (accent-stripped search keyword)
QUERY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Game", ("tam quoc game", "game")),
    ("Điện ảnh", ("tam quoc phim", "phim")),
    ("Giải trí", ("tam quoc cai luong", "cai luong", "cải lương")),
    ("Tín ngưỡng", ("quan thanh de quan", "tho quan cong", "thờ quan")),
]

JUNK_DOMAINS = frozenset({
    "google.com", "w3snoop.com", "statshow.com", "appsimilar.com",
})

# apps.apple.com: Game nếu title chứa game/rpg
_APPLE_GAME_RE = re.compile(r"game|rpg|three kingdoms", re.I)


def _domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        return host.removeprefix("www.")
    except Exception:
        return ""


def strip_accents(text: str) -> str:
    if not isinstance(text, str):
        return ""
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn").lower()


def _normalize_title(title) -> str:
    if not isinstance(title, str):
        return ""
    t = title.strip()
    if t.lower() in ("", "nan"):
        return ""
    return t


def is_valid_result(url, title, description="") -> bool:
    """Loại kết quả SERP rác (URL/title không hợp lệ)."""
    if not url or not str(url).startswith("http"):
        return False
    if not _normalize_title(title):
        return False
    if _domain(url) in JUNK_DOMAINS:
        return False
    return True


def _match_domain(domain: str) -> str | None:
    d = domain.lower()
    for label, domains in DOMAIN_RULES:
        if any(dom in d for dom in domains):
            return label
    return None


def _match_keywords(blob: str) -> str | None:
    for label, signals in KEYWORD_RULES:
        if any(sig in blob for sig in signals):
            return label
    return None


def _match_query(query: str) -> str | None:
    q = strip_accents(query)
    for label, signals in QUERY_RULES:
        if any(sig in q for sig in signals):
            return label
    return None


def classify_content(
    url: str,
    title: str,
    description: str = "",
    domain: str = "",
    query: str = "",
) -> str:
    """Phân loại 3 tầng: domain → keyword → query-intent."""
    d = (domain or _domain(url)).lower()
    blob = strip_accents(f"{url} {title} {description}")

    # apps.apple.com đặc biệt
    if "apps.apple.com" in d and _APPLE_GAME_RE.search(f"{title} {description}"):
        return "Game"

    label = _match_domain(d)
    if label:
        return label

    label = _match_keywords(blob)
    if label:
        return label

    label = _match_query(query)
    if label:
        return label

    return "Khác"
