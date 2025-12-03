"""
Mapbox Isochrone Map Dashboard
Mapbox API를 사용하여 특정 좌표에서 도달 가능한 영역을 시각화하는 대시보드
"""

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="Mapbox Isochrone Dashboard",
    page_icon="🗺️",
    layout="wide"
)

# 이동 수단 설정
PROFILES = {
    "도보 🚶": "walking",
    "자전거 🚴": "cycling",
    "자동차 🚗": "driving",
    "교통체증 반영 🚗": "driving-traffic"
}

# 시간 옵션 (분)
TIME_OPTIONS = [5, 10, 15, 20, 30, 45, 60]

# 색상 설정 (시간대별)
COLORS = ["#00ff00", "#66ff00", "#ccff00", "#ffff00", "#ffcc00", "#ff6600", "#ff0000"]


def get_isochrone(access_token: str, lon: float, lat: float,
                  profile: str, minutes: list) -> dict:
    """Mapbox Isochrone API 호출"""

    # 최대 4개 contour만 허용
    minutes = minutes[:4]
    contours = ",".join(map(str, minutes))

    url = f"https://api.mapbox.com/isochrone/v1/mapbox/{profile}/{lon},{lat}"

    params = {
        "contours_minutes": contours,
        "polygons": "true",
        "access_token": access_token
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API 오류: {response.status_code} - {response.text}")


def create_map(lat: float, lon: float, geojson_data: dict = None,
               selected_times: list = None) -> folium.Map:
    """Folium 지도 생성"""

    m = folium.Map(
        location=[lat, lon],
        tiles="CartoDB Positron",
        zoom_start=13
    )

    # 아이소크론 폴리곤 추가 (역순으로 추가해서 작은 영역이 위에 오도록)
    if geojson_data and "features" in geojson_data:
        features = geojson_data["features"]

        for i, feature in enumerate(reversed(features)):
            contour = feature.get("properties", {}).get("contour", 0)
            color_idx = min(i, len(COLORS) - 1)

            folium.GeoJson(
                feature,
                style_function=lambda x, c=COLORS[color_idx]: {
                    "fillColor": c,
                    "color": c,
                    "weight": 2,
                    "fillOpacity": 0.3
                },
                tooltip=f"{contour}분 도달 영역"
            ).add_to(m)

    # 중심점 마커
    folium.Marker(
        location=[lat, lon],
        popup="출발점",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    return m


def main():
    st.title("🗺️ Mapbox Isochrone Dashboard")
    st.caption("Mapbox API를 사용하여 특정 위치에서 도달 가능한 영역을 시각화합니다")

    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")

        # API 토큰 입력
        st.subheader("🔑 Mapbox Access Token")
        access_token = st.text_input(
            "Access Token",
            type="password",
            placeholder="pk.eyJ1Ijo...",
            help="Mapbox 계정에서 발급받은 Access Token을 입력하세요"
        )

        if not access_token:
            st.warning("⚠️ Access Token을 입력하세요")

        st.divider()

        # 좌표 입력
        st.subheader("📍 좌표 입력")
        lat = st.number_input(
            "위도 (Latitude)",
            min_value=-90.0,
            max_value=90.0,
            value=37.5665,
            step=0.0001,
            format="%.4f"
        )
        lon = st.number_input(
            "경도 (Longitude)",
            min_value=-180.0,
            max_value=180.0,
            value=126.9780,
            step=0.0001,
            format="%.4f"
        )

        st.divider()

        # 이동 수단
        st.subheader("🚶 이동 수단")
        profile = st.radio(
            "이동 수단 선택",
            options=list(PROFILES.keys()),
            index=0,
            label_visibility="collapsed"
        )

        st.divider()

        # 시간 선택 (최대 4개)
        st.subheader("⏱️ 시간 선택")
        st.caption("최대 4개까지 선택 가능")

        selected_times = st.multiselect(
            "시간 (분)",
            options=TIME_OPTIONS,
            default=[5, 10, 15],
            max_selections=4,
            label_visibility="collapsed"
        )

        st.divider()

        # 실행 버튼
        run_button = st.button(
            "🔍 아이소크론 생성",
            use_container_width=True,
            type="primary",
            disabled=not access_token or not selected_times
        )

        st.divider()
        st.caption("ℹ️ **Mapbox Isochrone API**")
        st.caption("• 월 100,000건 무료")
        st.caption("• 실시간 교통 정보 반영 가능")
        st.caption("• 빠른 응답 속도 (1~2초)")

    # 메인 영역
    if run_button and access_token and selected_times:
        profile_code = PROFILES[profile]

        try:
            with st.spinner("🌐 Mapbox API 호출 중..."):
                geojson = get_isochrone(
                    access_token=access_token,
                    lon=lon,
                    lat=lat,
                    profile=profile_code,
                    minutes=sorted(selected_times)
                )

            st.success(f"✅ {profile} 아이소크론 생성 완료!")

            # 범례 표시
            times_str = ", ".join([f"{t}분" for t in sorted(selected_times)])
            st.info(f"📊 표시된 영역: {times_str}")

            # 지도 표시
            m = create_map(lat, lon, geojson, selected_times)
            st_folium(m, width=None, height=600, use_container_width=True)

            # GeoJSON 다운로드
            with st.expander("📥 GeoJSON 데이터 보기"):
                st.json(geojson)

        except Exception as e:
            st.error(f"❌ 오류: {str(e)}")
            st.info("💡 Access Token이 올바른지 확인하세요")
    else:
        # 초기 상태
        if not access_token:
            st.info("👈 사이드바에서 Mapbox Access Token을 먼저 입력하세요")
        elif not selected_times:
            st.info("👈 시간을 최소 1개 이상 선택하세요")
        else:
            st.info("👈 설정을 완료하고 '아이소크론 생성' 버튼을 클릭하세요")

        # 기본 지도 표시
        m = create_map(lat, lon)
        st_folium(m, width=None, height=600, use_container_width=True)


if __name__ == "__main__":
    main()
