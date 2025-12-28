"""
Web Scraping Agent Configuration
오픈업(OpenUB) 상권 정보 스크래핑 설정
"""

# =============================================================================
# 로그인 설정
# =============================================================================
LOGIN_CONFIG = {
    "enabled": True,
    "login_url": "https://auth.openub.com/",
    "credentials": {
        "email": "jj2jj2jj2jj2jj2@gmail.com",
        "password": "@letsmalet1",
    },
    # 로그인 폼 선택자
    "selectors": {
        "email_input": "input[type='email'], input[name='email'], #email",
        "password_input": "input[type='password'], input[name='password'], #password",
        "submit_button": "button[type='submit'], input[type='submit'], .login-btn",
    },
    # 로그인 성공 확인 (이 요소가 나타나면 로그인 성공)
    "success_indicator": ".user-profile, .logout, .my-page",
}

# =============================================================================
# 스크래핑 대상 URL
# =============================================================================
TARGET_URL = "https://www.openub.com/search?area=성수동"

# =============================================================================
# 브라우저 설정
# =============================================================================
BROWSER_CONFIG = {
    "headless": False,  # False: 브라우저 표시 (디버깅/선택자 확인용)
    "slow_mo": 500,     # 동작 간 지연시간 (ms) - 로그인 안정성 위해 증가
    "timeout": 60000,   # 페이지 로드 타임아웃 (ms) - 동적 로딩 대응
}

# =============================================================================
# CSS 선택자 설정 (오픈업 페이지 구조에 맞게 조정 필요)
# =============================================================================
# 참고: 실제 선택자는 브라우저 개발자 도구(F12)로 확인 후 수정하세요
SELECTORS = {
    # 각 상점/업체 카드 컨테이너
    "item_container": "[class*='card'], [class*='item'], [class*='store'], [class*='shop'], li",

    # 각 아이템에서 추출할 필드들
    "fields": {
        "name": "[class*='name'], [class*='title'], h3, h4",           # 상호명
        "category": "[class*='category'], [class*='type']",            # 업종
        "address": "[class*='address'], [class*='location']",          # 주소
        "sales": "[class*='sales'], [class*='revenue']",               # 매출
        "link": "a",                                                    # 상세 링크
    }
}

# =============================================================================
# 페이지네이션 설정
# =============================================================================
PAGINATION = {
    "enabled": True,
    "next_button": "[class*='next'], [class*='more'], button:has-text('다음')",
    "max_pages": 10,
}

# =============================================================================
# 대기 설정
# =============================================================================
WAIT_CONFIG = {
    "wait_for_selector": None,  # 특정 요소 대기 (예: ".store-list")
    "wait_time": 3000,          # 페이지 로드 후 추가 대기시간 (ms)
}

# =============================================================================
# 출력 설정
# =============================================================================
OUTPUT_CONFIG = {
    "filename": "openub_성수동_상권정보.csv",
    "encoding": "utf-8-sig",  # Excel 한글 호환
}

# =============================================================================
# User-Agent 설정
# =============================================================================
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
