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
    .excel-table { border-collapse: collapse; width: 100%; font-size: 13px; border: 2px solid #444; }
    .excel-table th, .excel-table td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    .excel-table th { background-color: #f2f2f2; font-weight: bold; text-align: center; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 15%; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "비교프로젝트_설비.xlsx"
    if not os.path.exists(file_name): return None
    # 엑셀을 헤더 없이 읽어 행 인덱스를 엑셀 번호와 동기화 (엑셀 1행 = 인덱스 0)
    return pd.read_excel(file_name, header=None)

def extract_number(value):
    if pd.isna(value): return 0
    try:
        # 숫자와 소수점만 추출
        num_str = re.sub(r'[^0-9.]', '', str(value))
        return float(num_str) if num_str else 0
    except: return 0

df = load_data()

if df is None:
    st.error("❌ '비교프로젝트_설비.xlsx' 파일을 찾을 수 없습니다.")
else:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    # 4. 상단 필터 영역 (이미지 리스트와 100% 일치화)
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
        # 프로젝트는 D열(3번 인덱스)부터 2열씩 간격으로 배치됨
        project_cols = [j for j in range(3, len(df.columns), 2)]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        start_time = time.time()

        for i, j in enumerate(project_cols):
            # 진행 상태 업데이트
            elapsed = time.time() - start_time
            avg = elapsed / (i + 1)
            rem = avg * (len(project_cols) - (i + 1))
            progress_bar.progress((i + 1) / len(project_cols))
            status_text.markdown(f"⏳ **분석 중 ({i+1}/{len(project_cols)})** | 남은 시간: **{rem:.1f}초**")
            
            # 프로젝트명 (2행 -> 인덱스 1)
            p_name = str(df.iloc[1, j]) if pd.notna(df.iloc[1, j]) else ""
            if not p_name.strip(): continue

            # --- [보완된 9가지 조건 매칭 로직] ---
            
            # 1. 위치: 프로젝트명에 해당 지역명이 있는지 확인
            match_loc = (v_loc == "전체") or (v_loc[:2] in p_name)

            # 2. 년도 (4행 -> 인덱스 3): 작성일자 등에서 년도 추출
            date_val = str(df.iloc[3, j])
            match_year = (v_year == "전체") or (v_year in date_val)

            # 3. 냉난방방식 (5행 -> 인덱스 4): 개별가스, 지역 등 텍스트 매칭
            hvac_val = str(df.iloc[4, j])
            match_hvac = (v_hvac == "전체") or (v_hvac in hvac_val)

            # 4. 세대수 (7, 8행 합계 -> 인덱스 6, 7): 아파트 + 오피스텔 세대수 합산
            u1, u2 = extract_number(df.iloc[6, j]), extract_number(df.iloc[7, j])
            total_u = u1 + u2
            if v_unit == "전체": match_unit = True
            elif v_unit == "100세대 미만": match_unit = total_u < 100
            elif v_unit == "101~300세대": match_unit = 101 <= total_u <= 300
            elif v_unit == "301~500세대": match_unit = 301 <= total_u <= 500
            elif v_unit == "501~1000세대": match_unit = 501 <= total_u <= 1000
            elif v_unit == "1001~2000세대": match_unit = 1001 <= total_u <= 2000
            elif v_unit == "2001~3000세대": match_unit = 2001 <= total_u <= 3000
            elif v_unit == "3001세대 이상": match_unit = total_u >= 3001
            else: match_unit = True

            # 5. 건물유형 (6행 -> 인덱스 5)
            type_val = str(df.iloc[5, j])
            match_type = (v_type == "전체") or (v_type in type_val)

            # 6. 연면적 (14행 합계 -> 인덱스 13)
            area_val = extract_number(df.iloc[13, j])
            if v_area == "전체": match_area = True
            elif v_area == "~30,000평": match_area = area_val <= 30000
            elif v_area == "30,001~50,000평": match_area = 30001 <= area_val <= 50000
            elif v_area == "50,001~70,000평": match_area = 50001 <= area_val <= 70000
            elif v_area == "70,001~100,000평": match_area = 70001 <= area_val <= 100000
            elif v_area == "100,001~200,000평": match_area = 100001 <= area_val <= 200000
            elif v_area == "200,001~300,000평": match_area = 200001 <= area_val <= 300000
            elif v_area == "300,001평~": match_area = area_val > 300000
            else: match_area = True

            # 7. 소방포함 (6행 비고 -> 인덱스 5, j+1열)
            fire_val = str(df.iloc[5, j+1])
            match_fire = (v_fire == "전체") or (v_fire[:4] in fire_val)

            # 8. 특화설비 (47행 -> 인덱스 46)
            spec_val = str(df.iloc[46, j]) if pd.notna(df.iloc[46, j]) else ""
            match_spec = (v_spec == "전체") or (v_spec[:2] in spec_val)

            # 9. 특수사항 (49행 -> 인덱스 48): 지하단차 등 확인
            # 본문열(j)과 비고열(j+1) 모두 검사하여 누락 방지
            note_combined = str(df.iloc[48, j]) + str(df.iloc[48, j+1])
            match_note = (v_note == "전체") or (v_note[:2] in note_combined)

            # 모든 조건이 충족될 때만 결과 리스트에 추가
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
                    html += f'<tr><th colspan="4" style="background-color:#4472c4; color:white; font-size:16px;">{p_title}</th></tr>'
                    html += '<tr><th>구분1</th><th>구분2</th><th>내용</th><th>비고</th></tr>'
                    # 엑셀의 주요 데이터 범위(1~50행)를 테이블로 생성
                    for r in range(50):
                        v1 = df.iloc[r, 0] if pd.notna(df.iloc[r, 0]) else ""
                        v2 = df.iloc[r, 1] if pd.notna(df.iloc[r, 1]) else ""
                        v3 = df.iloc[r, col_idx] if pd.notna(df.iloc[r, col_idx]) else ""
                        v4 = df.iloc[r, col_idx+1] if pd.notna(df.iloc[r, col_idx+1]) else ""
                        html += f'<tr><td class="header-col">{v1}</td><td class="header-col">{v2}</td><td>{v3}</td><td>{v4}</td></tr>'
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("🧐 조건에 맞는 프로젝트가 없습니다. 필터를 조정해보세요.")
