# newsclipping

경제 뉴스를 키워드별로 수집해 카테고리 탭으로 보여주는 정적 사이트.
https://chulholee17.github.io/newsclipping/

## 구성

- `fetch_news.py` — [Google 뉴스 RSS](https://news.google.com/rss/search)에서 카테고리별 키워드로 기사를 수집해 `news.json`으로 저장. (네이버의 구 RSS 검색 파라미터 `where=rss`는 더 이상 RSS를 반환하지 않아 사용하지 않음)
- `news.json` — 수집 결과. `index.html`이 읽어서 화면에 표시.
- `index.html` — 카테고리 탭 UI. "저장" 버튼을 누르면 현재 뉴스 목록을 브라우저 `localStorage`에 저장해, 네트워크 오류 시에도 마지막 저장본을 볼 수 있음.
- `.github/workflows/update-news.yml` — 매일 08:00 KST에 `fetch_news.py`를 실행해 `news.json`을 갱신하고 자동 커밋/푸시.

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
python3 fetch_news.py   # news.json 갱신
python3 -m http.server 8000   # index.html 로컬 확인 (http://localhost:8000)
```
