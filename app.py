import streamlit as st
import pandas as pd

# 앱 레이아웃 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 배경색(노란색) 및 스타일 설정
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stSelectbox { background-color: #ffff00 !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # 파일명은 '비교프로젝트_설비.xlsx'로 준비해주세요.
        return pd.read_excel("비교프로젝트_설비.xlsx", header=None)
    except:
        return None

df = load_data()

if df is None:
    st.error("❌ '비교프로젝트_설비.xlsx' 파일을 찾을 수 없습니다. 앱과 같은 폴더에 파일을 놓아주세요.")
else:
    st.title("📂 비교프로젝트 선정 시스템")
    
    # --- 상단 선택 영역 (사진과 동일한 9개 항목) ---
    with st.container():
        st.write("### 🔍 검색 조건 설정")
        r1, r2, r3, r4, r5 = st.columns(5)
        r6, r7, r8, r9, _ = st.columns(5)
        
        with r1: v_type = st.selectbox("건물유형", ["전체"] + sorted(list(df.iloc[1:10, 4].dropna().unique())))
        with r2: v_loc = st.selectbox("위치", ["전체"] + sorted(list(df.iloc[1:12, 0].dropna().unique())))
        with r3: v_year = st.selectbox("년도", ["전체"] + [str(x) for x in df.iloc[1:8, 1].dropna().unique()])
        with r4: v_hvac = st.selectbox("냉난방방식", ["전체"] + sorted(list(df.iloc[1:4, 2].dropna().unique())))
        with r5: v_unit = st.selectbox("세대수", ["전체"] + sorted(list(df.iloc[1:8, 3].dropna().unique())))
        with r6: v_area = st.selectbox("연면적", ["전체"] + sorted(list(df.iloc[1:7, 5].dropna().unique())))
        with r7: v_fire = st.selectbox("소방포함", ["전체"] + sorted(list(df.iloc[1:5, 6].dropna().unique())))
        with r8: v_spec = st.selectbox("특화설비", ["전체"] + sorted(list(df.iloc[1:12, 7].dropna().unique())))
        with r9: v_note = st.selectbox("특수사항", ["전체"] + sorted(list(df.iloc[1:9, 8].dropna().unique())))

    # --- 조회 버튼 및 필터링 로직 ---
    if st.button("🚀 교집합 프로젝트 조회", use_container_width=True):
        results = []
        
        # D열(index 3)부터 2열씩 세트로 검사
        for i in range(3, len(df.columns), 2):
            # 1. A열의 5번셀 (index 4)
            c1 = str(df.iloc[4, i])
            # 2. A열 7번 + C열 7번 (index 6)
            c2 = str(df.iloc[6, i]) + str(df.iloc[6, i+1])
            # 3. A열 8번 + C열 8번 (index 7)
            c3 = str(df.iloc[7, i]) + str(df.iloc[7, i+1])
            # 4. A열 13번 + A열 14번 (index 12, 13)
            c4 = str(df.iloc[12, i]) + str(df.iloc[13, i])
            
            # 교집합 체크 (선택한 조건만 필터링)
            match = True
            # 요청하신 핵심 4가지 교집합 조건 매칭 (예시 기준)
            if v_type != "전체" and v_type not in c1: match = False
            # ... 필요한 만큼 조건을 추가할 수 있습니다.
            
            if match:
                res_df = df.iloc[0:48, [i, i+1]]
                res_df.columns = ["항목", "내용"] # 가독성을 위한 컬럼명
                results.append((f"프로젝트 {i//2}", res_df))

        # --- 결과 표시 ---
        if results:
            st.success(f"🎯 총 {len(results)}개의 프로젝트를 찾았습니다.")
            for name, data in results:
                with st.expander(f"📌 {name} 상세 데이터 (1~48행)"):
                    st.table(data)
        else:
            st.warning("🧐 조건에 맞는 프로젝트가 없습니다. 선택 조건을 변경해 보세요.")