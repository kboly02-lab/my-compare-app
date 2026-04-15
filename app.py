import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 2. 스타일 설정
st.markdown("""
    <style>
    .filter-container { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ddd; }
    .excel-table { border-collapse: collapse; width: 100%; font-size: 11px; border: 2px solid #444; }
    .excel-table th, .excel-table td { border: 1px solid #ccc; padding: 5px 8px; text-align: left; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 150px; }
    .project-title { background-color: #4472c4; color: white; padding: 10px; border-radius: 5px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# 안전한 데이터 추출 함수
def get_val(df, row, col):
    try:
        if row < len(df) and col < len(df.columns):
            v = df.iloc[row, col]
            return str(v).strip() if pd.notna(v) else ""
    except:
        return ""
    return ""

def extract_num(val):
    try:
        # 숫자와 소수점만 남기고 제거
        n = re.sub(r'[^0-9.]', '', str(val).replace(',', ''))
        return float(n) if n else 0
    except:
        return 0

@st.cache_data
def load_data():
    # 파일명 리스트 (사용자가 올린 파일명 우선 순위)
    files = ["비교프로젝트_설비.xlsx - Sheet1.csv", "비교프로젝트_설비.csv"]
    for f in files:
        if os.path.exists(f):
            # 엑셀 파일 특성상 header 없이 전체를 읽어옴
            return pd.read_csv(f, header=None)
    return None

df = load_data()

if df is None:
    st.error("❌ '비교프로젝트_설비.xlsx - Sheet1.csv' 파일을 찾을 수 없습니다. 파일 이름을 확인해주세요.")
else:
    st.title("🏢 설비 비교 프로젝트 정밀 검색 시스템")
    
    # --- 검색 필터 UI ---
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: v_loc = st.selectbox("위치(지역)", ["전체", "서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "강원", "충남", "경남", "경북", "전남", "전북", "제주"])
    with c2: v_year = st.selectbox("년도(준공/입주)", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
    with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "EHP", "GHP"])
    with c4: v_unit = st.selectbox("세대수", ["전체", "300세대 미만", "300~500세대", "500~1000세대", "1000~2000세대", "2000세대 이상"])
    
    c5, c6, c7 = st.columns(3)
    with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링", "재개발", "재건축"])
    with c6: v_area = st.selectbox("연면적(평)", ["전체", "~3만", "3~5만", "5~10만", "10~20만", "20만~"])
    with c7: v_fire = st.selectbox("소방/성능위주", ["전체", "소방", "성능위주"])

    v_specs = st.multiselect("특화설비/특이사항 (포함 키워드)", ["우수", "중수", "연료전지", "지열", "정화조", "사우나", "음식물", "쓰레기", "수영장", "지하단차", "초고층", "준초고층", "지하철"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 조건에 맞는 프로젝트 검색", use_container_width=True):
        found_indices = []
        # D열(인덱스 3)부터 2칸씩(프로젝트/비고) 이동하며 탐색
        for j in range(3, len(df.columns), 2):
            name = get_val(df, 0, j)
            if not name or "Unnamed" in name or name == "": continue

            # 엑셀 구조 분석에 따른 정확한 좌표값 추출
            row_year = get_val(df, 4, j)
            row_hvac = get_val(df, 5, j)
            row_type = get_val(df, 6, j)
            row_fire_note = get_val(df, 6, j+1) # 건물유형 옆 비고란에 '성능위주' 등 기입됨
            
            # 세대수 합산 (아파트 7행 + 오피 8행)
            row_unit = extract_num(get_val(df, 7, j)) + extract_num(get_val(df, 8, j))
            
            # 연면적 (14행)
            row_area = extract_num(get_val(df, 14, j))
            
            # 특화 및 비고 (46행 ~ 50행 통합 검색)
            spec_notes = ""
            for r in range(45, 51):
                spec_notes += get_val(df, r, j) + get_val(df, r, j+1)

            # --- 필터링 로직 ---
            m_loc = (v_loc == "전체") or (v_loc in name)
            m_year = (v_year == "전체") or (v_year in row_year)
            m_hvac = (v_hvac == "전체") or (v_hvac in row_hvac)
            m_type = (v_type == "전체") or (v_type in row_type) or (v_type in name)
            m_fire = (v_fire == "전체") or (v_fire in row_fire_note) or (v_fire in row_type)
            
            m_unit = True
            if v_unit != "전체":
                if "300세대 미만" in v_unit: m_unit = row_unit < 300
                elif "300~500" in v_unit: m_unit = 300 <= row_unit <= 500
                elif "500~1000" in v_unit: m_unit = 500 <= row_unit <= 1000
                elif "1000~2000" in v_unit: m_unit = 1000 <= row_unit <= 2000
                else: m_unit = row_unit >= 2000

            m_area = True
            if v_area != "전체":
                if "~3만" in v_area: m_area = row_area <= 30000
                elif "3~5만" in v_area: m_area = 30001 <= row_area <= 50000
                elif "5~10만" in v_area: m_area = 50001 <= row_area <= 100000
                elif "10~20만" in v_area: m_area = 100001 <= row_area <= 200000
                else: m_area = row_area > 200000

            m_spec = all(s in spec_notes for s in v_specs)

            if all([m_loc, m_year, m_hvac, m_type, m_fire, m_unit, m_area, m_spec]):
                found_indices.append(j)

        # --- 결과 출력 ---
        if found_indices:
            st.success(f"🎯 검색 조건에 맞는 프로젝트를 {len(found_indices)}개 발견했습니다.")
            for col in found_indices:
                p_name = get_val(df, 0, col)
                with st.expander(f"📍 {p_name}"):
                    html = '<table class="excel-table">'
                    # 주요 정보 상단 배치 (1~55행 출력)
                    for r in range(min(60, len(df))):
                        h1 = get_val(df, r, 0) # 대분류
                        h2 = get_val(df, r, 1) # 소분류
                        d1 = get_val(df, r, col) # 데이터
                        d2 = get_val(df, r, col+1) # 비고
                        
                        # 내용이 있는 행만 표시
                        if h1 or h2 or d1 or d2:
                            html += f'<tr><td class="header-col">{h1}</td><td class="header-col">{h2}</td>'
                            html += f'<td>{d1}</td><td>{d2}</td></tr>'
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("🧐 해당 조건에 맞는 프로젝트가 없습니다. 필터를 조절해보세요.")
