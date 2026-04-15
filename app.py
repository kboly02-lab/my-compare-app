import streamlit as st
import pandas as pd
import os
import re
import time
from difflib import SequenceMatcher # 유사도 계산을 위한 라이브러리

# 1. 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 2. 스타일 설정
st.markdown("""
    <style>
    .filter-container { background-color: #ffff00; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .excel-table { border-collapse: collapse; width: 100%; font-size: 12px; border: 2px solid #444; }
    .excel-table th, .excel-table td { border: 1px solid #ccc; padding: 6px; text-align: left; }
    .excel-table th { background-color: #f2f2f2; font-weight: bold; text-align: center; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 15%; }
    </style>
""", unsafe_allow_html=True)

# --- 유틸리티 함수 추가 ---

def clean_text(text):
    """공백을 제거하고 소문자로 변환하여 비교를 준비함"""
    if pd.isna(text): return ""
    return re.sub(r'\s+', '', str(text)).lower()

def is_similar(target, source, threshold=0.6):
    """띄어쓰기 무시 및 오타 보정 로직 (유사도 60% 이상이면 일치로 간주)"""
    target_clean = clean_text(target)
    source_clean = clean_text(source)
    
    # 1. 공백 제거 후 포함 여부 확인 (가장 확실함)
    if target_clean in source_clean or source_clean in target_clean:
        return True
    
    # 2. 오타 보정 (레벤슈타인 거리 유사도 계산)
    similarity = SequenceMatcher(None, target_clean, source_clean).ratio()
    return similarity >= threshold

@st.cache_data
def load_data():
    file_name = "비교프로젝트_설비.xlsx"
    if not os.path.exists(file_name): return None
    return pd.read_excel(file_name, header=None)

def extract_number(value):
    if pd.isna(value): return 0
    try:
        num_str = re.sub(r'[^0-9.]', '', str(value))
        return float(num_str) if num_str else 0
    except: return 0

df = load_data()

if df is None:
    st.error("❌ '비교프로젝트_설비.xlsx' 파일을 찾을 수 없습니다.")
else:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.write("### 🔍 검색 조건 설정")
    c1, c2, c3, c4 = st.columns(4)
    c5, c6, c7, c8, c9 = st.columns(5)

    with c1: v_loc = st.selectbox("위치", ["전체", "서울", "인천", "경기", "대전", "광주", "부산", "세종", "충청", "전라", "경상", "강원", "기타"])
    with c2: v_year = st.selectbox("년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "기타"])
    with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "기타"])
    with c4: v_unit = st.selectbox("세대수", ["전체", "100세대 미만", "101~300세대", "301~500세대", "501~1000세대", "1001~2000세대", "2001~3000세대", "3001세대 이상"])
    with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링", "일반건축물", "기타"])
    with c6: v_area = st.selectbox("연면적", ["전체", "~30,000평", "30,001~50,000평", "50,001~70,000평", "70,001~100,000평", "100,001~200,000평", "200,001~300,000평", "300,001평~"])
    with c7: v_fire = st.selectbox("소방포함", ["전체", "소방포함", "소방제외", "성능위주", "기타"])
    with c8: v_spec = st.selectbox("특화설비", ["전체", "우수처리", "중수처리", "연료전지", "지열", "정화조", "사우나", "음식물", "쓰레기", "수영장", "주차", "기타", "없음"])
    with c9: v_note = st.selectbox("특수사항", ["전체", "지하단차", "초고층", "준초고층", "진출입", "산악", "공항", "지하철", "기타", "없음"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 프로젝트 조회", use_container_width=True):
        found_projects = []
        project_cols = [j for j in range(3, len(df.columns), 2)]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        start_time = time.time()

        for i, j in enumerate(project_cols):
            elapsed = time.time() - start_time
            avg = elapsed / (i + 1)
            rem = avg * (len(project_cols) - (i + 1))
            progress_bar.progress((i + 1) / len(project_cols))
            status_text.markdown(f"⏳ **분석 중 ({i+1}/{len(project_cols)})** | 남은 시간: **{rem:.1f}초**")
            
            p_name = str(df.iloc[1, j]) if pd.notna(df.iloc[1, j]) else ""
            if not p_name.strip() or "공사금액" in p_name: continue

            # --- [강화된 조건 매칭 로직 적용] ---
            
            match_loc = (v_loc == "전체") or is_similar(v_loc[:2], p_name)
            
            date_val = str(df.iloc[3, j])
            match_year = (v_year == "전체") or (v_year in date_val)
            
            hvac_val = str(df.iloc[4, j])
            match_hvac = (v_hvac == "전체") or is_similar(v_hvac, hvac_val)
            
            total_u = extract_number(df.iloc[6, j]) + extract_number(df.iloc[7, j])
            # 세대수 로직 (생략 없이 유지)
            if v_unit == "전체": match_unit = True
            elif "100세대 미만" in v_unit: match_unit = total_u < 100
            elif "101~300" in v_unit: match_unit = 101 <= total_u <= 300
            elif "301~500" in v_unit: match_unit = 301 <= total_u <= 500
            elif "501~1000" in v_unit: match_unit = 501 <= total_u <= 1000
            elif "1001~2000" in v_unit: match_unit = 1001 <= total_u <= 2000
            elif "2001~3000" in v_unit: match_unit = 2001 <= total_u <= 3000
            elif "3001세대 이상" in v_unit: match_unit = total_u >= 3001
            else: match_unit = True

            type_val = str(df.iloc[5, j])
            match_type = (v_type == "전체") or is_similar(v_type, type_val)

            area_val = extract_number(df.iloc[13, j])
            # 연면적 로직
            if v_area == "전체": match_area = True
            elif "~30,000평" in v_area: match_area = area_val <= 30000
            elif "30,001~50,000" in v_area: match_area = 30001 <= area_val <= 50000
            elif "50,001~70,000" in v_area: match_area = 50001 <= area_val <= 70000
            elif "70,001~100,000" in v_area: match_area = 70001 <= area_val <= 100000
            elif "100,001~200,000" in v_area: match_area = 100001 <= area_val <= 200000
            elif "200,001~300,000" in v_area: match_area = 200001 <= area_val <= 300000
            elif "300,001평~" in v_area: match_area = area_val > 300000
            else: match_area = True

            fire_val = str(df.iloc[5, j+1])
            match_fire = (v_fire == "전체") or is_similar(v_fire, fire_val)

            spec_val = str(df.iloc[46, j])
            match_spec = (v_spec == "전체") or (v_spec == "없음" and not spec_val.strip()) or is_similar(v_spec, spec_val)

            # 특수사항 (49행 인덱스 48) - 띄어쓰기 및 오타 보정 핵심
            note_content = str(df.iloc[48, j]) + str(df.iloc[48, j+1])
            match_note = (v_note == "전체") or (v_note == "없음" and not note_content.strip()) or is_similar(v_note, note_content)

            if all([match_loc, match_year, match_hvac, match_unit, match_type, match_area, match_fire, match_spec, match_note]):
                found_projects.append(j)

        progress_bar.empty()
        status_text.empty()

        if found_projects:
            st.success(f"🎯 총 {len(found_projects)}개의 프로젝트가 검색되었습니다.")
            for col_idx in found_projects:
                p_title = str(df.iloc[1, col_idx])
                with st.expander(f"📌 {p_title} 상세 데이터"):
                    html = '<table class="excel-table">'
                    html += f'<tr><th colspan="4" style="background-color:#4472c4; color:white; font-size:14px;">{p_title}</th></tr>'
                    html += '<tr><th>구분1</th><th>구분2</th><th>내용</th><th>비고</th></tr>'
                    for r in range(55):
                        v1, v2 = (df.iloc[r, 0] if pd.notna(df.iloc[r, 0]) else ""), (df.iloc[r, 1] if pd.notna(df.iloc[r, 1]) else "")
                        v3, v4 = (df.iloc[r, col_idx] if pd.notna(df.iloc[r, col_idx]) else ""), (df.iloc[r, col_idx+1] if pd.notna(df.iloc[r, col_idx+1]) else "")
                        html += f'<tr><td class="header-col">{v1}</td><td class="header-col">{v2}</td><td>{v3}</td><td>{v4}</td></tr>'
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("🧐 조건에 맞는 프로젝트가 없습니다. 선택하신 조건을 다시 확인해주세요.")
