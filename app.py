import streamlit as st
import pandas as pd
import os
import re
import time

# 1. 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 2. 스타일 설정 (노란색 배경 및 엑셀 스타일 표)
st.markdown("""
    <style>
    .filter-container { background-color: #ffff00; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .stSelectbox label { font-weight: bold; color: black; }
    
    /* 엑셀 스타일 테이블 CSS */
    .excel-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 13px;
        border: 2px solid #444;
    }
    .excel-table th, .excel-table td {
        border: 1px solid #ccc;
        padding: 8px;
        text-align: left;
    }
    .excel-table th {
        background-color: #f2f2f2;
        font-weight: bold;
        text-align: center;
    }
    .excel-table tr:nth-child(even) { background-color: #fafafa; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 15%; }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 함수
@st.cache_data
def load_data():
    file_name = "비교프로젝트_설비.xlsx"
    if not os.path.exists(file_name):
        return None
    return pd.read_excel(file_name, header=None)

def extract_number(value):
    if pd.isna(value): return 0
    try:
        num_str = re.sub(r'[^0-9.]', '', str(value))
        return float(num_str) if num_str else 0
    except:
        return 0

df = load_data()

if df is None:
    st.error("❌ '비교프로젝트_설비.xlsx' 파일을 찾을 수 없습니다.")
else:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    # 4. 상단 필터 영역
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.write("### 🔍 검색 조건 설정")
    
    c1, c2, c3, c4 = st.columns(4)
    c5, c6, c7, c8, c9 = st.columns(5)

    with c1: v_loc = st.selectbox("위치", ["전체", "서울", "인천", "경기", "대전", "광주", "부산", "오지(세종, 충청권)", "전라도", "경상도", "충청도", "강원도", "기타"])
    with c2: v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "기타"])
    with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "기타"])
    with c4: v_unit = st.selectbox("세대수", ["전체", "100세대 미만", "101~300세대", "301~500세대", "501~1000세대", "1001~2000세대", "2001~3000세대", "3001세대 이상", "기타"])
    with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링", "일반건축물", "기타"])
    with c6: v_area = st.selectbox("연면적", ["전체", "~30,000평", "30,001~50,000평", "50,001~70,000평", "70,001~100,000평", "100,001~200,000평", "200,001~300,000평", "300,001평~"])
    with c7: v_fire = st.selectbox("소방포함", ["전체", "소방포함/성능위주", "소방포함/비성능위주", "소방제외/성능위주", "소방제외/비성능위주", "기타"])
    with c8: v_spec = st.selectbox("특화설비", ["전체", "우수처리시설", "중수처리시설", "연료전지", "지열", "정화조", "사우나", "음식물쓰레기 이송설비", "일반쓰레기 이송설비", "수영장", "주차시설", "기타", "없음"])
    with c9: v_note = st.selectbox("특수사항", ["전체", "지하단차", "초고층", "준초고층", "진출입 어려움", "산악지역", "공항지역", "지하철인근", "기타", "없음"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 프로젝트 조회", use_container_width=True):
        found_projects = []
        project_cols = [j for j in range(3, len(df.columns), 2)]
        total_cols = len(project_cols)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        start_time = time.time()

        for i, j in enumerate(project_cols):
            # 시간 및 진행바 계산
            elapsed = time.time() - start_time
            avg = elapsed / (i + 1)
            rem = avg * (total_cols - (i + 1))
            progress_bar.progress((i + 1) / total_cols)
            status_text.markdown(f"⏳ **분석 중 ({i+1}/{total_cols})** | 예상 남은 시간: **{rem:.1f}초**")
            
            p_name = str(df.iloc[1, j]) if pd.notna(df.iloc[1, j]) else ""
            if not p_name.strip(): continue

            # --- 필터링 로직 (위와 동일) ---
            loc_list = ["서울", "인천", "경기", "대전", "광주", "부산", "세종", "충청", "전라", "경상", "강원"]
            match_loc = (v_loc == "전체") or (v_loc == "기타" and not any(x in p_name for x in loc_list)) or (v_loc[:2] in p_name)
            
            date_val = str(df.iloc[3, j])
            p_year = re.search(r'(\d{4})', date_val).group(1) if re.search(r'(\d{4})', date_val) else ""
            match_year = (v_year == "전체") or (v_year == "기타" and p_year not in ["2020","2021","2022","2023","2024","2025","2026"]) or (v_year == p_year)
            
            hvac_val = str(df.iloc[4, j])
            match_hvac = (v_hvac == "전체") or (v_hvac in hvac_val) or (v_hvac == "기타" and not any(x in hvac_val for x in ["개별가스", "지역", "중앙"]))
            
            total_units = extract_number(df.iloc[6, j]) + extract_number(df.iloc[7, j])
            match_unit = (v_unit == "전체") or (v_unit == "100세대 미만" and total_units < 100) or (v_unit == "101~300세대" and 101 <= total_units <= 300) or (v_unit == "301~500세대" and 301 <= total_units <= 500) or (v_unit == "501~1000세대" and 501 <= total_units <= 1000) or (v_unit == "1001~2000세대" and 1001 <= total_units <= 2000) or (v_unit == "2001~3000세대" and 2001 <= total_units <= 3000) or (v_unit == "3001세대 이상" and total_units >= 3001)

            type_val = str(df.iloc[5, j])
            match_type = (v_type == "전체") or (v_type in type_val) or (v_type == "기타" and not any(x in type_val for x in ["공동주택", "주상복합", "오피스텔", "리모델링", "일반건축"]))

            area_val = extract_number(df.iloc[13, j])
            match_area = (v_area == "전체") or (v_area == "~30,000평" and area_val <= 30000) or (v_area == "30,001~50,000평" and 30001 <= area_val <= 50000) or (v_area == "50,001~70,000평" and 50001 <= area_val <= 70000) or (v_area == "70,001~100,000평" and 70001 <= area_val <= 100000) or (v_area == "100,001~200,000평" and 100001 <= area_val <= 200000) or (v_area == "200,001~300,000평" and 200001 <= area_val <= 300000) or (v_area == "300,001평~" and area_val > 300000)

            fire_val = str(df.iloc[5, j+1])
            match_fire = (v_fire == "전체") or (v_fire in fire_val) or (v_fire == "기타" and not any(x in fire_val for x in ["소방포함", "성능위주", "제외"]))

            spec_val = str(df.iloc[46, j]) if pd.notna(df.iloc[46, j]) else ""
            match_spec = (v_spec == "전체") or (v_spec == "없음" and spec_val.strip() == "") or (v_spec == "기타" and spec_val.strip() != "" and not any(x in spec_val for x in ["우수처리", "중수처리", "연료전지", "지열", "정화조", "사우나", "음식물", "쓰레기", "수영장", "주차"])) or (v_spec != "없음" and v_spec != "기타" and v_spec[:2] in spec_val)

            note_val = str(df.iloc[48, j]) if pd.notna(df.iloc[48, j]) else ""
            match_note = (v_note == "전체") or (v_note == "없음" and note_val.strip() == "") or (v_note == "기타" and note_val.strip() != "" and not any(x in note_val for x in ["지하단차", "초고층", "진출입", "산악", "공항", "지하철"])) or (v_note != "전체" and v_note != "없음" and v_note != "기타" and v_note[:2] in note_val)

            if all([match_loc, match_year, match_hvac, match_unit, match_type, match_area, match_fire, match_spec, match_note]):
                found_projects.append(j)

        progress_bar.empty()
        status_text.empty()

        if found_projects:
            st.success(f"🎯 총 {len(found_projects)}개의 프로젝트가 검색되었습니다.")
            for col_idx in found_projects:
                p_title = str(df.iloc[1, col_idx])
                with st.expander(f"📌 {p_title} 상세 데이터"):
                    # 엑셀 스타일 HTML 표 생성
                    html = '<table class="excel-table">'
                    html += f'<tr><th colspan="4" style="background-color:#4472c4; color:white;">{p_title}</th></tr>'
                    html += '<tr><th>구분1</th><th>구분2</th><th>내용</th><th>비고</th></tr>'
                    
                    for row_idx in range(49):
                        v1 = df.iloc[row_idx, 0] if pd.notna(df.iloc[row_idx, 0]) else ""
                        v2 = df.iloc[row_idx, 1] if pd.notna(df.iloc[row_idx, 1]) else ""
                        v3 = df.iloc[row_idx, col_idx] if pd.notna(df.iloc[row_idx, col_idx]) else ""
                        v4 = df.iloc[row_idx, col_idx+1] if pd.notna(df.iloc[row_idx, col_idx+1]) else ""
                        
                        html += f'<tr><td class="header-col">{v1}</td><td class="header-col">{v2}</td><td>{v3}</td><td>{v4}</td></tr>'
                    
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("🧐 조건에 맞는 프로젝트가 없습니다.")
