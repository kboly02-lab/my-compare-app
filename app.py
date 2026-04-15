import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 2. 스타일 설정 (엑셀 양식 극대화)
st.markdown("""
    <style>
    .filter-container { background-color: #ffff00; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ccc; }
    .stSelectbox label { font-weight: bold; color: black; }
    .excel-table { border-collapse: collapse; width: 100%; font-size: 11px; border: 2px solid #444; }
    .excel-table th, .excel-table td { border: 1px solid #ccc; padding: 5px 8px; text-align: left; }
    .excel-table th { background-color: #f2f2f2; font-weight: bold; text-align: center; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 140px; }
    .project-title { background-color: #4472c4; color: white; font-weight: bold; text-align: center; font-size: 15px; height: 35px; }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 함수
@st.cache_data
def load_data():
    # 파일명이 여러 버전일 수 있으므로 체크
    file_names = ["비교프로젝트_설비.xlsx - Sheet1.csv", "비교프로젝트_설비.xlsx"]
    for f in file_names:
        if os.path.exists(f):
            try:
                # 엑셀/CSV 구분하여 로드 (header=None 필수: 1행부터 데이터로 인식)
                if f.endswith('.csv'): return pd.read_csv(f, header=None)
                else: return pd.read_excel(f, header=None)
            except: continue
    return None

df = load_data()

if df is None:
    st.error("❌ '비교프로젝트_설비.xlsx' 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
else:
    # --- 검색 조건 설정 UI ---
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.write("### 🔍 검색 조건 설정")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: v_loc = st.selectbox("위치", ["전체", "서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "충청", "전라", "경상", "강원"])
    with c2: v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
    with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "기타"])
    with c4: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링", "일반건축물"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 프로젝트 조회", use_container_width=True):
        found_indices = []
        
        # [데이터 구조 분석 결과] 
        # - 프로젝트명: 1행 (df 인덱스 0)
        # - 년도: 4행 (df 인덱스 3) -> D4, F4 등
        # - 냉난방방식: 5행 (df 인덱스 4)
        # - 건물유형: 6행 (df 인덱스 5)
        # - 데이터 시작 열: D열 (df 인덱스 3)부터 2칸 간격
        
        project_cols = [j for j in range(3, len(df.columns), 2)]

        for j in project_cols:
            # 1. 프로젝트명 (1행)
            p_name = str(df.iloc[0, j]) if pd.notna(df.iloc[0, j]) else ""
            if not p_name.strip() or "공사금액" in p_name: continue

            # 2. 위치 (이름에 포함 여부)
            m_loc = (v_loc == "전체") or (v_loc in p_name)
            
            # 3. 년도 (4행 = 인덱스 3) ★ 사용자 요청 포인트
            val_year = str(df.iloc[3, j])
            m_year = (v_year == "전체") or (v_year in val_year)
            
            # 4. 냉난방방식 (5행 = 인덱스 4)
            val_hvac = str(df.iloc[4, j])
            m_hvac = (v_hvac == "전체") or (v_hvac in val_hvac)
            
            # 5. 건물유형 (6행 = 인덱스 5)
            val_type = str(df.iloc[5, j])
            m_type = (v_type == "전체") or (v_type in val_type)

            # 모든 필터 조건 결합
            if m_loc and m_year and m_hvac and m_type:
                found_indices.append(j)

        # 결과 렌더링
        if found_indices:
            st.success(f"🎯 조건에 맞는 프로젝트를 {len(found_indices)}개 찾았습니다.")
            for col in found_indices:
                with st.expander(f"📌 {df.iloc[0, col]} 상세 데이터"):
                    html = '<table class="excel-table">'
                    html += f'<tr><th colspan="4" class="project-title">{df.iloc[0, col]}</th></tr>'
                    html += '<tr><th>구분1</th><th>구분2</th><th>내용</th><th>비고</th></tr>'
                    
                    # 49행까지 출력 (데이터가 있는 만큼)
                    for r in range(49):
                        try:
                            v1 = df.iloc[r, 0] if pd.notna(df.iloc[r, 0]) else "" # A열
                            v2 = df.iloc[r, 1] if pd.notna(df.iloc[r, 1]) else "" # B열
                            v3 = df.iloc[r, col] if pd.notna(df.iloc[r, col]) else "" # 데이터열
                            v4 = df.iloc[r, col+1] if pd.notna(df.iloc[r, col+1]) else "" # 비고열
                            html += f'<tr><td class="header-col">{v1}</td><td class="header-col">{v2}</td><td>{v3}</td><td>{v4}</td></tr>'
                        except: break
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("🧐 일치하는 현장이 없습니다. 조건을 '전체'로 변경한 후 하나씩 선택해보세요.")
