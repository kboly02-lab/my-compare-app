import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")
st.markdown("""
    <style>
    .filter-container { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ddd; }
    .excel-table { border-collapse: collapse; width: 100%; font-size: 11px; border: 2px solid #444; }
    .excel-table td { border: 1px solid #ccc; padding: 5px 8px; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 140px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. 안전한 데이터 추출 함수
def get_val(df, r, c):
    try:
        if r < df.shape[0] and c < df.shape[1]:
            val = df.iloc[r, c]
            return str(val).strip() if pd.notna(val) else ""
    except: return ""
    return ""

def extract_num(val):
    try:
        n = re.sub(r'[^0-9.]', '', str(val).replace(',', ''))
        return float(n) if n else 0
    except: return 0

# 3. 메인 화면
st.title("📂 설비 비교 프로젝트 선정 시스템")
uploaded_file = st.file_uploader("📊 분석할 엑셀(XLSX) 또는 CSV 파일을 업로드하세요", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file, header=None)
        else: df = pd.read_excel(uploaded_file, header=None)
        
        st.success(f"✅ 파일을 읽었습니다. (데이터 크기: {df.shape[0]}행 x {df.shape[1]}열)")

        # 4. 검색 필터 UI (리스트 복구)
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: v_loc = st.selectbox("위치", ["전체", "서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "강원"])
        with c2: v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
        with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "EHP"])
        with c4: v_unit = st.selectbox("세대수", ["전체", "100세대 미만", "101~300세대", "301~500세대", "501~1000세대", "1001~2000세대", "2001~3000세대", "3001세대 이상"])
        
        c5, c6, c7 = st.columns(3)
        with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링"])
        with c6: v_area = st.selectbox("연면적(평)", ["전체", "~3만", "3~5만", "5~7만", "7~10만", "10~20만", "20만~"])
        with c7: v_fire = st.selectbox("소방/성능위주", ["전체", "소방포함", "성능위주"])

        # 누락되었던 다중 선택 리스트 복구
        v_specs = st.multiselect("특화설비", ["우수처리", "중수처리", "연료전지", "지열", "정화조", "사우나", "음식물", "쓰레기", "수영장"])
        v_notes = st.multiselect("특수사항", ["지하단차", "초고층", "준초고층", "진출입", "산악", "공항", "지하철"])
        st.markdown('</div>', unsafe_allow_html=True)

        # 5. 검색 실행
        if st.button("🚀 프로젝트 조회", use_container_width=True):
            found_indices = []
            for j in range(3, df.shape[1], 2):
                name = get_val(df, 0, j)
                if not name or "Unnamed" in name: continue

                # 좌표 및 데이터 추출
                row_year = get_val(df, 4, j)
                row_hvac = get_val(df, 5, j)
                row_type = get_val(df, 6, j)
                row_fire_note = get_val(df, 6, j+1) # 비고란 확인용
                row_unit = extract_num(get_val(df, 7, j)) + extract_num(get_val(df, 8, j))
                row_area = extract_num(get_val(df, 14, j))
                
                # 특화설비 및 특수사항 통합 검색 (45행~50행 구간 훑기)
                all_notes = ""
                for r in range(45, 51):
                    all_notes += get_val(df, r, j) + get_val(df, r, j+1)

                # 매칭 로직
                m_loc = (v_loc == "전체") or (v_loc in name)
                m_year = (v_year == "전체") or (v_year in row_year)
                m_hvac = (v_hvac == "전체") or (v_hvac in row_hvac)
                m_type = (v_type == "전체") or (v_type in row_type)
                m_fire = (v_fire == "전체") or (v_fire in row_fire_note) or (v_fire in row_type)
                
                # 세대수 구간 로직
                m_unit = True
                if v_unit != "전체":
                    if "100세대 미만" in v_unit: m_unit = row_unit < 100
                    elif "101~300" in v_unit: m_unit = 101 <= row_unit <= 300
                    elif "301~500" in v_unit: m_unit = 301 <= row_unit <= 500
                    elif "501~1000" in v_unit: m_unit = 501 <= row_unit <= 1000
                    elif "1001~2000" in v_unit: m_unit = 1001 <= row_unit <= 2000
                    elif "2001~3000" in v_unit: m_unit = 2001 <= row_unit <= 3000
                    else: m_unit = row_unit >= 3001

                # 연면적 구간 로직
                m_area = True
                if v_area != "전체":
                    if "~3만" in v_area: m_area = row_area <= 30000
                    elif "3~5만" in v_area: m_area = 30001 <= row_area <= 50000
                    elif "5~7만" in v_area: m_area = 50001 <= row_area <= 70000
                    elif "7~10만" in v_area: m_area = 70001 <= row_area <= 100000
                    elif "10~20만" in v_area: m_area = 100001 <= row_area <= 200000
                    else: m_area = row_area > 200000

                # 다중 선택 키워드 매칭
                m_spec = all(s in all_notes for s in v_specs)
                m_note = all(n in all_notes for n in v_notes)

                if all([m_loc, m_year, m_hvac, m_type, m_fire, m_unit, m_area, m_spec, m_note]):
                    found_indices.append(j)

            # 6. 결과 출력
            if found_indices:
                st.success(f"🎯 {len(found_indices)}개의 프로젝트를 찾았습니다.")
                for col in found_indices:
                    with st.expander(f"📌 {get_val(df, 0, col)}"):
                        html = '<table class="excel-table">'
                        for r in range(len(df)):
                            h1, h2 = get_val(df, r, 0), get_val(df, r, 1)
                            d1, d2 = get_val(df, r, col), get_val(df, r, col+1)
                            if h1 or h2 or d1 or d2:
                                html += f'<tr><td class="header-col">{h1}</td><td class="header-col">{h2}</td>'
                                html += f'<td>{d1}</td><td>{d2}</td></tr>'
                        st.markdown(html + '</table>', unsafe_allow_html=True)
            else:
                st.warning("🧐 조건에 맞는 프로젝트가 없습니다.")
    except Exception as e:
        st.error(f"⚠️ 오류가 발생했습니다. (파일 형식을 확인해주세요): {e}")
