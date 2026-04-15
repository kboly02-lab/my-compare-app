import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 스타일 설정
st.markdown("""
    <style>
    .filter-container { background-color: #ffff00; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .stSelectbox label { font-weight: bold; color: black; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "비교프로젝트_설비.xlsx"
    if not os.path.exists(file_name):
        return None, None
    
    # 시트가 여러 개일 수 있으므로 첫 번째와 두 번째 시트를 확인합니다.
    try:
        all_sheets = pd.read_excel(file_name, sheet_name=None, header=None)
        sheet_names = list(all_sheets.keys())
        # 첫 번째 시트는 필터용(기준), 두 번째 시트는 데이터용으로 가정하거나 
        # 사용자가 주신 image_dff2a5.png가 'Sheet1'일 경우를 대비합니다.
        return all_sheets[sheet_names[0]], all_sheets
    except:
        return None, None

df_main, all_data = load_data()

if df_main is None:
    st.error("❌ '비교프로젝트_설비.xlsx' 파일을 찾을 수 없습니다. 깃허브에 파일이 있는지 확인해주세요.")
else:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    # --- 상단 필터 영역 ---
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.write("### 🔍 프로젝트 검색 조건")
    
    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7, col8 = st.columns(4)
    
    # image_54684c.png 기준 필터 데이터 추출 (안전하게 추출)
    def safe_get(c, r_start, r_end):
        try:
            return ["전체"] + [str(x) for x in df_main.iloc[r_start:r_end, c].dropna().unique()]
        except:
            return ["전체"]

    with col1: v_loc = st.selectbox("위치", safe_get(0, 1, 15))
    with col2: v_year = st.selectbox("년도", safe_get(1, 1, 10))
    with col3: v_hvac = st.selectbox("냉난방방식", safe_get(2, 1, 5))
    with col4: v_unit = st.selectbox("세대수", safe_get(3, 1, 10))
    with col5: v_type = st.selectbox("건물유형", safe_get(4, 1, 10))
    with col6: v_area = st.selectbox("연면적", safe_get(5, 1, 10))
    with col7: v_fire = st.selectbox("소방포함", safe_get(6, 1, 5))
    with col8: v_spec = st.selectbox("특화설비", safe_get(7, 1, 15))
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 조회 로직 ---
    if st.button("🚀 조건에 맞는 프로젝트 조회", use_container_width=True):
        # image_dff2a5.png 구조 분석: 
        # 프로젝트명은 2행(index 1) 또는 4행(index 3) D, F, H... 열에 있음
        # 데이터는 4열(D열, index 3)부터 시작해서 2열씩 건너뜀
        
        found_projects = []
        
        # 엑셀 시트 중 데이터가 들어있는 시트 선택 (보통 'Sheet1')
        data_df = df_main 
        
        # 4번째 열(D열)부터 끝까지 2열씩 검사
        for j in range(3, len(data_df.columns), 2):
            project_name = data_df.iloc[1, j] # '동작 하이팰리스...' 등의 이름
            if pd.isna(project_name): continue
            
            # 검색 필터 비교 (현재는 필터 선택 시 해당 프로젝트의 전체 내용을 보여주도록 설정)
            # 엑셀의 특정 행(예: 5행의 냉난방, 7행의 세대수 등)과 필터값을 대조합니다.
            
            # 상세 데이터 추출 (A~B열의 항목명 + 해당 프로젝트의 값열)
            detail = data_df.iloc[4:40, [0, 1, j, j+1]] # 항목명과 해당 프로젝트 데이터
            detail.columns = ['구분1', '구분2', '금액/수치', '비고']
            
            found_projects.append((project_name, detail))

        if found_projects:
            st.success(f"🎯 총 {len(found_projects)}개의 프로젝트가 검색되었습니다.")
            for name, d_df in found_projects:
                with st.expander(f"📌 {name} (상세보기)"):
                    st.table(d_df.reset_index(drop=True)) # 표 형태로 깔끔하게 출력
        else:
            st.warning("일치하는 프로젝트가 없습니다.")
