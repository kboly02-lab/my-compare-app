import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 2. 안전한 데이터 추출 함수 (KeyError 방지 및 병합셀 처리)
def get_val(df, r, c):
    try:
        if r < df.shape[0] and c < df.shape[1]:
            val = df.iloc[r, c]
            return str(val).strip() if pd.notna(val) else ""
    except: return ""
    return ""

def extract_num(val):
    try:
        # 숫자만 추출 (콤마 제거)
        n = re.sub(r'[^0-9.]', '', str(val).replace(',', ''))
        return float(n) if n else 0
    except: return 0

# 3. 메인 화면
st.title("📂 설비 비교 프로젝트 선정 시스템")
uploaded_file = st.file_uploader("📊 '비교프로젝트_설비' 파일을 업로드해주세요", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file, header=None)
        else: df = pd.read_excel(uploaded_file, header=None)
        
        st.success("✅ 파일을 성공적으로 읽었습니다.")

        # --- 필터 UI (사용자 요청 리스트 구성) ---
        st.markdown('<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        
        # 위치: 서울~강원 + 기타
        loc_list = ["서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "강원"]
        with c1: v_loc = st.selectbox("위치", ["전체"] + loc_list + ["기타"])
        
        # 년도: 2020~2026 + 기타
        year_list = ["2020", "2021", "2022", "2023", "2024", "2025", "2026"]
        with c2: v_year = st.selectbox("년도", ["전체"] + year_list + ["기타"])
        
        # 냉난방방식
        hvac_list = ["개별가스", "지역난방", "중앙난방", "EHP"]
        with c3: v_hvac = st.selectbox("냉난방방식", ["전체"] + hvac_list + ["기타"])
        
        # 세대수 합산 범위
        with c4: v_unit = st.selectbox("세대수", ["전체", "100세대 미만", "101~300세대", "301~500세대", "501~1000세대", "1001~2000세대", "2001~3000세대", "3001세대 이상"])
        
        c5, c6, c7 = st.columns(3)
        # 건물유형
        type_list = ["공동주택", "주상복합", "오피스텔", "리모델링"]
        with c5: v_type = st.selectbox("건물유형", ["전체"] + type_list + ["기타"])
        
        # 연면적 범위
        with c6: v_area = st.selectbox("연면적(평)", ["전체", "~30000", "30001~50000", "50001~70000", "70001~100000", "100001~200000", "200001~"])
        
        # 소방포함 (요청하신 정확한 4종 리스트)
        fire_list = ["소방포함/ 성능위주", "소방포함/ 비성능위주", "소방제외/ 성능위주", "소방제외/ 비성능위주"]
        with c7: v_fire = st.selectbox("소방포함", ["전체"] + fire_list + ["기타"])

        # 특화설비 및 특수사항
        spec_list = ["우수처리", "중수처리", "연료전지", "지열", "정화조", "사우나", "음식물", "쓰레기", "수영장"]
        v_specs = st.selectbox("특화설비", ["전체", "없음", "기타"] + spec_list)
        
        note_list = ["지하단차", "초고층", "준초고층", "진출입", "산악", "공항", "지하철"]
        v_notes = st.selectbox("특수사항", ["전체", "없음", "기타"] + note_list)
        st.markdown('</div>', unsafe_allow_html=True)

        # 4. 검색 로직 (D열=3번 인덱스부터 2칸씩 점프)
        if st.button("🚀 프로젝트 조회", use_container_width=True):
            found_indices = []
            for j in range(3, df.shape[1], 2):
                # [위치] 1행 (0번 인덱스)
                p_name = get_
