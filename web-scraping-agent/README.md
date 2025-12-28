# Web Scraping Agent

Playwright 기반 동적 웹 스크래핑 에이전트입니다. JavaScript로 렌더링되는 동적 페이지도 스크래핑할 수 있습니다.

## 주요 기능

- Playwright 브라우저 자동화
- 동적 페이지 (JavaScript 렌더링) 지원
- 페이지네이션 자동 처리
- CSV 파일 출력
- CLI 인터페이스

## 설치

### 1. 가상환경 생성 (권장)

```bash
cd web-scraping-agent
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. Playwright 브라우저 설치

```bash
playwright install chromium
```

## 사용법

### 기본 실행

```bash
python agent.py
```

### CLI 옵션

```bash
# 특정 URL 스크래핑
python agent.py --url https://example.com

# 브라우저 표시 모드 (디버깅용)
python agent.py --headless false

# 출력 파일명 지정
python agent.py --output result.csv

# 모든 옵션 조합
python agent.py --url https://example.com --headless false --output result.csv
```

## 설정 (config.py)

스크래핑 대상 웹사이트에 맞게 `config.py`를 수정하세요.

### 1. 대상 URL 설정

```python
TARGET_URL = "https://example.com/products"
```

### 2. CSS 선택자 설정

```python
SELECTORS = {
    # 각 아이템을 감싸는 컨테이너
    "item_container": ".product-card",

    # 추출할 필드들
    "fields": {
        "title": ".product-title",
        "price": ".product-price",
        "description": ".product-desc",
        "link": "a",      # href 속성 자동 추출
        "image": "img",   # src 속성 자동 추출
    }
}
```

### 3. 페이지네이션 설정 (선택)

```python
PAGINATION = {
    "enabled": True,               # 페이지네이션 활성화
    "next_button": ".next-page",   # 다음 버튼 선택자
    "max_pages": 10,               # 최대 페이지 수
}
```

### 4. 대기 설정 (동적 로딩 대응)

```python
WAIT_CONFIG = {
    "wait_for_selector": ".loaded",  # 특정 요소 대기
    "wait_time": 3000,               # 추가 대기시간 (ms)
}
```

## CSS 선택자 찾는 방법

1. 브라우저에서 대상 웹사이트 열기
2. F12 (개발자 도구) 열기
3. Elements 탭에서 원하는 요소 선택
4. 우클릭 → Copy → Copy selector

또는 `--headless false` 옵션으로 실행하여 브라우저 동작을 직접 확인할 수 있습니다.

## 출력 예시

```
🕷️  Web Scraping Agent 시작
🚀 브라우저 시작 중... (headless: True)
✅ 브라우저 준비 완료
📄 페이지 로딩 중: https://example.com
✅ 페이지 로딩 완료
📦 25개 아이템 발견
  [1] ['상품명1', '10,000원']...
  [2] ['상품명2', '20,000원']...
  ...
✅ 총 25개 데이터 수집 완료
💾 CSV 저장 완료: scraped_data.csv
🎉 스크래핑 완료!
```

## 주의사항

- 웹사이트의 robots.txt와 이용약관을 확인하세요
- 과도한 요청은 IP 차단의 원인이 될 수 있습니다
- `slow_mo` 설정으로 요청 간격을 조절하세요
- 상업적 목적의 스크래핑은 법적 검토가 필요할 수 있습니다

## 트러블슈팅

### "데이터를 수집하지 못했습니다"
- CSS 선택자가 올바른지 확인
- `--headless false`로 실행하여 페이지 상태 확인
- `wait_time`을 늘려 로딩 대기

### "타임아웃" 오류
- `config.py`의 `timeout` 값 증가
- 네트워크 연결 확인

### 한글 깨짐 (CSV)
- `encoding: "utf-8-sig"` 설정 확인 (Excel 호환)
