import streamlit as st
import pandas as pd
import os
import re
from difflib import SequenceMatcher

# 1. 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 2. 유틸리티 함수
def clean_text(text):
    if pd.isna(text): return ""
    return re.sub(r'[^a-zA-Z0-9가-힣]', '', str(text)).lower()

def is_similar(target, source, threshold=0.6):
    if target == "전체": return True
    t_clean = clean_text(target)
    s_clean = clean_text(source)
    if not t_clean: return True
    if t_clean in s_clean or s_clean in t_clean: return True
    return SequenceMatcher(None, t_clean, s_clean).ratio() >= threshold

def extract_num(val):
    if pd.isna(val): return 0
    try:
        # 숫자와 소수점만 추출
        n = re.sub(r'[^0-9.]', '', str(val))
        return float(n) if n else 0
    except: return 0

@st.cache_data
def load_data():
    # 파일명은 실제 환경에 맞춰 수정 (비교프로젝트_설비.xlsx 또는 csv)
    file_path = "비교프로젝트_설비.xlsx" 
    if not os.path.exists(file_path):
        # 테스트를 위해 업로드된 CSV 경로 대응 (사용자 환경에선 엑셀 파일명 사용)
        file_path = "비교프로젝트_설비.xlsx - Sheet1.csv"
    
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path, header=None)
        else:
            return pd.read_excel(file_path, header=None, engine='openpyxl')
    except Exception as e:
        st.error(f"파일 로드 실패: {e}")
        return None

# 데이터 로드
df = load_data()

if df is not None:
    st.title("📂 설비 비교 프로젝트 선정 시스템")
    
    # [생략] 필터 UI 영역 (기존 코드와 동일하게 유지하되 검색 조건만 매칭)
    # ... (필터 selectbox 부분) ...
    
    # ---------------------------------------------------------
    # 필터 변수 예시 (실제 코드에선 위 Selectbox 결과값 사용)
    # v_loc, v_year, v_hvac, v_unit, v_type, v_area, v_fire, v_spec, v_note
    # ---------------------------------------------------------

    if st.button("🚀 프로젝트 조회", use_container_width=True):
        found_indices = []
        # 실제 데이터는 4번째 열(인덱스 3)부터 2칸씩 프로젝트 존재
        project_cols = [j for j in range(3, len(df.columns), 2)]

        for j in project_cols:
            # 1. 프로젝트명 (2행 -> 인덱스 1)
            p_name = str(df.iloc[1, j]) if pd.notna(df.iloc[1, j]) else ""
            if not p_name.strip() or "공사금액" in p_name: continue

            # 2. 위치 매칭 (프로젝트명에서 찾기)
            m_loc = is_similar(v_loc[:2], p_name) if v_loc != "전체" else True
            
            # 3. 년도 (3행 -> 인덱스 2) - 데이터 확인 결과 3행에 있음
            m_year = is_similar(v_year, str(df.iloc[2, j]))
            
            # 4. 냉난방방식 (4행 -> 인덱스 3)
            m_hvac = is_similar(v_hvac, str(df.iloc[3, j]))
            
            # 5. 세대수 (6행 + 7행 -> 인덱스 5, 6)
            total_u = extract_num(df.iloc[5, j]) + extract_num(df.iloc[6, j])
            # [세대수 매칭 로직 생략 - 기존과 동일]
            
            # 6. 건물유형 (5행 -> 인덱스 4)
            m_type = is_similar(v_type, str(df.iloc[4, j]))

            # 7. 연면적 (13행 -> 인덱스 12)
            area_val = extract_num(df.iloc[12, j])
            # [연면적 매칭 로직 생략 - 기존과 동일]

            # 8. 특화/특수사항 (46행, 48행 -> 인덱스 45, 47)
            # 데이터가 비어있는 경우가 많으므로 '전체'일 때는 무조건 통과하게 처리
            spec_content = str(df.iloc[45, j]) if pd.notna(df.iloc[45, j]) else ""
            m_spec = True if v_spec == "전체" else is_similar(v_spec, spec_content)

            if all([m_loc, m_year, m_hvac, m_type, m_spec]): # 주요 조건 위주 매칭
                found_indices.append(j)

        # 결과 렌더링 (기존 로직 유지)
