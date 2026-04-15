import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")
st.markdown("""
    <style>
    .filter-container { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ddd; }
    .excel-table { border-collapse: collapse; width: 100%; font-size: 11px; border: 2px solid #444; }
    .excel-table td { border: 1px solid #ccc; padding: 5px 8px; }
    .header-col { background-color: #e8eef7; font-weight: bold; width: 140px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. 에러 방지용 안전 데이터 추출 함수 (KeyError 해결사)
def get_val(df, r, c):
    try:
        # 데이터프레임의 실제 크기보다 큰 행/열을 참조하려고 하면 에러 대신 빈칸 반환
        if r < df.shape[0] and c < df.shape[1]:
            val = df.iloc[r, c]
            return str(val).strip() if pd.notna(val) else ""
    except:
        return ""
    return ""

def extract_num(val):
    try:
        n = re.sub(r'[^0-9.]', '', str(val).replace(',', ''))
        return float(n) if n else 0
    except:
        return 0

# 3. 메인 화면 및 파일 업로드
st.title("📂 설비 비교 프로젝트 선정 시스템")
st.write("---")
uploaded_file = st.file_uploader("📊 분석할 엑셀(XLSX) 또는 CSV 파일을 업로드하세요", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # 확장자에 따라 데이터 로드
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None)
        else:
            df = pd.read_excel(uploaded_file, header=None)
        
        st.success(f"✅ 파일을 성공적으로 읽었습니다! (데이터 크기: {df.shape[0]}행 x {df.shape[1]}열)")

        # 4. 검색 필터 UI
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: v_loc = st.selectbox("위치(지역)", ["전체", "서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "강원"])
        with c2: v_year = st.selectbox("준공년도", ["전체", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
        with c3: v_hvac = st.selectbox("냉난방방식", ["전체", "개별가스", "지역난방", "중앙난방", "EHP", "GHP"])
        with c4: v_unit = st.selectbox("세대수 구간", ["전체", "300세대 미만", "300~1000세대", "1000~2000세대", "2000세대 이상"])
        
        c5, c6, c7 = st.columns(3)
        with c5: v_type = st.selectbox("건물유형", ["전체", "공동주택", "주상복합", "오피스텔", "리모델링"])
        with c6: v_area = st.selectbox("연면적(평)", ["전체", "~3만", "3~5만", "5~10만", "10만~"])
        with c7: v_fire = st.selectbox("소방/성능위주", ["전체", "소방", "성능위주"])
        st.markdown('</div>', unsafe_allow_html=True)

        # 5. 검색 및 필터링 로직
        if st.button("🚀 조건에 맞는 프로젝트 조회", use_container_width=True):
            found_indices = []
            # D열(3번 인덱스)부터 2칸씩 이동 (프로젝트/비고 쌍)
            for j in range(3, df.shape[1], 2):
                p_name = get_val(df, 0, j)
                if not p_name or "Unnamed" in p_name: continue

                # 엑셀 구조 정밀 좌표 (에러 방지 get_val 사용)
                row_year = get_val(df, 4, j)      
                row_hvac = get_val(df, 5, j)      
                row_type = get_val(df, 6, j)      
                row_fire_note = get_val(df, 6, j+1) # 건물유형 옆 비고란 확인 (성능위주 등)
                
                # 세대수(7, 8행 합산) 및 연면적(14행)
                unit_val = extract_num(get_val(df, 7, j)) + extract_num(get_val(df, 8, j))
                area_val = extract_num(get_val(df, 14, j))

                # 필터링 조건 계산
                conds = [
                    (v_loc == "전체") or (v_loc in p_name),
                    (v_year == "전체") or (v_year in row_year),
                    (v_hvac == "전체") or (v_hvac in row_hvac),
                    (v_type == "전체") or (v_type in row_type),
                    (v_fire == "전체") or (v_fire in row_fire_note) or (v_fire in row_type)
                ]
                
                # 세대수 조건
                if v_unit != "전체":
                    if "300세대 미만" in v_unit: conds.append(unit_val < 300)
                    elif "300~1000" in v_unit: conds.append(300 <= unit_val <= 1000)
                    elif "1000~2000" in v_unit: conds.append(1000 <= unit_val <= 2000)
                    else: conds.append(unit_val >= 2000)

                # 연면적 조건
                if v_area != "전체":
                    if "~3만" in v_area: conds.append(area_val <= 30000)
                    elif "3~5만" in v_area: conds.append(30001 <= area_val <= 50000)
                    elif "5~10만" in v_area: conds.append(50001 <= area_val <= 100000)
                    else: conds.append(area_val > 100000)

                if all(conds):
                    found_indices.append(j)

            # 6. 결과 시각화
            if found_indices:
                st.success(f"🎯 검색 조건에 맞는 프로젝트 {len(found_indices)}개를 발견했습니다.")
                for col in found_indices:
                    with st.expander(f"📌 {get_val(df, 0, col)}"):
                        html = '<table class="excel-table">'
                        for r in range(df.shape[0]):
                            h1, h2 = get_val(df, r, 0), get_val(df, r, 1)
                            d1, d2 = get_val(df, r, col), get_val(df, r, col+1)
                            if h1 or h2 or d1 or d2:
                                html += f'<tr><td class="header-col">{h1}</td><td class="header-col">{h2}</td>'
                                html += f'<td>{d1}</td><td>{d2}</td></tr>'
                        html += '</table>'
                        st.markdown(html, unsafe_allow_html=True)
            else:
                st.warning("🧐 조건에 맞는 프로젝트가 없습니다. 필터를 조정해보세요.")
                
    except Exception as e:
        st.error(f"⚠️ 데이터 처리 중 오류가 발생했습니다: {e}")
else:
    st.info("💡 파일을 업로드하면 검색 시스템이 활성화됩니다.")
