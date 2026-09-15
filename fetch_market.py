#!/usr/bin/env python3
"""환율/주가지수 데이터를 수집해 market.json으로 저장한다.

- 환율: Frankfurter API (https://api.frankfurter.dev) — 키 불필요, ECB 기준 환율.
- 주가지수: Yahoo Finance 비공식 차트 엔드포인트 — 키 불필요.

기준금리·물가·고용 등 거시 경제지표는 한국은행 ECOS/통계청 KOSIS처럼 개인이
직접 발급받아야 하는 API 키가 필요해 이번 범위에서는 제외했다.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

USER_AGENT = "Mozilla/5.0 (compatible; newsclipping-bot/1.0)"
KST = timezone(timedelta(hours=9))
DAYS = 30
OUTPUT_PATH = "market.json"

FX_PAIRS = [
    {"label": "USD/KRW", "base": "USD"},
    {"label": "EUR/KRW", "base": "EUR"},
    {"label": "JPY/KRW", "base": "JPY", "multiply": 100, "label_override": "JPY(100)/KRW"},
]

INDICES = [
    {"symbol": "^KS11", "label": "코스피"},
    {"symbol": "^KQ11", "label": "코스닥"},
    {"symbol": "^GSPC", "label": "S&P 500"},
    {"symbol": "^IXIC", "label": "나스닥"},
]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def fetch_fx_series(base: str, multiply: float = 1) -> list[dict]:
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=DAYS)
    url = (
        f"https://api.frankfurter.dev/v1/{start.isoformat()}..{end.isoformat()}"
        f"?from={urllib.parse.quote(base)}&to=KRW"
    )
    data = fetch_json(url)
    series = [
        {"date": date, "value": round(rates["KRW"] * multiply, 2)}
        for date, rates in sorted(data.get("rates", {}).items())
    ]
    return series


def fetch_index_series(symbol: str) -> list[dict]:
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}"
        f"?range={DAYS}d&interval=1d"
    )
    data = fetch_json(url)
    result = data["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    closes = result["indicators"]["quote"][0].get("close", [])
    series = []
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        date = datetime.fromtimestamp(ts, tz=KST).date().isoformat()
        series.append({"date": date, "value": round(close, 2)})
    return series


def main() -> None:
    result = {
        "updated_at": datetime.now(KST).isoformat(),
        "fx": [],
        "indices": [],
    }

    for pair in FX_PAIRS:
        label = pair.get("label_override", pair["label"])
        print(f"[환율] {label} 수집 중...")
        try:
            series = fetch_fx_series(pair["base"], pair.get("multiply", 1))
            print(f"  -> {len(series)}건 수집")
        except Exception as exc:
            print(f"  ! 수집 실패: {exc}")
            series = []
        result["fx"].append({"label": label, "series": series})

    for idx in INDICES:
        print(f"[지수] {idx['label']} 수집 중...")
        try:
            series = fetch_index_series(idx["symbol"])
            print(f"  -> {len(series)}건 수집")
        except Exception as exc:
            print(f"  ! 수집 실패: {exc}")
            series = []
        result["indices"].append({"label": idx["label"], "series": series})

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n{OUTPUT_PATH} 저장 완료 ({result['updated_at']})")


if __name__ == "__main__":
    main()
