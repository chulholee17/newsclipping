# newsclipping

경제 뉴스를 키워드별로 수집해 카테고리 탭으로 보여주는 정적 사이트.
https://chulholee17.github.io/newsclipping/

## 구성

- `fetch_news.py` — [Google 뉴스 RSS](https://news.google.com/rss/search)에서 카테고리별 키워드로 기사를 수집해 `news.json`으로 저장. 기사마다 `title`/`link`/`source`/`pub_date`/`category` 필드를 담는다. (네이버의 구 RSS 검색 파라미터 `where=rss`는 더 이상 RSS를 반환하지 않아 사용하지 않음)
- `fetch_market.py` — [Frankfurter](https://api.frankfurter.dev)(환율)와 Yahoo Finance 비공식 차트 API(주가지수)에서 최근 30일 데이터를 모아 `market.json`으로 저장. 둘 다 API 키 불필요.
- `news.json` / `market.json` — 수집 결과. `index.html`이 읽어서 화면에 표시.
- `index.html` — 상단에 환율/주가지수 그래프(Chart.js), 그 아래 카테고리 탭 뉴스 목록. 키워드 입력창으로 제목 필터링, 기사별 ☆ 버튼으로 개별 저장(북마크, `localStorage`), "현재 목록 오프라인 저장" 버튼으로 전체 목록을 캐시해 네트워크 오류 시에도 표시.
- `.github/workflows/update-news.yml` — 매일 08:00 KST에 `fetch_news.py`·`fetch_market.py`를 실행해 `news.json`/`market.json`을 갱신하고 자동 커밋/푸시.

### 아직 없는 것

기준금리·물가·고용률 같은 거시 경제지표는 한국은행 ECOS/통계청 KOSIS API가 필요한데, 이건 개인이 직접 무료 가입해서 키를 발급받아야 한다. 키를 발급받으면 `fetch_market.py`에 추가할 수 있다.

## 카테고리/키워드 수정

`fetch_news.py`의 `CATEGORIES` 딕셔너리를 수정하면 된다.

```python
CATEGORIES = {
    "증시": ["코스피", "코스닥"],
    ...
}
```

## 로컬 실행

```bash
python3 fetch_news.py     # news.json 갱신
python3 fetch_market.py   # market.json 갱신
python3 -m http.server 8000   # index.html 로컬 확인 (http://localhost:8000)
```
