import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 노란색 배경 스타일 적용
st.markdown("""
    <style>
    .filter-box { background-color: #ffff00; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .stSelectbox label { font-weight: bold; color: black; }
    </style>
""", unsafe_allow_html=True)

st.title("📂 설비 비교 프로젝트 선정 시스템")

# --- 이미지(image_e0d064.png) 리스트 기반 필터 구성 ---
st.markdown('<div class="filter-box">', unsafe_allow_html=True)
st.write("### 🔍 검색 조건 설정")

# 행 분할 (4개 / 5개)
c1, c2, c3, c4 = st.columns(4)
c5, c6, c7, c8, c9 = st.columns(5)

with c1:
    v_loc = st.selectbox("위치", ["전체", "서울", "인천", "경기", "대전", "광주", "부산", "오지(세종, 충청권)", "전라도", "경상도", "충청도", "강원도", "기타"])

with c2:
    v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "기타"])

with c3:
    v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "기타"])

with c4:
    v_unit = st.selectbox("세대수", ["전체", "100세대 미만", "101~300세대", "301~500세대", "501~1000세대", "1001~2000세대", "2001~3000세대", "3001세대 이상", "기타"])

with c5:
    v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링", "일반건축물", "기타"])

with c6:
    v_area = st.selectbox("연면적", ["전체", "~30,000평", "30,001~50,000평", "50,001~70,000평", "70,001~100,000평", "100,001~200,000평", "200,001~300,000평", "300,001평~"])

with c7:
    v_fire = st.selectbox("소방포함", ["전체", "소방포함/성능위주", "소방포함/비성능위주", "소방제외/성능위주", "소방제외/비성능위주", "기타"])

with c8:
    v_spec = st.selectbox("특화설비", ["전체", "우수처리시설", "중수처리시설", "연료전지", "지열", "정화조", "사우나", "음식물쓰레기 이송설비", "일반쓰레기 이송설비", "수영장", "주차시설", "기타", "없음"])

with c9:
    v_note = st.selectbox("특수사항", ["전체", "지하단차", "초고층", "준초고층", "진출입 어려움", "산악지역", "공항지역", "지하철인근", "기타", "없음"])

st.markdown('</div>', unsafe_allow_html=True)

# 조회 버튼
if st.button("🚀 프로젝트 조회", use_container_width=True):
    st.info("선택한 조건으로 검색을 시작합니다.")
    # 여기에 다음 단계인 엑셀 매칭 로직이 들어갑니다.
