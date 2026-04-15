import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 2. 스타일 설정
st.markdown("""
    <style>
    .filter-container { background-color: #ffff00; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ccc; }
    .excel-table { border-collapse: collapse; width: 100%; font-size: 11px; border: 2px solid #444; }
    .excel-table th, .excel-table td { border: 1px solid #ccc; padding: 5px 8px; text-align: left; }
    .excel-table th { background-color: #f2f2f2; font-weight: bold; text-align: center; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 140px; }
    .project-title { background-color: #4472c4; color: white; font-weight: bold; text-align: center; font-size: 15px; height: 35px; }
    </style>
""", unsafe_allow_html=True)

# 3. 유틸리티 함수
def extract_num(val):
    if pd.isna(val): return 0
    try:
        n = str(val).replace(',', '')
        n = re.sub(r'[^0-9.]', '', n)
        return float(n) if n else 0
    except: return 0

@st.cache_data
def load_data():
    file_names = ["비교프로젝트_설비.xlsx - Sheet1.csv", "비교프로젝트_설비.csv", "비교프로젝트_설비.xlsx"]
    for f in file_names:
        if os.path.exists(f):
            try:
                if f.endswith('.csv'): return pd.read_csv(f, header=None)
                else: return pd.read_excel(f, header=None)
            except: continue
    return None

df = load_data()

if df is None:
    st.error("❌ 데이터 파일을 찾을 수 없습니다.")
else:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.write("### 🔍 검색 조건 설정")
    
    c1, c2, c3, c4 = st.columns(4)
    c5, c6, c7 = st.columns(3)
    c8, c9 = st.columns(2)

    with c1: v_loc = st.selectbox("위치", ["전체", "서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "충청", "전라", "경상", "강원"])
    with c2: v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
    with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "기타"])
    with c4: v_unit = st.selectbox("세대수", ["전체", "100세대 미만", "101~300세대", "301~500세대", "501~1000세대", "1001~2000세대", "2001~3000세대", "3001세대 이상"])
    with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링", "일반건축물"])
    with c6: v_area = st.selectbox("연면적", ["전체", "~30,000평", "30,001~50,000평", "50,001~70,000평", "70,001~100,000평", "100,001~200,000평", "200,001~300,000평", "300,001평~"])
    
    # 소방 선택지 (데이터의 '성능위주설계' 포함 여부를 확인하기 위해 키워드 중심으로 구성)
    fire_options = ["전체", "소방포함 / 성능위주", "소방포함 / 비성능위주", "소방제외 / 성능위주", "소방제외 / 비성능위주"]
    with c7: v_fire = st.selectbox("소방/성능위주설계", fire_options)

    with c8: v_specs = st.multiselect("특화설비", ["우수처리", "중수처리", "연료전지", "지열", "정화조", "사우나", "음식물", "쓰레기", "수영장", "주차", "없음"])
    with c9: v_notes = st.multiselect("특수사항", ["지하단차", "초고층", "준초고층", "진출입", "산악", "공항", "지하철", "없음"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 프로젝트 조회", use_container_width=True):
        found_indices = []
        # 프로젝트 열: D, F, H... (인덱스 3, 5, 7...)
        project_cols = [j for j in range(3, len(df.columns), 2)]

        for j in project_cols:
            # 1행 프로젝트명
            p_name = str(df.iloc[0, j]) if pd.notna(df.iloc[0, j]) else ""
            if not p_name.strip() or "공사금액" in p_name: continue

            # --- 필터 로직 (전부 포함 여부로 체크) ---
            m_loc = (v_loc == "전체") or (v_loc in p_name)
            m_year = (v_year == "전체") or (v_year in str(df.iloc[3, j]))
            m_hvac = (v_hvac == "전체") or (v_hvac in str(df.iloc[4, j]))
            m_type = (v_type == "전체") or (v_type in str(df.iloc[5, j]))

            # 세대수 합산
            u_val = extract_num(df.iloc[6, j]) + extract_num(df.iloc[7, j])
            m_unit = True
            if v_unit != "전체":
                if "100세대 미만" in v_unit: m_unit = u_val < 100
                elif "101~300" in v_unit: m_unit = 101 <= u_val <= 300
                elif "301~500" in v_unit: m_unit = 301 <= u_val <= 500
                elif "501~1000" in v_unit: m_unit = 501 <= u_val <= 1000
                elif "1001~2000" in v_unit: m_unit = 1001 <= u_val <= 2000
                elif "2001~3000" in v_unit: m_unit = 2001 <= u_val <= 3000
                elif "30
