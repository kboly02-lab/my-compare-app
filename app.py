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
    .excel-table th { background-color: #f2f2f2; font-weight: bold; text-align: center; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 140px; }
    .project-title { background-color: #4472c4; color: white; font-weight: bold; text-align: center; font-size: 15px; height: 35px; }
    </style>
""", unsafe_allow_html=True)

# 데이터 안전 추출 함수
def get_val(df, row, col):
    if row < len(df) and col < len(df.columns):
        v = df.iloc[row, col]
        return str(v).strip() if pd.notna(v) else ""
    return ""

def extract_num(val):
    try:
        n = re.sub(r'[^0-9.]', '', str(val).replace(',', ''))
        return float(n) if n else 0
    except: return 0

@st.cache_data
def load_data():
    files = ["비교프로젝트_설비.xlsx - Sheet1.csv", "비교프로젝트_설비.csv", "비교프로젝트_설비.xlsx"]
    for f in files:
        if os.path.exists(f):
            try:
                if f.endswith('.csv'): return pd.read_csv(f, header=None)
                else: return pd.read_excel(f, header=None)
            except: continue
    return None

df = load_data()

if df is None:
    st.error("❌ 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
else:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    # --- 검색 필터 UI ---
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: v_loc = st.selectbox("위치", ["전체", "서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "강원"])
    with c2: v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
    with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방"])
    with c4: v_unit = st.selectbox("세대수", ["전체", "100세대 미만", "101~300세대", "301~500세대", "501~1000세대", "1001~2000세대", "2001~3000세대", "3001세대 이상"])
    
    c5, c6, c7 = st.columns(3)
    with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링"])
    with c6: v_area = st.selectbox("연면적(평)", ["전체", "~3만", "3~5만", "5~7만", "7~10만", "10~20만", "20만~"])
    with c7: v_fire = st.selectbox("소방/성능위주", ["전체", "소방포함", "성능위주"])

    v_specs = st.multiselect("특화설비", ["우수처리", "중수처리", "연료전지", "지열", "정화조", "사우나", "음식물", "쓰레기", "수영장"])
    v_notes = st.multiselect("특수사항", ["지하단차", "초고층", "준초고층", "진출입", "산악", "공항", "지하철"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 프로젝트 조회", use_container_width=True):
        found_indices = []
        # D열(3)부터 2칸씩 점프하며 프로젝트 탐색
        for j in range(3, len(df.columns), 2):
            name = get_val(df, 0, j)
            if not name or "공사금액" in name: continue

            # 데이터 추출 (행 번호는 0부터 시작 기준)
            row_year = get_val(df, 3, j)
            row_hvac = get_val(df, 4, j)
            row_type = get_val(df, 5, j)
            row_fire_note = get_val(df, 5, j+1) # 비고란 소방 확인
            row_unit = extract_num(get_val(df, 6, j)) + extract_num(get_val(df, 7, j))
            row_area = extract_num(get_val(df, 13, j))
            row_spec = get_val(df, 45, j)
            row_note = get_val(df, 47, j) + get_val(df, 47, j+1)

            # 필터 체크
            m_loc = (v_loc == "전체") or (v_loc in name)
            m_year = (v_year == "전체") or (v_year in row_year)
            m_hvac = (v_hvac == "전체") or (v_hvac in row_hvac)
            m_type = (v_type == "전체") or (v_type in row_type)
            m_fire = (v_fire == "전체") or (v_fire in row_fire_note) or (v_fire in row_type)
            
            m_unit = True
            if v_unit != "전체":
                if "100세대 미만" in v_unit: m_unit = row_unit < 100
                elif "101~300" in v_unit: m_unit = 101 <= row_unit <= 300
                elif "301~500" in v_unit: m_unit = 301 <= row_unit <= 500
                elif "501~1000" in v_unit: m_unit = 501 <= row_unit <= 1000
                elif "1001~2000" in v_unit: m_unit = 1001 <= row_unit <= 2000
                elif "2001~3000" in v_unit: m_unit = 2001 <= row_unit <= 3000
                else: m_unit = row_unit >= 3001

            m_area = True
            if v_area != "전체":
                if "~3만" in v_area: m_area = row_area <= 30000
                elif "3~5만" in v_area: m_area = 30001 <= row_area <= 50000
                elif "5~7만" in v_area: m_area = 50001 <= row_area <= 70000
                elif "7~10만" in v_area: m_area = 70001 <= row_area <= 100000
                elif "10~20만" in v_area: m_area = 100001 <= row_area <= 200000
                else: m_area = row_area > 200000

            m_spec = all(s in row_spec for s in v_specs)
            m_note = all(n in row_note for n in v_notes)

            if all([m_loc, m_year, m_hvac, m_type, m_fire, m_unit, m_area, m_spec, m_note]):
                found_indices.append(j)

        # 결과 출력
        if found_indices:
            st.success(f"🎯 {len(found_indices)}개의 프로젝트를 찾았습니다.")
            for col in found_indices:
                with st.expander(f"📌 {df.iloc[0, col]}"):
                    html = '<table class="excel-table">'
                    for r in range(min(50, len(df))):
                        h1, h2 = get_val(df, r, 0), get_val(df, r, 1)
                        d1, d2 = get_val(df, r, col), get_val(df, r, col+1)
                        html += f'<tr><td class="header-col">{h1}</td><td class="header-col">{h2}</td>'
                        html += f'<td>{d1}</td><td>{d2}</td></tr>'
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("🧐 조건에 맞는 프로젝트가 없습니다.")
