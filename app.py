import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정 및 스타일
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")
st.markdown("""
    <style>
    .filter-container { background-color: #ffff00; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ccc; }
    .stMultiSelect label, .stSelectbox label { font-weight: bold; color: black; }
    .excel-table { border-collapse: collapse; width: 100%; font-size: 11px; border: 2px solid #444; }
    .excel-table th, .excel-table td { border: 1px solid #ccc; padding: 5px 8px; text-align: left; }
    .excel-table th { background-color: #f2f2f2; font-weight: bold; text-align: center; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 140px; }
    .project-title { background-color: #4472c4; color: white; font-weight: bold; text-align: center; font-size: 15px; height: 35px; }
    </style>
""", unsafe_allow_html=True)

# 2. 숫자 추출 함수 (범위 필터용)
def extract_num(val):
    if pd.isna(val): return 0
    try:
        n = str(val).replace(',', '')
        n = re.sub(r'[^0-9.]', '', n)
        return float(n) if n else 0
    except: return 0

# 3. 데이터 로드
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
    st.error("❌ '비교프로젝트_설비' 데이터 파일을 찾을 수 없습니다.")
else:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    # --- 검색 인터페이스 ---
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
    
    # 소방 선택지 고정
    fire_options = ["전체", "소방포함 / 성능위주", "소방포함 / 비성능위주", "소방제외 / 성능위주", "소방제외 / 비성능위주"]
    with c7: v_fire = st.selectbox("소방/성능위주설계", fire_options)

    # 중복 선택 가능 (AND 조건)
    with c8: v_specs = st.multiselect("특화설비", ["우수처리", "중수처리", "연료전지", "지열", "정화조", "사우나", "음식물", "쓰레기", "수영장", "주차", "없음"])
    with c9: v_notes = st.multiselect("특수사항", ["지하단차", "초고층", "준초고층", "진출입", "산악", "공항", "지하철", "없음"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 프로젝트 조회", use_container_width=True):
        found_indices = []
        # D열(3)부터 2칸씩 점프하여 프로젝트 단위 체크
        project_cols = [j for j in range(3, len(df.columns), 2)]

        for j in project_cols:
            p_name = str(df.iloc[0, j]) if pd.notna(df.iloc[0, j]) else ""
            if not p_name.strip() or "공사금액" in p_name: continue

            # [1] 기본 정보 (텍스트 포함)
            m_loc = (v_loc == "전체") or (v_loc in p_name)
            m_year = (v_year == "전체") or (v_year in str(df.iloc[3, j]))
            m_hvac = (v_hvac == "전체") or (v_hvac in str(df.iloc[4, j]))
            m_type = (v_type == "전체") or (v_type in str(df.iloc[5, j]))

            # [2] 세대수 합산 (7행 + 8행)
            u_val = extract_num(df.iloc[6, j]) + extract_num(df.iloc[7, j])
            m_unit = True
            if v_unit != "전체":
                if "100세대 미만" in v_unit: m_unit = u_val < 100
                elif "101~300" in v_unit: m_unit = 101 <= u_val <= 300
                elif "301~500" in v_unit: m_unit = 301 <= u_val <= 500
                elif "501~1000" in v_unit: m_unit = 501 <= u_val <= 1000
                elif "1001~2000" in v_unit: m_unit = 1001 <= u_val <= 2000
                elif "2001~3000" in v_unit: m_unit = 2001 <= u_val <= 3000
                elif "3001세대" in v_unit: m_unit = u_val >= 3001

            # [3] 연면적 (14행)
            a_val = extract_num(df.iloc[13, j])
            m_area = True
            if v_area != "전체":
                if "~30,000" in v_area: m_area = a_val <= 30000
                elif "30,001~50,000" in v_area: m_area = 30001 <= a_val <= 50000
                elif "50,001~70,000" in v_area: m_area = 50001 <= a_val <= 70000
                elif "70,001~100,000" in v_area: m_area = 70001 <= a_val <= 100000
                elif "100,001~200,000" in v_area: m_area = 100001 <= a_val <= 200000
                elif "200,001~300,000" in v_area: m_area = 200001 <= a_val <= 300000
                elif "300,001" in v_area: m_area = a_val > 300000

            # [4] 소방 (6행 비고란 j+1열) - 유연한 키워드 매칭
            f_txt = str(df.iloc[5, j+1]) if pd.notna(df.iloc[5, j+1]) else ""
            m_fire = True
            if v_fire != "전체":
                keys = [k.strip() for k in v_fire.split('/')]
                m_fire = all(k in f_txt for k in keys)

            # [5] 특화설비 (46행) - 선택된 모든 항목 포함 (AND)
            s_txt = str(df.iloc[45, j]) if pd.notna(df.iloc[45, j]) else ""
            m_spec = True
            if v_specs:
                if "없음" in v_specs: m_spec = not s_txt.strip()
                else: m_spec = all(s in s_txt for s in v_specs)

            # [6] 특수사항 (48행 데이터+비고 병합 확인)
            n_txt = str(df.iloc[47, j]) + str(df.iloc[47, j+1])
            m_note = True
            if v_notes:
                if "없음" in v_notes: m_note = not n_txt.strip()
                else: m_note = all(n in n_txt for n in v_notes)

            # --- 최종 판정 ---
            if all([m_loc, m_year, m_hvac, m_type, m_unit, m_area, m_fire, m_spec, m_note]):
                found_indices.append(j)

        # 결과 출력
        if found_indices:
            st.success(f"🎯 조건에 맞는 프로젝트를 {len(found_indices)}개 찾았습니다.")
            for col in found_indices:
                with st.expander(f"📌 {df.iloc[0, col]} 상세 데이터"):
                    html = '<table class="excel-table">'
                    html += f'<tr><th colspan="4" class="project-title">{df.iloc[0, col]}</th></tr>'
                    html += '<tr><th>구분1</th><th>구분2</th><th>내용</th><th>비고</th></tr>'
                    for r in range(min(49, len(df))):
                        v1, v2 = df.iloc[r, 0], df.iloc[r, 1]
                        v3, v4 = df.iloc[r, col], df.iloc[r, col+1]
                        html += f'<tr><td class="header-col">{v1 if pd.notna(v1) else ""}</td>'
                        html += f'<td class="header-col">{v2 if pd.notna(v2) else ""}</td>'
                        html += f'<td>{v3 if pd.notna(v3) else ""}</td>'
                        html += f'<td>{v4 if pd.notna(v4) else ""}</td></tr>'
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("🧐 일치하는 현장이 없습니다. 조건을 변경해보세요.")
