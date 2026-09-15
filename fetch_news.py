#!/usr/bin/env python3
"""경제 뉴스를 키워드별로 수집해 news.json으로 저장한다.

네이버의 구 RSS 검색(where=rss)은 더 이상 RSS를 반환하지 않아(현재는 일반 검색
HTML만 응답) Google 뉴스 RSS(https://news.google.com/rss/search)를 대신 사용한다.
API 키 없이 한국어 뉴스를 안정적으로 가져올 수 있다.
"""

import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

RSS_URL = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
USER_AGENT = "Mozilla/5.0 (compatible; newsclipping-bot/1.0)"
KST = timezone(timedelta(hours=9))
ARTICLES_PER_CATEGORY = 12
OUTPUT_PATH = "news.json"

# 카테고리별 검색 키워드. 필요에 따라 자유롭게 추가/수정한다.
CATEGORIES = {
    "증시": ["코스피", "코스닥"],
    "환율/금리": ["원달러 환율", "기준금리"],
    "부동산": ["부동산 시장", "아파트 가격"],
    "산업/기업": ["반도체 수출", "기업 실적"],
    "고용/물가": ["소비자물가", "고용률"],
}


def fetch_rss(query: str) -> bytes:
    url = RSS_URL.format(query=urllib.parse.quote(query))
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def parse_items(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall("./channel/item"):
        raw_title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date_raw = (item.findtext("pubDate") or "").strip()

        # Google 뉴스 제목은 "기사 제목 - 출처" 형식
        source = ""
        title = raw_title
        m = re.match(r"^(.*)\s-\s([^-]+)$", raw_title)
        if m:
            title, source = m.group(1).strip(), m.group(2).strip()

        try:
            pub_dt = parsedate_to_datetime(pub_date_raw)
            if pub_dt.tzinfo is None:
                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pub_dt = datetime.now(timezone.utc)

        items.append(
            {
                "title": title,
                "link": link,
                "source": source,
                "pub_date": pub_dt.astimezone(KST).isoformat(),
                "_sort_key": pub_dt.timestamp(),
            }
        )
    return items


def collect_category(keywords: list[str]) -> list[dict]:
    seen_titles = set()
    articles: list[dict] = []
    for keyword in keywords:
        try:
            xml_bytes = fetch_rss(keyword)
            items = parse_items(xml_bytes)
        except Exception as exc:  # 네트워크/파싱 오류는 해당 키워드만 건너뛴다
            print(f"  ! '{keyword}' 수집 실패: {exc}")
            continue
        for item in items:
            if item["title"] in seen_titles:
                continue
            seen_titles.add(item["title"])
            articles.append(item)

    articles.sort(key=lambda a: a["_sort_key"], reverse=True)
    for a in articles:
        del a["_sort_key"]
    return articles[:ARTICLES_PER_CATEGORY]


def main() -> None:
    result = {
        "updated_at": datetime.now(KST).isoformat(),
        "categories": [],
    }

    for name, keywords in CATEGORIES.items():
        print(f"[{name}] 수집 중... ({', '.join(keywords)})")
        articles = collect_category(keywords)
        print(f"  -> {len(articles)}건 수집")
        result["categories"].append({"name": name, "articles": articles})

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n{OUTPUT_PATH} 저장 완료 ({result['updated_at']})")


if __name__ == "__main__":
    main()
