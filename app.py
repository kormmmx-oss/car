import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. 환경 설정 및 데이터 로드 ---
SAVE_FILE = "fuel_logs_v2.csv"  # 단가가 추가되었으므로 파일명을 구분합니다.

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            return pd.read_csv(SAVE_FILE)
        except Exception:
            return pd.DataFrame(columns=["날짜", "주행 거리(km)", "연료량(L)", "단가(원)", "총액(원)", "연비(km/L)"])
    else:
        return pd.DataFrame(columns=["날짜", "주행 거리(km)", "연료량(L)", "단가(원)", "총액(원)", "연비(km/L)"])

def save_data(df):
    df.to_csv(SAVE_FILE, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="차계부 & 연비 계산기", layout="centered")
st.title("🚗 스마트 차계부 (연비 & 비용)")

if 'df_logs' not in st.session_state:
    st.session_state.df_logs = load_data()

# --- 2. 입력 섹션 ---
with st.form("fuel_input_form", clear_on_submit=True):
    st.subheader("📝 주유 기록 입력")
    
    col1, col2 = st.columns(2)
    with col1:
        distance = st.number_input("주행 거리 (km)", min_value=0.0, step=0.1)
        fuel = st.number_input("주유량 (L)", min_value=0.1, step=0.1)
    with col2:
        price_per_liter = st.number_input("리터당 단가 (원)", min_value=0, step=1, value=1600)
        date = st.date_input("주유 날짜", datetime.now())
    
    submit_btn = st.form_submit_button("기록 저장하기")

# --- 3. 계산 및 저장 로직 ---
if submit_btn:
    if fuel > 0:
        efficiency = round(distance / fuel, 2)  # 연비 계산
        total_price = int(fuel * price_per_liter) # 총 주유 금액 계산
        
        new_entry = pd.DataFrame({
            "날짜": [date.strftime("%Y-%m-%d")],
            "주행 거리(km)": [distance],
            "연료량(L)": [fuel],
            "단가(원)": [price_per_liter],
            "총액(원)": [total_price],
            "연비(km/L)": [efficiency]
        })
        
        st.session_state.df_logs = pd.concat([st.session_state.df_logs, new_entry], ignore_index=True)
        save_data(st.session_state.df_logs)
        
        st.success(f"✅ 저장 완료! (총액: {total_price:,}원 / 연비: {efficiency} km/L)")
    else:
        st.error("주유량은 0보다 커야 합니다.")

st.divider()

# --- 4. 데이터 확인 및 통계 섹션 ---
if not st.session_state.df_logs.empty:
    df = st.session_state.df_logs
    
    # 상단 요약 지표 (Metric)
    avg_eff = df["연비(km/L)"].mean()
    total_spent = df["총액(원)"].sum()
    # 1km당 비용 계산 (총액 합계 / 주행거리 합계)
    cost_per_km = total_spent / df["주행 거리(km)"].sum() if df["주행 거리(km)"].sum() > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("평균 연비", f"{avg_eff:.2f} km/L")
    m2.metric("총 지출액", f"{total_spent:,} 원")
    m3.metric("km당 비용", f"{cost_per_km:.1f} 원/km")

    # 상세 내역 표
    st.subheader("📋 주유 상세 내역")
    st.dataframe(df.sort_values(by="날짜", ascending=False), use_container_width=True)
    
    # 삭제 기능
    with st.expander("데이터 관리"):
        if st.button("🚨 모든 데이터 초기화"):
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            st.session_state.df_logs = pd.DataFrame(columns=["날짜", "주행 거리(km)", "연료량(L)", "단가(원)", "총액(원)", "연비(km/L)"])
            st.rerun()
else:
    st.info("기록된 데이터가 없습니다.")
