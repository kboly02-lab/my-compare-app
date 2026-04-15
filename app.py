import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 배경색(노란색) 및 스타일 설정
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stSelectbox div[data-baseweb="select"] { background-color: #ffff00 !important; }
    .filter-box { background-color: #ffff00; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "비교프로젝트_설비.xlsx"
    if os.path.exists(file_name):
        return pd.read_excel(file_name, header=None)
    return None

df = load_data()

if df is None:
    st.error("❌ '비교프로젝트_설비.xlsx' 파일을 찾을 수 없습니다.")
else:
    st.title("📂 비교프로젝트 선정 시스템")
    
    # --- 상단 필터 영역 (노란색 배경 느낌) ---
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    st.write("### 🔍 검색 조건 설정")
    
    # 9개의 필터 구성 (가로로 배치)
    r1, r2, r3, r4, r5 = st.columns(5)
    r6, r7, r8, r9, _ = st.columns(5)
    
    # 엑셀의 데이터 범위 내에서 자동으로 선택지 생성 (A~I열 데이터 활용)
    with r1: v_type = st.selectbox("건물유형", ["전체"] + sorted(list(df.iloc[1:10, 4].dropna().unique())))
    with r2: v_loc = st.selectbox("위치", ["전체"] + sorted(list(df.iloc[1:12, 0].dropna().unique())))
    with r3: v_year = st.selectbox("년도", ["전체"] + [str(x) for x in df.iloc[1:8, 1].dropna().unique()])
    with r4: v_hvac = st.selectbox("냉난방방식", ["전체"] + sorted(list(df.iloc[1:4, 2].dropna().unique())))
    with r5: v_unit = st.selectbox("세대수", ["전체"] + sorted(list(df.iloc[1:8, 3].dropna().unique())))
    with r6: v_area = st.selectbox("연면적", ["전체"] + sorted(list(df.iloc[1:7, 5].dropna().unique())))
    with r7: v_fire = st.selectbox("소방포함", ["전체"] + sorted(list(df.iloc[1:5, 6].dropna().unique())))
    with r8: v_spec = st.selectbox("특화설비", ["전체"] + sorted(list(df.iloc[1:12, 7].dropna().unique())))
    with r9: v_note = st.selectbox("특수사항", ["전체"] + sorted(list(df.iloc[1:9, 8].dropna().unique())))
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 조회 버튼 및 교집합 로직 ---
    if st.button("🚀 조건에 맞는 프로젝트 조회", use_container_width=True):
        results = []
        # D열(3)부터 2열씩 검사
        for i in range(3, len(df.columns), 2):
            # 핵심 4조건 (A5, A7+C7, A8+C8, A13+A14) - 엑셀 인덱스 주의
            # 예시: 사용자가 선택한 필터값들이 각 열의 데이터와 일치하는지 체크
            match = True
            
            # (여기에 실제 엑셀 위치에 따른 필터 비교 로직이 들어갑니다)
            # 일단 모든 프로젝트를 보여주도록 설정 (테스트용)
            
            project_data = df.iloc[0:48, [i, i+1]]
            p_name = str(df.iloc[0, i]) if pd.notna(df.iloc[0, i]) else f"Project {i//2}"
            results.append((p_name, project_data))

        if results:
            st.success(f"🎯 총 {len(results)}개의 프로젝트를 찾았습니다.")
            for name, res_df in results:
                with st.expander(f"📌 {name} 상세 데이터 보기"):
                    st.dataframe(res_df, use_container_width=True)
        else:
            st.warning("🧐 일치하는 프로젝트가 없습니다.")
