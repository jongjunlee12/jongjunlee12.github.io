# 🗺️ Isochrone Map Viewer

특정 좌표에서 **도보/차량**으로 일정 시간 내 도달 가능한 영역(아이소크론)을 지도 위에 시각화하는 도구입니다.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.51.0-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 특징

- **API 키 불필요** - OpenStreetMap 데이터를 직접 다운로드하여 사용
- **로컬 계산** - 아이소크론 계산이 100% 로컬에서 수행됨
- **무제한 사용** - 외부 API 호출 제한 없음
- **깔끔한 UI** - Carto Positron 스타일의 밝은 회색 지도

## 🖼️ 스크린샷

```
┌─────────────────────────────────────────────────────────────┐
│  🗺️ Isochrone Map Viewer                                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─── 사이드바 ───┐   ┌─────── 지도 영역 ───────────────┐   │
│  │ 📍 좌표 입력    │   │                                 │   │
│  │ 위도: 37.5665  │   │      ┌─────────────────┐        │   │
│  │ 경도: 126.9780 │   │      │   아이소크론     │        │   │
│  │                │   │      │    폴리곤       │        │   │
│  │ 🚶 도보 / 🚗 차량│   │      └─────────────────┘        │   │
│  │ ⏱️ 15분        │   │             📍                  │   │
│  │                │   │          (출발점)               │   │
│  │ [🔍 실행]      │   │                                 │   │
│  └────────────────┘   └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/isochrone-map-viewer.git
cd isochrone-map-viewer
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 📦 기술 스택

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| Streamlit | 1.51.0 | 웹 프레임워크 |
| OSMnx | 2.0.7 | OpenStreetMap 데이터 다운로드 |
| NetworkX | 3.4+ | 그래프 분석 (아이소크론 계산) |
| Folium | 0.19.0 | 지도 시각화 |
| GeoPandas | 1.0+ | 지리 데이터 처리 |
| Shapely | 2.0+ | 폴리곤 생성 |

## 📖 사용법

1. **좌표 입력**: 위도와 경도를 입력 (기본값: 서울시청)
2. **이동 수단 선택**: 도보 🚶 또는 차량 🚗
3. **시간 선택**: 5분, 10분, 15분, 30분, 60분 중 선택
4. **실행**: "아이소크론 생성" 버튼 클릭

## ⚠️ 주의사항

- **첫 실행 시** 도로 네트워크 다운로드로 10~30초 소요
- **이후 실행**은 캐싱으로 5초 이내
- 인터넷 연결 필요 (도로 네트워크 다운로드)

## 🔧 트러블슈팅

### OSMnx 설치 오류

```bash
# conda 사용 권장
conda install -c conda-forge osmnx
```

### 메모리 부족

큰 영역(60분 차량 등)은 메모리를 많이 사용합니다.
시간을 줄이거나 도보 모드를 사용해보세요.

## 📄 라이선스

MIT License

## 🙏 감사

- [OSMnx](https://github.com/gboeing/osmnx) by Geoff Boeing
- [OpenStreetMap](https://www.openstreetmap.org/) contributors
- [Streamlit](https://streamlit.io/) team
