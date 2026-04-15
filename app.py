import streamlit as st
import pandas as pd
import os
import re

# 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 스타일 설정
st.markdown("""
    <style>
    .filter-container { background-color: #ffff00; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .stSelectbox label { font-weight: bold; color: black; }
    .stTable { font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "비교프로젝트_설비.xlsx"
    if not os.path.exists(file_name): return None
    # 모든 시트를 읽어오되, 첫 번째 시트를 메인으로 사용
    return pd.read_excel(file_name, header=None)

df = load_data()

# 숫자만 추출하는 안전한 함수
def extract_number(value):
    if pd.isna(value): return 0
    try:
        # 숫자와 소수점만 남기고 제거
        num_str = re.sub(r'[^0-9.]', '', str(value))
        return float(num_str) if num_str else 0
    except:
        return 0

if df is None:
    st.error("❌ '비교프로젝트_설비.xlsx' 파일을 찾을 수 없습니다.")
else:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.write("### 🔍 검색 조건 설정")
    
    c1, c2, c3, c4 = st.columns(4)
    c5, c6, c7, c8, c9 = st.columns(5)

    with c1: v_loc = st.selectbox("위치", ["전체", "서울", "경기", "인천", "강원", "충청", "경상", "전라", "제주", "기타"])
    with c2: v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "기타"])
    with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "EHP", "기타"])
    with c4: v_unit = st.selectbox("세대수", ["전체", "1~300세대", "301~500세대", "501~1000세대", "1001세대 이상"])
    with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "오피스텔", "판매시설", "기타"])
    with c6: v_area = st.selectbox("연면적", ["전체", "~30,000평", "30,001~50,000평", "50,001~100,000평", "100,001평 이상"])
    with c7: v_fire = st.selectbox("소방포함", ["전체", "소방포함", "성능위주", "기타"])
    with c8: v_spec = st.selectbox("특화설비", ["전체", "우수처리시설", "정화조", "수영장", "없음", "기타"])
    with c9: v_note = st.selectbox("특수사항", ["전체", "지하단차", "없음", "기타"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 조건에 맞는 프로젝트 조회", use_container_width=True):
        found_projects = []
        
        # D열(3)부터 2열씩 건너뛰며 검사
        for j in range(3, len(df.columns), 2):
            p_name = str(df.iloc[1, j]) # 2행: 프로젝트명
            if pd.isna(df.iloc[1, j]) or p_name.strip() == "": continue

            # --- 1. 위치 ---
            loc_list = ["서울", "경기", "인천", "강원", "충청", "경상", "전라", "제주"]
            match_loc = (v_loc == "전체") or (v_loc == "기타" and not any(x in p_name for x in loc_list)) or (v_loc in p_name)

            # --- 2. 년도 (4행) ---
            date_val = str(df.iloc[3, j])
            p_year = re.search(r'(\d{4})', date_val).group(1) if re.search(r'(\d{4})', date_val) else ""
            year_list = ["2020", "2021", "2022", "2023", "2024", "2025"]
            match_year = (v_year == "전체") or (v_year == "기타" and p_year not in year_list) or (v_year == p_year)

            # --- 3. 냉난방방식 (5행) ---
            hvac_val = str(df.iloc[4, j])
            match_hvac = (v_hvac == "전체") or (v_hvac == "개별가스" and "개별가스" in hvac_val) or \
                         (v_hvac == "지역난방" and ("지역" in hvac_val)) or (v_hvac == "EHP" and "EHP" in hvac_val) or \
                         (v_hvac == "기타" and not any(x in hvac_val for x in ["개별가스", "지역", "EHP"]))

            # --- 4. 세대수 (7+8행 합계) ---
            total_units = extract_number(df.iloc[6, j]) + extract_number(df.iloc[7, j])
            match_unit = (v_unit == "전체") or \
                         (v_unit == "1~300세대" and 1 <= total_units <= 300) or \
                         (v_unit == "301~500세대" and 301 <= total_units <= 500) or \
                         (v_unit == "501~1000세대" and 501 <= total_units <= 1000) or \
                         (v_unit == "1001세대 이상" and total_units >= 1001)

            # --- 5. 건물유형 (6행) ---
            type_val = str(df.iloc[5, j])
            match_type = (v_type == "전체") or (v_type == "공동주택" and "공동주택" in type_val) or \
                         (v_type == "오피스텔" and "오피스텔" in type_val) or (v_type == "판매시설" and "판매" in type_val) or \
                         (v_type == "기타" and not any(x in type_val for x in ["공동주택", "오피스텔", "판매"]))

            # --- 6. 연면적 (14행) ---
            area_val = extract_number(df.iloc[13, j])
            match_area = (v_area == "전체") or \
                         (v_area == "~30,000평" and area_val <= 30000) or \
                         (v_area == "30,001~50,000평" and 30001 <= area_val <= 50000) or \
                         (v_area == "50,001~100,000평" and 50001 <= area_val <= 100000) or \
                         (v_area == "100,001평 이상" and area_val >= 100001)

            # --- 7. 소방포함 (6행 인접열) ---
            fire_val = str(df.iloc[5, j+1])
            match_fire = (v_fire == "전체") or (v_fire in fire_val) or \
                         (v_fire == "기타" and not any(x in fire_val for x in ["소방포함", "성능위주"]))

            # --- 8. 특화설비 (47행) ---
            spec_val = str(df.iloc[46, j]) if pd.notna(df.iloc[46, j]) else ""
            spec_list = ["우수처리", "정화조", "수영장"]
            match_spec = (v_spec == "전체") or \
                         (v_spec == "없음" and spec_val.strip() == "") or \
                         (v_spec == "기타" and spec_val.strip() != "" and not any(x in spec_val for x in spec_list)) or \
                         (v_spec != "없음" and v_spec != "기타" and v_spec[:2] in spec_val)

            # --- 9. 특수사항 (49행) ---
            note_val = str(df.iloc[48, j]) if pd.notna(df.iloc[48, j]) else ""
            match_note = (v_note == "전체") or \
                         (v_note == "없음" and note_val.strip() == "") or \
                         (v_note == "기타" and note_val.strip() != "" and "지하단차" not in note_val) or \
                         (v_note == "지하단차" and "지하단차" in note_val)

            # 교집합 판정
            if all([match_loc, match_year, match_hvac, match_unit, match_type, match_area, match_fire, match_spec, match_note]):
                detail = df.iloc[0:49, [0, 1, j, j+1]]
                detail.columns = ['구분1', '구분2', '내용', '비고']
                found_projects.append((p_name, detail))

        if found_projects:
            st.success(f"🎯 총 {len(found_projects)}개의 프로젝트가 검색되었습니다.")
            for name, res_df in found_projects:
                with st.expander(f"📌 {name} 상세 데이터 (1~49행)"):
                    st.table(res_df.reset_index(drop=True))
        else:
            st.warning("🧐 조건에 맞는 프로젝트가 없습니다. 필터를 조정해보세요.")
