"""
Isochrone Map Viewer + Naver POI Search
특정 좌표에서 도보/차량으로 일정 시간 내 도달 가능한 영역을 시각화하고
해당 영역 내 POI를 검색하는 대시보드

- API 키 불필요 (OpenStreetMap 데이터 사용) - 등시선 계산
- 네이버 검색 API 사용 - POI 검색
- Carto Positron 스타일 지도 (밝은 회색)
"""

import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
from shapely.geometry import MultiPoint, Point
import requests
import pandas as pd
import time
from typing import Optional, List, Dict

# 페이지 설정
st.set_page_config(
    page_title="Isochrone + POI Map",
    page_icon="🗺️",
    layout="wide"
)

# 상수 정의
WALK_SPEED = 1.25  # m/s (약 4.5 km/h)
TIME_OPTIONS = [5, 10, 15, 20, 30, 60]  # 분 단위

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
    20: {"walk": 2500, "drive": 12000},
    30: {"walk": 3000, "drive": 18000},
    60: {"walk": 6000, "drive": 35000}
}

# 시간별 색상 (그라데이션)
TIME_COLORS = {
    5: '#2ecc71',    # 녹색
    10: '#3498db',   # 파랑
    15: '#9b59b6',   # 보라
    20: '#e67e22',   # 주황
    30: '#e74c3c',   # 빨강
    60: '#c0392b'    # 진빨강
}

# POI 카테고리 정의
POI_CATEGORIES = {
    "대형마트": {"query": "대형마트", "color": "blue"},
    "편의점": {"query": "편의점", "color": "lightblue"},
    "어린이집": {"query": "어린이집", "color": "pink"},
    "유치원": {"query": "유치원", "color": "lightpink"},
    "학교": {"query": "학교", "color": "darkblue"},
    "입시학원": {"query": "입시학원", "color": "purple"},
    "일반학원": {"query": "학원", "color": "darkpurple"},
    "주차장": {"query": "주차장", "color": "gray"},
    "주유소": {"query": "주유소", "color": "orange"},
    "충전소": {"query": "전기차충전소", "color": "green"},
    "지하철역": {"query": "지하철역", "color": "darkgreen"},
    "은행": {"query": "은행", "color": "darkblue"},
    "문화시설": {"query": "문화시설", "color": "red"},
    "중개업소": {"query": "부동산", "color": "beige"},
    "공공기관": {"query": "공공기관", "color": "lightgray"},
    "관광명소": {"query": "관광명소", "color": "cadetblue"},
    "숙박": {"query": "호텔", "color": "darkred"},
    "음식점": {"query": "음식점", "color": "orange"},
    "카페": {"query": "카페", "color": "lightred"},
    "병원": {"query": "병원", "color": "red"},
    "약국": {"query": "약국", "color": "lightgreen"},
    "소매(의류/신발)": {"query": "의류매장", "color": "pink"}
}


def init_session_state():
    """세션 상태 초기화"""
    if 'clicked_lat' not in st.session_state:
        st.session_state.clicked_lat = 37.5665
    if 'clicked_lon' not in st.session_state:
        st.session_state.clicked_lon = 126.9780
    if 'isochrone_polygons' not in st.session_state:
        st.session_state.isochrone_polygons = {}
    if 'poi_data' not in st.session_state:
        st.session_state.poi_data = []
    if 'address_info' not in st.session_state:
        st.session_state.address_info = ""


@st.cache_data(ttl=3600, show_spinner=False)
def get_graph(lat: float, lon: float, dist: int, network_type: str):
    """도로 네트워크 다운로드 (캐싱 적용)"""
    return ox.graph_from_point(
        center_point=(lat, lon),
        dist=dist,
        network_type=network_type
    )


def add_travel_time(G, mode: str):
    """그래프 엣지에 이동 시간 추가"""
    if mode == "walk":
        for u, v, data in G.edges(data=True):
            data['travel_time'] = data['length'] / WALK_SPEED
    else:
        G = ox.routing.add_edge_speeds(G)
        G = ox.routing.add_edge_travel_times(G)
    return G


def calculate_isochrone(G, lat: float, lon: float, trip_time_seconds: float):
    """아이소크론 폴리곤 계산"""
    center_node = ox.nearest_nodes(G, lon, lat)

    subgraph = nx.ego_graph(
        G,
        center_node,
        radius=trip_time_seconds,
        distance='travel_time'
    )

    if len(subgraph.nodes()) < 3:
        return None

    node_coords = [
        (G.nodes[node]['x'], G.nodes[node]['y'])
        for node in subgraph.nodes()
    ]

    points = MultiPoint([Point(coord) for coord in node_coords])
    isochrone_polygon = points.convex_hull

    return isochrone_polygon


@st.cache_data(ttl=3600)
def reverse_geocode(lat: float, lon: float) -> Dict:
    """좌표 → 주소 변환 (Nominatim 사용, 무료)"""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
            "accept-language": "ko"
        }
        headers = {"User-Agent": "IsochronePOIMap/1.0"}

        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            return {
                "full": data.get("display_name", ""),
                "city": address.get("city", address.get("county", "")),
                "district": address.get("borough", address.get("suburb", address.get("neighbourhood", ""))),
                "dong": address.get("quarter", address.get("suburb", ""))
            }
    except Exception as e:
        st.warning(f"주소 변환 오류: {e}")
    return {}


def search_naver_local(query: str, client_id: str, client_secret: str,
                       display: int = 5, start: int = 1) -> List[Dict]:
    """네이버 지역 검색 API 호출"""
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": "random"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('items', [])
        elif response.status_code == 429:
            st.warning("API 호출 한도 초과. 잠시 후 다시 시도하세요.")
        else:
            st.warning(f"API 오류: {response.status_code}")
    except Exception as e:
        st.error(f"검색 오류: {str(e)}")
    return []


def convert_naver_coords(mapx: str, mapy: str) -> tuple:
    """네이버 좌표 → WGS84 변환"""
    try:
        # 네이버 API는 Katec 좌표계 사용 (1/10,000,000 단위)
        x = int(mapx)
        y = int(mapy)
        lon = x / 10000000
        lat = y / 10000000
        return lat, lon
    except:
        return None, None


def is_point_in_polygon(lat: float, lon: float, polygon) -> bool:
    """점이 폴리곤 내부에 있는지 확인"""
    if polygon is None:
        return True  # 폴리곤 없으면 모두 통과
    point = Point(lon, lat)
    return polygon.contains(point)


def search_poi_with_location(category: str, location_name: str,
                             client_id: str, client_secret: str,
                             polygon=None) -> List[Dict]:
    """지역명 기반 POI 검색 및 필터링"""
    query_base = POI_CATEGORIES[category]["query"]
    all_results = []
    seen_titles = set()

    # 검색어 조합 (지역명 + 카테고리)
    search_queries = [
        f"{location_name} {query_base}",
        f"{query_base} {location_name}"
    ]

    for query in search_queries:
        # 여러 페이지 검색 (최대 20개)
        for start in [1, 6, 11, 16]:
            items = search_naver_local(query, client_id, client_secret,
                                       display=5, start=start)
            for item in items:
                title = item.get('title', '').replace('<b>', '').replace('</b>', '')

                # 중복 제거
                if title in seen_titles:
                    continue
                seen_titles.add(title)

                # 좌표 변환
                lat, lon = convert_naver_coords(
                    item.get('mapx', '0'),
                    item.get('mapy', '0')
                )

                if lat and lon:
                    # 등시선 내 필터링
                    if is_point_in_polygon(lat, lon, polygon):
                        item['lat'] = lat
                        item['lon'] = lon
                        item['category'] = category
                        item['title_clean'] = title
                        all_results.append(item)

            time.sleep(0.1)  # API 호출 간격

    return all_results


def create_map(lat: float, lon: float, isochrone_polygons: Dict = None,
               poi_list: List[Dict] = None):
    """Folium 지도 생성"""
    m = folium.Map(
        location=[lat, lon],
        tiles="CartoDB Positron",
        zoom_start=14
    )

    # 중심점 마커
    folium.Marker(
        location=[lat, lon],
        popup="출발점",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # 등시선 폴리곤 (큰 시간부터)
    if isochrone_polygons:
        for time_min in sorted(isochrone_polygons.keys(), reverse=True):
            polygon = isochrone_polygons[time_min]
            if polygon is not None:
                color = TIME_COLORS.get(time_min, '#3388ff')
                folium.GeoJson(
                    polygon.__geo_interface__,
                    style_function=lambda x, c=color: {
                        'fillColor': c,
                        'color': c,
                        'weight': 2,
                        'fillOpacity': 0.2
                    },
                    tooltip=f"{time_min}분 도달 영역"
                ).add_to(m)

    # POI 마커
    if poi_list:
        for poi in poi_list:
            if 'lat' in poi and 'lon' in poi:
                category = poi.get('category', '')
                cat_info = POI_CATEGORIES.get(category, {"color": "blue"})
                title = poi.get('title_clean', poi.get('title', ''))

                folium.Marker(
                    location=[poi['lat'], poi['lon']],
                    popup=folium.Popup(
                        f"<b>{title}</b><br>"
                        f"📍 {poi.get('address', '')}<br>"
                        f"📞 {poi.get('telephone', '')}",
                        max_width=300
                    ),
                    tooltip=f"[{category}] {title}",
                    icon=folium.Icon(color=cat_info['color'], icon='info-sign')
                ).add_to(m)

    return m


def poi_to_dataframe(poi_list: List[Dict]) -> pd.DataFrame:
    """POI 리스트를 DataFrame으로 변환"""
    if not poi_list:
        return pd.DataFrame()

    data = []
    for poi in poi_list:
        data.append({
            '카테고리': poi.get('category', ''),
            '이름': poi.get('title_clean', ''),
            '주소': poi.get('address', ''),
            '도로명주소': poi.get('roadAddress', ''),
            '전화번호': poi.get('telephone', ''),
            '위도': poi.get('lat', ''),
            '경도': poi.get('lon', ''),
            '링크': poi.get('link', '')
        })

    return pd.DataFrame(data)


def main():
    init_session_state()

    # 제목
    st.title("🗺️ Isochrone + POI Map")
    st.caption("등시선도 생성 & 네이버 POI 검색 대시보드")

    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")

        # 네이버 API 설정
        with st.expander("🔑 네이버 API 설정", expanded=False):
            naver_client_id = st.text_input("Client ID", type="password")
            naver_client_secret = st.text_input("Client Secret", type="password")
            st.caption("네이버 개발자센터에서 발급받은 검색 API 키")

        st.divider()

        # 좌표 입력
        st.subheader("📍 좌표 입력")
        col1, col2 = st.columns(2)
        with col1:
            input_lat = st.number_input(
                "위도",
                min_value=-90.0,
                max_value=90.0,
                value=st.session_state.clicked_lat,
                step=0.0001,
                format="%.4f"
            )
        with col2:
            input_lon = st.number_input(
                "경도",
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.clicked_lon,
                step=0.0001,
                format="%.4f"
            )

        st.caption("💡 지도 클릭으로도 좌표 선택 가능")

        # 현재 주소 표시
        if st.session_state.address_info:
            st.info(f"📍 {st.session_state.address_info}")

        st.divider()

        # 이동 수단
        st.subheader("🚶 이동 수단")
        transport = st.radio(
            "이동 수단",
            options=list(TRANSPORT_MODES.keys()),
            index=0,
            label_visibility="collapsed"
        )

        st.divider()

        # 시간 선택 (다중)
        st.subheader("⏱️ 시간 선택 (다중 가능)")
        selected_times = st.multiselect(
            "이동 시간",
            options=TIME_OPTIONS,
            default=[15],
            format_func=lambda x: f"{x}분"
        )

        st.divider()

        # 등시선 생성 버튼
        run_isochrone = st.button(
            "🔍 등시선 생성",
            use_container_width=True,
            type="primary"
        )

        st.divider()

        # POI 카테고리
        st.subheader("🏪 POI 카테고리")
        selected_categories = st.multiselect(
            "검색할 POI",
            options=list(POI_CATEGORIES.keys()),
            default=[],
            placeholder="카테고리 선택..."
        )

        # POI 검색 버튼
        api_ready = naver_client_id and naver_client_secret
        search_poi = st.button(
            "🔎 POI 검색",
            use_container_width=True,
            disabled=not (api_ready and selected_categories)
        )

        if not api_ready:
            st.caption("⚠️ POI 검색: 네이버 API 키 필요")

    # 메인 영역
    col_map, col_data = st.columns([2, 1])

    with col_map:
        current_lat = input_lat
        current_lon = input_lon

        # 등시선 생성
        if run_isochrone and selected_times:
            mode_config = TRANSPORT_MODES[transport]
            network_type = mode_config["network_type"]
            max_time = max(selected_times)
            dist = RADIUS_BY_TIME[max_time][network_type]

            try:
                with st.spinner("🌐 도로 네트워크 다운로드 중..."):
                    G = get_graph(current_lat, current_lon, dist, network_type)

                with st.spinner("🔧 이동 시간 계산 중..."):
                    G = add_travel_time(G, network_type)

                with st.spinner("📐 등시선 계산 중..."):
                    polygons = {}
                    for time_min in selected_times:
                        trip_time_seconds = time_min * 60
                        isochrone = calculate_isochrone(G, current_lat, current_lon, trip_time_seconds)
                        if isochrone is not None:
                            polygons[time_min] = isochrone
                    st.session_state.isochrone_polygons = polygons

                # 주소 정보 가져오기
                with st.spinner("📍 주소 확인 중..."):
                    addr = reverse_geocode(current_lat, current_lon)
                    if addr:
                        location_parts = [p for p in [addr.get('city'), addr.get('district'), addr.get('dong')] if p]
                        st.session_state.address_info = " ".join(location_parts) if location_parts else addr.get('full', '')[:50]

                if polygons:
                    time_str = ', '.join([f'{t}분' for t in sorted(selected_times)])
                    st.success(f"✅ {transport} 등시선 생성 완료! ({time_str})")
                else:
                    st.warning("⚠️ 등시선 생성 실패. 다른 위치를 시도해보세요.")

            except Exception as e:
                st.error(f"❌ 오류: {str(e)}")

        # POI 검색
        if search_poi and selected_categories:
            # 지역명 가져오기
            if not st.session_state.address_info:
                with st.spinner("📍 주소 확인 중..."):
                    addr = reverse_geocode(current_lat, current_lon)
                    if addr:
                        location_parts = [p for p in [addr.get('city'), addr.get('district'), addr.get('dong')] if p]
                        st.session_state.address_info = " ".join(location_parts) if location_parts else ""

            location_name = st.session_state.address_info or "서울"

            # 가장 큰 등시선 폴리곤
            largest_polygon = None
            if st.session_state.isochrone_polygons:
                max_time = max(st.session_state.isochrone_polygons.keys())
                largest_polygon = st.session_state.isochrone_polygons[max_time]

            with st.spinner(f"🔍 '{location_name}' 주변 POI 검색 중..."):
                all_poi = []
                progress = st.progress(0)

                for i, category in enumerate(selected_categories):
                    results = search_poi_with_location(
                        category, location_name,
                        naver_client_id, naver_client_secret,
                        largest_polygon
                    )
                    all_poi.extend(results)
                    progress.progress((i + 1) / len(selected_categories))

                progress.empty()
                st.session_state.poi_data = all_poi

                if all_poi:
                    st.success(f"✅ {len(all_poi)}개 POI 발견!")
                else:
                    st.warning("⚠️ 해당 영역에 POI가 없습니다. 등시선을 먼저 생성하거나 다른 카테고리를 선택해보세요.")

        # 지도 생성
        m = create_map(
            current_lat, current_lon,
            st.session_state.isochrone_polygons,
            st.session_state.poi_data
        )

        # 지도 표시 (클릭 이벤트)
        map_data = st_folium(
            m,
            width=None,
            height=600,
            use_container_width=True,
            returned_objects=["last_clicked"]
        )

        # 지도 클릭 시 좌표 업데이트
        if map_data and map_data.get('last_clicked'):
            clicked = map_data['last_clicked']
            new_lat = clicked['lat']
            new_lon = clicked['lng']
            if (abs(new_lat - st.session_state.clicked_lat) > 0.0001 or
                abs(new_lon - st.session_state.clicked_lon) > 0.0001):
                st.session_state.clicked_lat = new_lat
                st.session_state.clicked_lon = new_lon
                st.session_state.address_info = ""  # 주소 리셋
                st.rerun()

    with col_data:
        st.subheader("📊 POI 데이터")

        if st.session_state.poi_data:
            df = poi_to_dataframe(st.session_state.poi_data)

            # 통계
            st.metric("총 POI 수", len(df))

            # 카테고리별 개수
            if '카테고리' in df.columns and len(df) > 0:
                cat_counts = df['카테고리'].value_counts()
                with st.expander("📈 카테고리별 개수", expanded=True):
                    for cat, count in cat_counts.items():
                        color = POI_CATEGORIES.get(cat, {}).get('color', 'gray')
                        st.write(f"• **{cat}**: {count}개")

            st.divider()

            # 데이터 테이블
            st.dataframe(
                df[['카테고리', '이름', '주소', '전화번호']],
                use_container_width=True,
                height=250
            )

            # CSV 다운로드
            st.divider()
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f"poi_{st.session_state.address_info.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("👈 등시선을 생성하고 POI 카테고리를 선택해서 검색하세요")

        # 등시선 범례
        if st.session_state.isochrone_polygons:
            st.divider()
            st.subheader("🎨 등시선 범례")
            for time_min in sorted(st.session_state.isochrone_polygons.keys()):
                color = TIME_COLORS.get(time_min, '#3388ff')
                st.markdown(
                    f'<span style="color:{color}; font-size:20px;">●</span> {time_min}분',
                    unsafe_allow_html=True
                )


if __name__ == "__main__":
    main()
