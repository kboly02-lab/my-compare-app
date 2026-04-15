import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 검색", layout="wide")

# 2. 스타일 설정
st.markdown("""
    <style>
    .filter-container { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ddd; }
    .excel-table { border-collapse: collapse; width: 100%; font-size: 11px; border: 2px solid #444; }
    .excel-table td { border: 1px solid #ccc; padding: 5px 8px; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 140px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 안전하게 데이터를 가져오는 함수 (범위 밖 참조 시 에러 대신 빈 문자열 반환)
def get_val(df, r, c):
    try:
        if r < len(df) and c < len(df.columns):
            val = df.iloc[r, c]
            return str(val).strip() if pd.notna(val) else ""
    except:
        return ""
    return ""

def extract_num(val):
    try:
        n = re.sub(r'[^0-9.]', '', str(val).replace(',', ''))
        return float(n) if n else 0
    except:
        return 0

@st.cache_data
def load_data():
    # 파일명 후보들
    for f in ["비교프로젝트_설비.xlsx - Sheet1.csv", "비교프로젝트_설비.csv"]:
        if os.path.exists(f):
            return pd.read_csv(f, header=None)
    return None

df = load_data()

if df is None:
    st.error("❌ 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
else:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    # --- 검색 필터 ---
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: v_loc = st.selectbox("위치", ["전체", "서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "강원"])
    with c2: v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
    with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "EHP"])
    with c4: v_unit = st.selectbox("세대수", ["전체", "300세대 미만", "300~1000세대", "1000~2000세대", "2000세대 이상"])
    
    c5, c6, c7 = st.columns(3)
    with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링"])
    with c6: v_area = st.selectbox("연면적(평)", ["전체", "~3만", "3~5만", "5~10만", "10만~"])
    with c7: v_fire = st.selectbox("소방/성능위주", ["전체", "소방", "성능위주"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 프로젝트 조회", use_container_width=True):
        found_indices = []
        # D열(3)부터 2칸씩 점프 (프로젝트명 위치)
        for j in range(3, len(df.columns), 2):
            name = get_val(df, 0, j)
            if not name or "Unnamed" in name: continue

            # 데이터 추출 (엑셀 행 번호와 매칭 - 1)
            row_year = get_val(df, 4, j)      # 5행: 년도
            row_hvac = get_val(df, 5, j)      # 6행: 냉난방
            row_type = get_val(df, 6, j)      # 7행: 건물유형
            row_fire_note = get_val(df, 6, j+1) # 7행 비고: 소방/성능위주 정보가 자주 들어감
            
            # 세대수: 8행(아파트) + 9행(오피) 합산
            row_unit = extract_num(get_val(df, 7, j)) + extract_num(get_val(df, 8, j))
            # 연면적: 15행
            row_area = extract_num(get_val(df, 14, j))

            # 필터 로직
            m_loc = (v_loc == "전체") or (v_loc in name)
            m_year = (v_year == "전체") or (v_year in row_year)
            m_hvac = (v_hvac == "전체") or (v_hvac in row_hvac)
            m_type = (v_type == "전체") or (v_type in row_type)
            # 성능위주 필터: 유형 혹은 비고란에 해당 단어가 있는지 확인
            m_fire = (v_fire == "전체") or (v_fire in row_fire_note) or (v_fire in row_type)
            
            # 세대수 필터
            m_unit = True
            if v_unit != "전체":
                if "300세대 미만" in v_unit: m_unit = row_unit < 300
                elif "300~1000" in v_unit: m_unit = 300 <= row_unit <= 1000
                elif "1000~2000" in v_unit: m_unit = 1000 <= row_unit <= 2000
                else: m_unit = row_unit >= 2000

            # 연면적 필터
            m_area = True
            if v_area != "전체":
                if "~3만" in v_area: m_area = row_area <= 30000
                elif "3~5만" in v_area: m_area = 30001 <= row_area <= 50000
                elif "5~10만" in v_area: m_area = 50001 <= row_area <= 100000
                else: m_area = row_area > 100000

            if all([m_loc, m_year, m_hvac, m_type, m_fire, m_unit, m_area]):
                found_indices.append(j)

        # 결과 출력
        if found_indices:
            st.success(f"🎯 {len(found_indices)}개의 프로젝트를 찾았습니다.")
            for col in found_indices:
                with st.expander(f"📌 {get_val(df, 0, col)}"):
                    html = '<table class="excel-table">'
                    # 데이터가 있는 행까지만 출력하도록 dynamic range 설정
                    for r in range(len(df)):
                        h1, h2 = get_val(df, r, 0), get_val(df, r, 1)
                        d1, d2 = get_val(df, r, col), get_val(df, r, col+1)
                        if h1 or h2 or d1 or d2: # 내용이 있는 행만 표시
                            html += f'<tr><td class="header-col">{h1}</td><td class="header-col">{h2}</td>'
                            html += f'<td>{d1}</td><td>{d2}</td></tr>'
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("🧐 조건에 맞는 프로젝트가 없습니다.")
