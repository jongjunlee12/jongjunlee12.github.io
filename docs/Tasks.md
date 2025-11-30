# 🤖 [Isochrone Map Viewer] AI 코딩 착수용 프롬프트

> **사용법**: 아래 프롬프트를 복사하여 AI 코더(Claude, GPT 등)에게 붙여넣으세요.
> PRD.md와 TRD.md 파일도 함께 첨부하세요.

---

## 📋 시스템 프롬프트 (복사용)

```
너는 Python Streamlit 1.51.0의 수석 개발자야.

첨부한 [요구사항 정의서(PRD.md)]의 기능을 구현하되, [기술 사양서(TRD.md)]의 스택과 아키텍처를 엄격하게 준수해.

## 필수 준수 사항

1. **라이브러리 버전 고정**
   - streamlit==1.51.0
   - folium==0.20.0
   - streamlit-folium==0.25.3
   - openrouteservice==2.3.3
   - python-dotenv==1.0.1

   위 라이브러리만 사용하고, 다른 라이브러리를 임의로 추가하지 마.

2. **프로젝트 구조**
   단일 파일(app.py) 구조를 유지해. 불필요한 모듈 분리 금지.

3. **좌표 순서 주의**
   OpenRouteService API는 [경도, 위도] 순서를 사용해.
   사용자 입력은 [위도, 경도]로 받되, API 호출 시 순서를 바꿔야 해.

4. **시간 단위**
   사용자에게는 '분' 단위로 보여주되, API 호출 시 '초' 단위로 변환해.

5. **지도 스타일**
   반드시 Carto Positron (tiles="CartoDB Positron") 사용.

6. **API 키 관리**
   - .env 파일에서 ORS_API_KEY 환경변수로 관리
   - 코드에 API 키 하드코딩 절대 금지
   - Streamlit Cloud 배포 시 st.secrets 사용

7. **에러 처리**
   API 호출 실패 시 st.error()로 사용자 친화적 메시지 표시.

## 개발 순서

먼저 프로젝트 폴더 구조부터 잡아줘:

isochrone-map-viewer/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
└── README.md

그 다음 순서대로 구현해:
1. requirements.txt 작성
2. .env.example 작성
3. .gitignore 작성
4. .streamlit/config.toml 작성
5. app.py 메인 로직 구현
6. README.md 작성

## 절대 하지 말 것

- 사양서에 없는 기능 임의 추가
- 라이브러리 버전 변경
- 복잡한 클래스/모듈 구조
- 추가 설명 없이 코드 생략 ("..." 등)
- API 키를 코드에 직접 작성

## app.py 핵심 구현 가이드

```python
import streamlit as st
import folium
from streamlit_folium import st_folium
import openrouteservice
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Isochrone Map Viewer",
    page_icon="🗺️",
    layout="wide"
)

# 사이드바: 입력 컨트롤
# - 위도/경도 입력 (st.number_input)
# - 이동수단 선택 (st.radio: 도보/차량)
# - 시간 선택 (st.selectbox: 5분, 10분, 15분, 30분, 60분)
# - 실행 버튼 (st.button)

# 메인 영역: 지도 표시
# - Folium 지도 생성 (CartoDB Positron)
# - 아이소크론 폴리곤 표시
# - 중심점 마커 표시
# - st_folium()으로 렌더링
```

위 구조를 기반으로 전체 코드를 완성해줘.
```

---

## 🚀 빠른 시작 프롬프트 (간단 버전)

아래는 문서 첨부 없이 빠르게 시작하고 싶을 때 사용하세요:

```
Streamlit으로 아이소크론 맵 뷰어를 만들어줘.

요구사항:
1. 위도/경도 좌표 입력
2. 도보/차량 선택
3. 시간(분) 선택: 5, 10, 15, 30, 60분
4. OpenRouteService 무료 API로 아이소크론 계산
5. Carto Positron 스타일 지도에 결과 표시

기술 스택 (버전 고정):
- Python 3.11+
- streamlit==1.51.0
- folium==0.20.0
- streamlit-folium==0.25.3
- openrouteservice==2.3.3

주의:
- OpenRouteService API는 [경도, 위도] 순서 사용
- API 키는 .env 파일로 관리
- 단일 파일(app.py) 구조 유지

먼저 폴더 구조부터 잡아줘.
```

---

## 📁 첨부 파일 체크리스트

AI 코더에게 전달할 때 다음 파일들을 함께 첨부하세요:

- [ ] `PRD.md` - 요구사항 정의서
- [ ] `TRD.md` - 기술 사양서
- [ ] 이 파일 (`Tasks.md`) - 시스템 프롬프트

---

## 🔑 사전 준비 사항

AI 코딩을 시작하기 전에 다음을 준비하세요:

### 1. OpenRouteService API 키 발급

1. [OpenRouteService 회원가입](https://openrouteservice.org/dev/#/signup) 접속
2. 이메일 인증 완료
3. Dashboard에서 API Key 복사
4. `.env` 파일에 저장:
   ```
   ORS_API_KEY=your_api_key_here
   ```

### 2. Python 환경 준비

```bash
# Python 3.11 이상 확인
python --version

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

---

## ✅ 완료 후 테스트 체크리스트

개발 완료 후 다음을 확인하세요:

- [ ] `streamlit run app.py`로 정상 실행
- [ ] 서울 좌표 (37.5665, 126.9780) 입력 테스트
- [ ] 도보 15분 아이소크론 표시 확인
- [ ] 차량 30분 아이소크론 표시 확인
- [ ] 지도 스타일이 Carto Positron (밝은 회색)인지 확인
- [ ] API 키 없을 때 에러 메시지 표시 확인
