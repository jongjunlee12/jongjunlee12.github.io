"""
Web Scraping Agent Configuration
스크래핑할 웹사이트 설정을 여기서 관리합니다.
"""

# 스크래핑 대상 URL
TARGET_URL = "https://example.com"  # 실제 URL로 변경하세요

# 브라우저 설정
BROWSER_CONFIG = {
    "headless": True,  # True: 브라우저 숨김, False: 브라우저 표시
    "slow_mo": 100,    # 동작 간 지연시간 (ms) - 디버깅시 유용
    "timeout": 30000,  # 페이지 로드 타임아웃 (ms)
}

# CSS 선택자 설정 (대상 웹사이트에 맞게 수정 필요)
SELECTORS = {
    # 데이터를 포함하는 각 아이템 컨테이너
    "item_container": ".item",  # 예: ".product-card", "article", "[data-item]"

    # 각 아이템에서 추출할 필드들
    "fields": {
        "title": ".item-title",        # 제목
        "price": ".item-price",        # 가격
        "description": ".item-desc",   # 설명
        "link": "a",                   # 링크 (href 속성)
        "image": "img",                # 이미지 (src 속성)
    }
}

# 페이지네이션 설정 (여러 페이지 스크래핑시)
PAGINATION = {
    "enabled": False,              # 페이지네이션 사용 여부
    "next_button": ".next-page",   # 다음 페이지 버튼 선택자
    "max_pages": 5,                # 최대 페이지 수
}

# 대기 설정
WAIT_CONFIG = {
    "wait_for_selector": None,     # 특정 요소가 나타날 때까지 대기 (예: ".loaded")
    "wait_time": 2000,             # 페이지 로드 후 추가 대기시간 (ms)
}

# 출력 설정
OUTPUT_CONFIG = {
    "filename": "scraped_data.csv",  # 출력 파일명
    "encoding": "utf-8-sig",         # 인코딩 (Excel 한글 호환: utf-8-sig)
}

# User-Agent 설정 (봇 감지 우회용)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
