import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 스타일
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")
st.markdown("""
    <style>
    .filter-container { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ddd; }
    .excel-table { border-collapse: collapse; width: 100%; font-size: 11px; border: 2px solid #444; }
    .excel-table td { border: 1px solid #ccc; padding: 5px 8px; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 140px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. 안전한 데이터 추출 함수 (에러 방지 핵심)
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

# 3. 메인 화면 구성
st.title("📂 설비 비교 프로젝트 선정 시스템")
st.info("💡 아래 [Browse files] 버튼을 눌러 엑셀(XLSX) 또는 CSV 파일을 업로드해주세요.")

# 파일 업로드 (파일명 오류 원천 차단)
uploaded_file = st.file_uploader("📊 비교프로젝트 파일을 선택하세요", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # 확장자별 로딩
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None)
        else:
            df = pd.read_excel(uploaded_file, header=None)
        
        st.success(f"✅ 파일을 성공적으로 읽어왔습니다. (총 {len(df)}행 데이터)")

        # 4. 검색 필터 UI
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: v_loc = st.selectbox("위치(지역)", ["전체", "서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "강원"])
        with c2: v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
        with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "EHP", "GHP"])
        with c4: v_unit = st.selectbox("세대수", ["전체", "300세대 미만", "300~1000세대", "1000~2000세대", "2000세대 이상"])
        
        c5, c6, c7 = st.columns(3)
        with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링"])
        with c6: v_area = st.selectbox("연면적(평)", ["전체", "~3만", "3~5만", "5~10만", "10만~"])
        with c7: v_fire = st.selectbox("소방
