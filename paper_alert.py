from __future__ import annotations

import datetime as dt
import json
import os
import re
from dataclasses import dataclass
from typing import Iterable

import feedparser
import requests
from dotenv import load_dotenv


ARXIV_API = "https://export.arxiv.org/api/query"
CROSSREF_API = "https://api.crossref.org/works"
KAKAO_TOKEN_API = "https://kauth.kakao.com/oauth/token"
KAKAO_SEND_API = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

DEFAULT_KEYWORDS = [
    "webtoon",
    "digital comics",
    "animation",
    "anime",
    "text mining",
    "natural language processing",
    "nlp",
    "topic modeling",
    "sentiment analysis",
]

DEFAULT_KR_KEYWORDS = [
    "웹툰",
    "애니메이션",
    "만화",
    "텍스트마이닝",
    "텍스트 마이닝",
    "자연어처리",
    "감성분석",
    "토픽모델링",
]


@dataclass
class Paper:
    title: str
    abstract: str
    url: str
    source: str
    published: dt.date
    journal: str = ""
    doi: str = ""
    language: str = ""
    score: int = 0
    reason: str = ""


def utc_today() -> dt.date:
    return dt.datetime.now(dt.timezone.utc).date()


def env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def tokenize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def parse_date_maybe(value: str) -> dt.date:
    if not value:
        return utc_today()
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return utc_today()


def load_journal_whitelist(path: str = "journal_whitelist.txt") -> set[str]:
    if not os.path.exists(path):
        return set()
    journals: set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            journals.add(tokenize(line))
    return journals


def fetch_arxiv(keywords: list[str], lookback_days: int, max_items: int) -> list[Paper]:
    joined = " OR ".join([f'all:"{kw}"' for kw in keywords])
    params = {
        "search_query": joined,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "start": 0,
        "max_results": max_items,
    }
    resp = requests.get(ARXIV_API, params=params, timeout=25)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    min_date = utc_today() - dt.timedelta(days=lookback_days)

    items: list[Paper] = []
    for entry in feed.entries:
        published = parse_date_maybe(entry.get("published", ""))
        if published < min_date:
            continue
        items.append(
            Paper(
                title=(entry.get("title") or "").replace("\n", " ").strip(),
                abstract=(entry.get("summary") or "").replace("\n", " ").strip(),
                url=entry.get("link", ""),
                source="arXiv",
                published=published,
                journal="arXiv",
                doi="",
                language="en",
            )
        )
    return items


def _crossref_title(item: dict) -> str:
    title = item.get("title") or []
    if isinstance(title, list) and title:
        return str(title[0]).strip()
    return ""


def _crossref_abstract(item: dict) -> str:
    abstract = str(item.get("abstract", "") or "")
    abstract = re.sub(r"<[^>]+>", " ", abstract)
    return re.sub(r"\s+", " ", abstract).strip()


def _crossref_doi_url(item: dict) -> str:
    doi = str(item.get("DOI", "") or "")
    return f"https://doi.org/{doi}" if doi else str(item.get("URL", "") or "")


def fetch_crossref(keywords: list[str], lookback_days: int, max_items: int) -> list[Paper]:
    min_date = utc_today() - dt.timedelta(days=lookback_days)
    min_date_s = min_date.isoformat()
    out: list[Paper] = []
    per_keyword = max(5, max_items // max(1, len(keywords)))

    for kw in keywords:
        params = {
            "query": kw,
            "filter": f"from-pub-date:{min_date_s},type:journal-article",
            "rows": per_keyword,
            "sort": "published",
            "order": "desc",
        }
        resp = requests.get(CROSSREF_API, params=params, timeout=25)
        if resp.status_code >= 400:
            # Skip noisy keyword-level failures instead of failing the whole run.
            continue
        payload = resp.json()
        items = payload.get("message", {}).get("items", [])
        for item in items:
            title = _crossref_title(item)
            if not title:
                continue
            journal = ""
            container = item.get("container-title") or []
            if isinstance(container, list) and container:
                journal = str(container[0]).strip()
            date_parts = (
                item.get("published-online", {}).get("date-parts")
                or item.get("published-print", {}).get("date-parts")
                or item.get("created", {}).get("date-parts")
                or [[utc_today().year, utc_today().month, utc_today().day]]
            )
            parts = date_parts[0] if date_parts and isinstance(date_parts, list) else [utc_today().year, 1, 1]
            year = int(parts[0]) if len(parts) > 0 else utc_today().year
            month = int(parts[1]) if len(parts) > 1 else 1
            day = int(parts[2]) if len(parts) > 2 else 1
            published = dt.date(year, month, day)
            if published < min_date:
                continue
            out.append(
                Paper(
                    title=title,
                    abstract=_crossref_abstract(item),
                    url=_crossref_doi_url(item),
                    source="Crossref",
                    published=published,
                    journal=journal,
                    doi=str(item.get("DOI", "") or ""),
                    language=str(item.get("language", "") or "").lower(),
                )
            )
    return out


def fetch_crossref_korean(keywords: list[str], lookback_days: int, max_items: int) -> list[Paper]:
    min_date = utc_today() - dt.timedelta(days=lookback_days)
    min_date_s = min_date.isoformat()
    out: list[Paper] = []
    per_keyword = max(8, max_items // max(1, len(keywords)))

    for kw in keywords:
        params = {
            "query": kw,
            "filter": f"from-pub-date:{min_date_s},type:journal-article",
            "rows": per_keyword,
            "sort": "published",
            "order": "desc",
        }
        resp = requests.get(CROSSREF_API, params=params, timeout=25)
        if resp.status_code >= 400:
            continue
        items = resp.json().get("message", {}).get("items", [])
        for item in items:
            title = _crossref_title(item)
            if not title:
                continue
            journal = ""
            container = item.get("container-title") or []
            if isinstance(container, list) and container:
                journal = str(container[0]).strip()
            date_parts = (
                item.get("published-online", {}).get("date-parts")
                or item.get("published-print", {}).get("date-parts")
                or item.get("created", {}).get("date-parts")
                or [[utc_today().year, utc_today().month, utc_today().day]]
            )
            parts = date_parts[0] if date_parts and isinstance(date_parts, list) else [utc_today().year, 1, 1]
            year = int(parts[0]) if len(parts) > 0 else utc_today().year
            month = int(parts[1]) if len(parts) > 1 else 1
            day = int(parts[2]) if len(parts) > 2 else 1
            published = dt.date(year, month, day)
            if published < min_date:
                continue
            lang = str(item.get("language", "") or "").lower()
            has_hangul = bool(re.search(r"[가-힣]", f"{title} {_crossref_abstract(item)} {journal}"))
            if lang not in ("ko", "kor") and not has_hangul:
                continue
            out.append(
                Paper(
                    title=title,
                    abstract=_crossref_abstract(item),
                    url=_crossref_doi_url(item),
                    source="Crossref-KR",
                    published=published,
                    journal=journal,
                    doi=str(item.get("DOI", "") or ""),
                    language=lang,
                )
            )
    return out


def score_papers(
    papers: Iterable[Paper],
    keywords: list[str],
    whitelist: set[str],
    strict_journal_filter: bool,
) -> list[Paper]:
    scored: list[Paper] = []
    low_keywords = [tokenize(k) for k in keywords]
    for paper in papers:
        title = tokenize(paper.title)
        abstract = tokenize(paper.abstract)
        hay = f"{title} {abstract}"

        score = 0
        hits: list[str] = []
        for kw in low_keywords:
            if kw in hay:
                score += 3 if kw in title else 1
                hits.append(kw)

        if paper.language in ("en", "eng", ""):
            score += 1
        is_korean = bool(
            paper.language in ("ko", "kor")
            or re.search(r"[가-힣]", f"{paper.title} {paper.abstract} {paper.journal}")
        )
        if is_korean:
            # Prefer Korean/KCI-like papers for this user's digest.
            score += 10
            hits.append("korean")
        else:
            score -= 1
        if paper.source == "arXiv":
            score += 1
        if paper.source == "Crossref-KR":
            score += 4
            hits.append("crossref-kr")
        if paper.journal and tokenize(paper.journal) in whitelist:
            score += 3
            hits.append("journal-whitelist")

        if strict_journal_filter and paper.source != "arXiv":
            if tokenize(paper.journal) not in whitelist:
                continue

        paper.score = score
        paper.reason = ", ".join(sorted(set(hits))) if hits else "keyword-match"
        if score > 0:
            scored.append(paper)

    scored.sort(key=lambda p: (p.score, p.published), reverse=True)
    return scored


def deduplicate(papers: Iterable[Paper]) -> list[Paper]:
    seen: set[str] = set()
    out: list[Paper] = []
    for p in papers:
        key = tokenize(p.doi) if p.doi else tokenize(p.title)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def build_kakao_message(papers: list[Paper], max_count: int = 8) -> dict:
    if not papers:
        desc = "No new papers matched your filters today."
    else:
        lines: list[str] = []
        for idx, p in enumerate(papers[:max_count], start=1):
            line = (
                f"{idx}) [{p.source}] {p.title[:78]}\n"
                f"{p.published.isoformat()} | {p.journal[:32]}\n"
                f"DOI: {p.url}"
            )
            lines.append(line)
        desc = "\n\n".join(lines)

    return {
        "object_type": "text",
        "text": f"[Daily Paper Alert]\n{utc_today().isoformat()}\n\n{desc}",
        "link": {
            "web_url": "https://www.google.com",
            "mobile_web_url": "https://www.google.com",
        },
        "button_title": "",
    }


def refresh_access_token() -> str:
    rest_api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    client_secret = os.getenv("KAKAO_CLIENT_SECRET", "").strip()
    refresh_token = os.getenv("KAKAO_REFRESH_TOKEN", "").strip()
    if not rest_api_key or not refresh_token:
        raise RuntimeError("KAKAO_REST_API_KEY, KAKAO_REFRESH_TOKEN are required.")
    data = {
        "grant_type": "refresh_token",
        "client_id": rest_api_key,
        "refresh_token": refresh_token,
    }
    if client_secret:
        data["client_secret"] = client_secret
    resp = requests.post(KAKAO_TOKEN_API, data=data, timeout=20)
    if resp.status_code >= 400:
        raise RuntimeError(f"Failed to refresh token: {resp.status_code} {resp.text}")
    token = resp.json()
    access_token = token.get("access_token", "")
    if not access_token:
        raise RuntimeError("No access_token in refresh response.")
    return access_token


def send_kakao_to_me(access_token: str, message_obj: dict) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"template_object": json.dumps(message_obj, ensure_ascii=True)}
    resp = requests.post(KAKAO_SEND_API, headers=headers, data=data, timeout=20)
    if resp.status_code >= 400:
        raise RuntimeError(f"Failed to send Kakao message: {resp.status_code} {resp.text}")
    payload = resp.json()
    if payload.get("result_code") != 0:
        raise RuntimeError(f"Kakao API returned non-zero result_code: {payload}")


def run() -> None:
    load_dotenv()
    keywords_raw = os.getenv("KEYWORDS", "").strip()
    keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()] if keywords_raw else DEFAULT_KEYWORDS
    lookback_days = env_int("LOOKBACK_DAYS", 2)
    max_per_source = env_int("MAX_ITEMS_PER_SOURCE", 30)
    kci_lookback_days = env_int("KCI_LOOKBACK_DAYS", 30)
    max_kci_items = env_int("MAX_KCI_ITEMS", 60)
    max_send_count = env_int("MAX_SEND_COUNT", 5)
    strict = os.getenv("STRICT_JOURNAL_FILTER", "false").strip().lower() == "true"
    whitelist = load_journal_whitelist()

    arxiv_papers = fetch_arxiv(keywords, lookback_days, max_per_source)
    crossref_papers = fetch_crossref(keywords, lookback_days, max_per_source)
    crossref_kr = fetch_crossref_korean(DEFAULT_KR_KEYWORDS, kci_lookback_days, max_kci_items)
    all_keywords = keywords + DEFAULT_KR_KEYWORDS
    scored = score_papers(arxiv_papers + crossref_papers + crossref_kr, all_keywords, whitelist, strict)
    unique = deduplicate(scored)
    top = unique[:max_send_count]

    access_token = os.getenv("KAKAO_ACCESS_TOKEN", "").strip()
    if not access_token:
        access_token = refresh_access_token()

    message_obj = build_kakao_message(top)
    send_kakao_to_me(access_token, message_obj)

    print(f"Sent {len(top)} paper(s) to KakaoTalk.")


if __name__ == "__main__":
    run()
