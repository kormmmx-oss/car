import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. 환경 설정 및 데이터 로드 ---
SAVE_FILE = "fuel_logs.csv"

def load_data():
    """기존 CSV 파일을 불러오거나 없으면 새 데이터프레임 생성"""
    if os.path.exists(SAVE_FILE):
        try:
            return pd.read_csv(SAVE_FILE)
        except Exception:
            return pd.DataFrame(columns=["날짜", "주행 거리(km)", "연료량(L)", "연비(km/L)"])
    else:
        return pd.DataFrame(columns=["날짜", "주행 거리(km)", "연료량(L)", "연비(km/L)"])

def save_data(df):
    """데이터프레임을 CSV 파일로 저장"""
    df.to_csv(SAVE_FILE, index=False, encoding='utf-8-sig')

# 앱 레이아웃 설정
st.set_page_config(page_title="자동차 연비 관리자", layout="centered")
st.title("🚗 자동차 연비 영구 기록장")

# 데이터 불러오기
if 'df_logs' not in st.session_state:
    st.session_state.df_logs = load_data()

# --- 2. 입력 섹션 ---
with st.form("fuel_input_form", clear_on_submit=True):
    st.subheader("📝 새로운 주유 기록 입력")
    
    col1, col2 = st.columns(2)
    with col1:
        distance = st.number_input("주행 거리 (km)", min_value=0.0, step=0.1, help="마지막 주유 이후 주행한 거리를 입력하세요.")
    with col2:
        fuel = st.number_input("사용 연료량 (L)", min_value=0.1, step=0.1, help="주유한 양을 리터 단위로 입력하세요.")
    
    date = st.date_input("주유 날짜", datetime.now())
    submit_btn = st.form_submit_button("데이터 저장 및 연비 계산")

# --- 3. 계산 및 저장 로직 ---
if submit_btn:
    if fuel > 0:
        # 연비 계산 (거리 / 연료)
        efficiency = round(distance / fuel, 2)
        
        # 새로운 데이터 행 생성
        new_entry = pd.DataFrame({
            "날짜": [date.strftime("%Y-%m-%d")],
            "주행 거리(km)": [distance],
            "연료량(L)": [fuel],
            "연비(km/L)": [efficiency]
        })
        
        # 데이터 병합 및 저장
        st.session_state.df_logs = pd.concat([st.session_state.df_logs, new_entry], ignore_index=True)
        save_data(st.session_state.df_logs)
        
        st.success(f"✅ 저장되었습니다! 이번 연비는 **{efficiency} km/L** 입니다.")
    else:
        st.error("연료량은 0보다 커야 합니다.")

# 시각적 구분선 (에러가 났던 지점 수정)
st.divider()

# --- 4. 데이터 확인 및 통계 섹션 ---
st.subheader("📊 연비 기록 내역")

if not st.session_state.df_logs.empty:
    # 데이터 출력 (최신 날짜가 위로 오도록 정렬)
    display_df = st.session_state.df_logs.copy()
    display_df = display_df.sort_values(by="날짜", ascending=False)
    st.dataframe(display_df, use_container_width=True)
    
    # 주요 통계 지표 계산
    avg_eff = st.session_state.df_logs["연비(km/L)"].mean()
    total_dist = st.session_state.df_logs["주행 거리(km)"].sum()
    
    m1, m2 = st.columns(2)
    m1.metric("누적 총 주행 거리", f"{total_dist:,.1f} km")
    m2.metric("전체 평균 연비", f"{avg_eff:.2f} km/L")

    # 삭제 옵션 (확인용 익스팬더)
    with st.expander("데이터 관리"):
        if st.button("🚨 모든 기록 삭제"):
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            st.session_state.df_logs = pd.DataFrame(columns=["날짜", "주행 거리(km)", "연료량(L)", "연비(km/L)"])
            st.warning("모든 데이터가 삭제되었습니다. 페이지를 새로고침하세요.")
            st.rerun()
else:
    st.info("기록된 데이터가 아직 없습니다. 위 양식을 통해 첫 데이터를 입력해 보세요!")
