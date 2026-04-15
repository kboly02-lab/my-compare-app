import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="설비 비교 프로젝트 선정", layout="wide")

# 2. 안전한 데이터 추출 함수
def get_val(df, r, c):
    try:
        if r < df.shape[0] and c < df.shape[1]:
            val = df.iloc[r, c]
            if pd.isna(val) or str(val).strip().lower() == 'nan':
                return ""
            return str(val).strip()
    except:
        return ""
    return ""

def extract_num(val):
    try:
        n = re.sub(r'[^0-9.]', '', str(val).replace(',', ''))
        return float(n) if n else 0
    except:
        return 0

# 3. 메인 화면
st.title("📂 설비 비교 프로젝트 선정 시스템")
uploaded_file = st.file_uploader("📊 '비교프로젝트_설비' 파일을 업로드해주세요", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None)
        else:
            df = pd.read_excel(uploaded_file, header=None)
        
        st.success("✅ 데이터를 성공적으로 불러왔습니다.")

        # --- 필터 UI ---
        st.markdown('<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        
        loc_list = ["서울", "인천", "경기", "대전", "광주", "대구", "부산", "세종", "강원"]
        with c1: v_loc = st.selectbox("위치", ["전체"] + loc_list + ["기타"])
        
        year_list = ["2020", "2021", "2022", "2023", "2024", "2025", "2026"]
        with c2: v_year = st.selectbox("년도", ["전체"] + year_list + ["기타"])
        
        hvac_list = ["개별가스", "지역난방", "중앙난방", "EHP"]
        with c3: v_hvac = st.selectbox("냉난방방식", ["전체"] + hvac_list + ["기타"])
        
        with c4: v_unit = st.selectbox("세대수", ["전체", "100세대 미만", "101~300세대", "301~500세대", "501~1000세대", "1001~2000세대", "2001~3000세대", "3001세대 이상"])
        
        c5, c6, c7 = st.columns(3)
        type_list = ["공동주택", "주상복합", "오피스텔", "리모델링"]
        with c5: v_type = st.selectbox("건물유형", ["전체"] + type_list + ["기타"])
        
        area_range_list = ["~30000", "30001~50000", "50001~70000", "70001~100000", "100001~200000", "200001~"]
        with c6: v_area = st.selectbox("연면적(평)", ["전체"] + area_range_list + ["기타"])
        
        fire_list = ["소방포함/ 성능위주", "소방포함/ 비성능위주", "소방제외/ 성능위주", "소방제외/ 비성능위주"]
        with c7: v_fire = st.selectbox("소방포함", ["전체"] + fire_list + ["기타"])

        # 🔥 중복 선택 가능하도록 multiselect로 변경
        spec_list = ["우수처리", "중수처리", "연료전지", "지열", "정화조", "사우나", "음식물", "쓰레기", "수영장"]
        v_specs = st.multiselect("특화설비 (중복선택 가능)", ["없음", "기타"] + spec_list)
        
        note_list = ["지하단차", "초고층", "준초고층", "진출입", "산악", "공항", "지하철"]
        v_notes = st.multiselect("특수사항 (중복선택 가능)", ["없음", "기타"] + note_list)
        st.markdown('</div>', unsafe_allow_html=True)

        # 4. 검색 로직
        if st.button("🚀 프로젝트 조회", use_container_width=True):
            found_indices = []
            for j in range(3, df.shape[1], 2):
                p_name = get_val(df, 0, j)
                if not p_name or "Unnamed" in p_name: continue
                
                row_year = get_val(df, 3, j)    # 4행
                row_hvac = get_val(df, 4, j)    # 5행
                row_type = get_val(df, 5, j)    # 6행(D,F,H)
                row_fire = get_val(df, 5, j+1)  # 6행(E,G,I)
                row_unit = extract_num(get_val(df, 6, j)) + extract_num(get_val(df, 7, j)) # 7+8행
                row_area = extract_num(get_val(df, 13, j)) # 14행
                row_spec = get_val(df, 46, j)   # 47행
                row_note = get_val(df, 48, j)   # 49행

                # --- 판정 로직 ---
                m_loc = (v_loc == "전체") or (v_loc in p_name if v_loc != "기타" else not any(x in p_name for x in loc_list))
                m_year = (v_year == "전체") or (v_year in row_year if v_year != "기타" else not any(x in row_year for x in year_list))
                m_hvac = (v_hvac == "전체") or (v_hvac in row_hvac if v_hvac != "기타" else not any(x in row_hvac for x in hvac_list))
                m_type = (v_type == "전체") or (v_type in row_type if v_type != "기타" else not any(x in row_type for x in type_list))
                
                # 소방 판정
                f_in, p_in = "소방" in row_fire, "성능" in row_fire
                if v_fire == "전체": m_fire = True
                elif v_fire == "소방포함/ 성능위주": m_fire = f_in and p_in
                elif v_fire == "소방포함/ 비성능위주": m_fire = f_in and not p_in
                elif v_fire == "소방제외/ 성능위주": m_fire = not f_in and p_in
                elif v_fire == "소방제외/ 비성능위주": m_fire = not f_in and not p_in
                else: m_fire = not (f_in or p_in)

                # 세대수/연면적 판정 (생략 없이 로직 유지)
                m_unit = True
                if v_unit != "전체":
                    if "100세대 미만" in v_unit: m_unit = row_unit < 100
                    elif "101~300" in v_unit: m_unit = 101 <= row_unit <= 300
                    elif "301~500" in v_unit: m_unit = 301 <= row_unit <= 500
                    elif "501~1000" in v_unit: m_unit = 501 <= row_unit <= 1000
                    elif "1001~2000" in v_unit: m_unit = 1001 <= row_unit <= 2000
                    elif "2001~3000" in v_unit: m_unit = 2001 <= row_unit <= 3000
                    else: m_unit = row_unit >= 3001

                m_area = True
                if v_area != "전체":
                    if v_area == "기타": m_area = row_area == 0
                    elif "~30000" in v_area: m_area = row_area <= 30000
                    elif "30001~50000" in v_area: m_area = 30001 <= row_area <= 50000
                    elif "50001~70000" in v_area: m_area = 50001 <= row_area <= 70000
                    elif "70001~100000" in v_area: m_area = 70001 <= row_area <= 100000
                    elif "100001~200000" in v_area: m_area = 100001 <= row_area <= 200000
                    else: m_area = row_area > 200000

                # 🔥 특화설비 중복 판정 (선택한 것 중 하나라도 포함되면 True)
                if not v_specs: m_spec = True
                else:
                    m_spec = False
                    if "없음" in v_specs and (row_spec == "" or row_spec == "0"): m_spec = True
                    if "기타" in v_specs and (row_spec != "" and not any(x in row_spec for x in spec_list)): m_spec = True
                    if any(x in row_spec for x in v_specs if x not in ["없음", "기타"]): m_spec = True

                # 🔥 특수사항 중복 판정 (선택한 것 중 하나라도 포함되면 True)
                if not v_notes: m_note = True
                else:
                    m_note = False
                    if "없음" in v_notes and (row_note == "" or row_note == "0"): m_note = True
                    if "기타" in v_notes and (row_note != "" and not any(x in row_note for x in note_list)): m_note = True
                    if any(x in row_note for x in v_notes if x not in ["없음", "기타"]): m_note = True

                if all([m_loc, m_year, m_hvac, m_unit, m_type, m_area, m_fire, m_spec, m_note]):
                    found_indices.append(j)

            # 결과 출력 (49행까지)
            if found_indices:
                st.success(f"🎯 {len(found_indices)}개의 프로젝트 발견")
                for col in found_indices:
                    with st.expander(f"📌 {get_val(df, 0, col)}"):
                        html = '<table style="width:100%; border-collapse:collapse; font-size:11px; border: 1px solid #444;">'
                        for r in range(49):
                            html += f'<tr><td style="border:1px solid #ccc; background:#e8eef7; font-weight:bold; width:20%;">{get_val(df,r,0)}</td>'
                            html += f'<td style="border:1px solid #ccc; background:#e8eef7; font-weight:bold; width:20%;">{get_val(df,r,1)}</td>'
                            html += f'<td style="border:1px solid #ccc; padding:4px;">{get_val(df,r,col)}</td>'
                            html += f'<td style="border:1px solid #ccc; padding:4px;">{get_val(df,r,col+1)}</td></tr>'
                        st.markdown(html + '</table>', unsafe_allow_html=True)
            else:
                st.warning("🧐 조건에 맞는 프로젝트가 없습니다.")
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")
