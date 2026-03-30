import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. 환경 설정 및 데이터 로드 ---
SAVE_FILE = "fuel_logs_v2.csv"

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
st.title("🚗 스마트 차계부")

if 'df_logs' not in st.session_state:
    st.session_state.df_logs = load_data()

# --- 2. 입력 섹션 (실시간 계산 포함) ---
st.subheader("📝 주유 기록 입력")

# 폼(form) 바깥에 입력창을 배치해야 실시간 계산 결과가 바로 보입니다.
col1, col2 = st.columns(2)
with col1:
    distance = st.number_input("주행 거리 (km)", min_value=0.0, step=0.1)
    fuel = st.number_input("주유량 (L)", min_value=0.0, step=0.1)
with col2:
    price_per_liter = st.number_input("리터당 단가 (원)", min_value=0, step=1, value=1600)
    date = st.date_input("주유 날짜", datetime.now())

# 실시간 금액 계산 결과 표시
total_calc = int(fuel * price_per_liter)
if fuel > 0:
    st.info(f"💡 현재 입력된 주유 금액: **{total_calc:,}원**")

# 저장 버튼은 별도로 배치
if st.button("🚀 기록 저장하기"):
    if fuel > 0 and distance > 0:
        efficiency = round(distance / fuel, 2)
        
        new_entry = pd.DataFrame({
            "날짜": [date.strftime("%Y-%m-%d")],
            "주행 거리(km)": [distance],
            "연료량(L)": [fuel],
            "단가(원)": [price_per_liter],
            "총액(원)": [total_calc],
            "연비(km/L)": [efficiency]
        })
        
        st.session_state.df_logs = pd.concat([st.session_state.df_logs, new_entry], ignore_index=True)
        save_data(st.session_state.df_logs)
        st.success(f"✅ 저장되었습니다! (연비: {efficiency} km/L)")
        st.rerun() # 데이터 갱신을 위해 새로고침
    else:
        st.warning("주행 거리와 주유량을 모두 입력해주세요.")

st.divider()

# --- 3. 데이터 확인 및 통계 섹션 ---
if not st.session_state.df_logs.empty:
    df = st.session_state.df_logs
    
    # 상단 요약 지표
    avg_eff = df["연비(km/L)"].mean()
    total_spent = df["총액(원)"].sum()
    total_dist = df["주행 거리(km)"].sum()
    cost_per_km = total_spent / total_dist if total_dist > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("평균 연비", f"{avg_eff:.2f} km/L")
    m2.metric("총 지출액", f"{total_spent:,} 원")
    m3.metric("km당 비용", f"{cost_per_km:.1f} 원/km")

    st.subheader("📋 주유 상세 내역")
    st.dataframe(df.sort_values(by="날짜", ascending=False), use_container_width=True)
    
    with st.expander("데이터 관리"):
        if st.button("🚨 모든 데이터 초기화"):
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            st.session_state.df_logs = pd.DataFrame(columns=["날짜", "주행 거리(km)", "연료량(L)", "단가(원)", "총액(원)", "연비(km/L)"])
            st.rerun()
else:
    st.info("기록된 데이터가 없습니다.")
