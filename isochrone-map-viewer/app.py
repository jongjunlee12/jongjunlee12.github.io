"""
Isochrone Map Viewer
특정 좌표에서 도보/차량으로 일정 시간 내 도달 가능한 영역을 시각화하는 도구

- API 키 불필요 (OpenStreetMap 데이터 사용)
- 로컬에서 아이소크론 계산 (OSMnx + NetworkX)
- Carto Positron 스타일 지도
"""

import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
from shapely.geometry import MultiPoint, Point

# 페이지 설정
st.set_page_config(
    page_title="Isochrone Map Viewer",
    page_icon="🗺️",
    layout="wide"
)

# 상수 정의
WALK_SPEED = 1.25  # m/s (약 4.5 km/h)
TIME_OPTIONS = [5, 10, 15, 30, 60]  # 분 단위

# 이동 수단별 설정
TRANSPORT_MODES = {
    "도보 🚶": {"network_type": "walk", "use_osmnx_speed": False},
    "차량 🚗": {"network_type": "drive", "use_osmnx_speed": True}
}

# 시간별 권장 다운로드 반경 (미터)
RADIUS_BY_TIME = {
    5: {"walk": 1000, "drive": 4000},
    10: {"walk": 1500, "drive": 7000},
    15: {"walk": 2000, "drive": 10000},
    30: {"walk": 3000, "drive": 18000},
    60: {"walk": 6000, "drive": 35000}
}


@st.cache_data(ttl=3600, show_spinner=False)
def get_graph(lat: float, lon: float, dist: int, network_type: str):
    """도로 네트워크 다운로드 (캐싱 적용)"""
    return ox.graph_from_point(
        center_point=(lat, lon),  # 주의: (lat, lon) 순서
        dist=dist,
        network_type=network_type
    )


def add_travel_time(G, mode: str):
    """그래프 엣지에 이동 시간 추가"""
    if mode == "walk":
        # 도보: 4.5 km/h = 1.25 m/s
        for u, v, data in G.edges(data=True):
            data['travel_time'] = data['length'] / WALK_SPEED
    else:
        # 차량: OSMnx 내장 함수 사용 (도로 제한속도 기반)
        G = ox.routing.add_edge_speeds(G)
        G = ox.routing.add_edge_travel_times(G)
    return G


def calculate_isochrone(G, lat: float, lon: float, trip_time_seconds: float):
    """아이소크론 폴리곤 계산"""
    # 시작점에서 가장 가까운 노드 찾기
    # 주의: nearest_nodes는 (lon, lat) 순서 (X, Y 좌표계)
    center_node = ox.nearest_nodes(G, lon, lat)

    # 지정 시간 내 도달 가능한 서브그래프
    subgraph = nx.ego_graph(
        G,
        center_node,
        radius=trip_time_seconds,
        distance='travel_time'
    )

    # 노드가 부족하면 폴리곤 생성 불가
    if len(subgraph.nodes()) < 3:
        return None

    # 도달 가능 노드들의 좌표 추출
    node_coords = [
        (G.nodes[node]['x'], G.nodes[node]['y'])
        for node in subgraph.nodes()
    ]

    # Convex Hull로 폴리곤 생성
    points = MultiPoint([Point(coord) for coord in node_coords])
    isochrone_polygon = points.convex_hull

    return isochrone_polygon


def create_map(lat: float, lon: float, isochrone_polygon=None):
    """Folium 지도 생성"""
    m = folium.Map(
        location=[lat, lon],
        tiles="CartoDB Positron",  # Carto Positron 스타일 (밝은 회색)
        zoom_start=14
    )

    # 중심점 마커 추가
    folium.Marker(
        location=[lat, lon],
        popup="출발점",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # 아이소크론 폴리곤 추가
    if isochrone_polygon is not None:
        folium.GeoJson(
            isochrone_polygon.__geo_interface__,
            style_function=lambda x: {
                'fillColor': '#3388ff',
                'color': '#3388ff',
                'weight': 2,
                'fillOpacity': 0.3
            },
            tooltip="도달 가능 영역"
        ).add_to(m)

    return m


def main():
    # 제목
    st.title("🗺️ Isochrone Map Viewer")
    st.caption("특정 위치에서 일정 시간 내 도달 가능한 영역을 시각화합니다")

    # 사이드바: 입력 컨트롤
    with st.sidebar:
        st.header("📍 설정")

        # 좌표 입력
        st.subheader("좌표 입력")
        lat = st.number_input(
            "위도 (Latitude)",
            min_value=-90.0,
            max_value=90.0,
            value=37.5665,  # 서울시청 기본값
            step=0.0001,
            format="%.4f"
        )
        lon = st.number_input(
            "경도 (Longitude)",
            min_value=-180.0,
            max_value=180.0,
            value=126.9780,  # 서울시청 기본값
            step=0.0001,
            format="%.4f"
        )

        st.divider()

        # 이동 수단 선택
        st.subheader("🚶 이동 수단")
        transport = st.radio(
            "이동 수단 선택",
            options=list(TRANSPORT_MODES.keys()),
            index=0,
            label_visibility="collapsed"
        )

        st.divider()

        # 시간 선택
        st.subheader("⏱️ 시간 선택")
        trip_time = st.selectbox(
            "이동 시간 (분)",
            options=TIME_OPTIONS,
            index=2,  # 기본값: 15분
            format_func=lambda x: f"{x}분"
        )

        st.divider()

        # 실행 버튼
        run_button = st.button(
            "🔍 아이소크론 생성",
            use_container_width=True,
            type="primary"
        )

        # 정보 표시
        st.divider()
        st.caption("ℹ️ **정보**")
        st.caption("• API 키 불필요")
        st.caption("• OpenStreetMap 데이터 사용")
        st.caption("• 첫 실행 시 10~30초 소요")

    # 메인 영역: 지도 표시
    if run_button:
        mode_config = TRANSPORT_MODES[transport]
        network_type = mode_config["network_type"]

        # 시간에 따른 반경 설정
        dist = RADIUS_BY_TIME[trip_time][network_type]

        try:
            with st.spinner("🌐 도로 네트워크 다운로드 중..."):
                G = get_graph(lat, lon, dist, network_type)

            with st.spinner("🔧 이동 시간 계산 중..."):
                G = add_travel_time(G, network_type)

            with st.spinner("📐 아이소크론 계산 중..."):
                trip_time_seconds = trip_time * 60  # 분 → 초
                isochrone = calculate_isochrone(G, lat, lon, trip_time_seconds)

            if isochrone is None:
                st.warning("⚠️ 도달 가능한 영역이 너무 작습니다. 시간을 늘려보세요.")
                m = create_map(lat, lon)
            else:
                st.success(f"✅ {transport} {trip_time}분 아이소크론 생성 완료!")
                m = create_map(lat, lon, isochrone)

            # 지도 표시
            st_folium(m, width=None, height=600, use_container_width=True)

        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다: {str(e)}")
            st.info("💡 인터넷 연결을 확인하거나, 다른 좌표를 시도해보세요.")
    else:
        # 초기 상태: 빈 지도 표시
        st.info("👈 사이드바에서 좌표와 조건을 설정한 후 '아이소크론 생성' 버튼을 클릭하세요.")
        m = create_map(lat, lon)
        st_folium(m, width=None, height=600, use_container_width=True)


if __name__ == "__main__":
    main()
