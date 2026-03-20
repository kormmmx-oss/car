import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. 페이지 설정
st.set_page_config(page_title="차량 관리 대시보드", layout="wide")

# 2. 데이터 초기화 (최초 실행 시 1회만 실행)
if 'gas_df' not in st.session_state:
    raw_data = [
        ["20260314", 19182, 21.629, 184.0, 916], ["20260310", 53183, 58.060, 506.1, 916],
        ["20260227", 51122, 55.810, 503.4, 916], ["20260215", 50776, 55.430, 491.2, 916],
        ["20260204", 48127, 52.540, 472.8, 916], ["20260125", 28250, 30.650, 270.8, 916],
        ["20260120", 53036, 57.900, 494.6, 916], ["20260109", 53073, 57.940, 503.1, 916],
        ["20251227", 54420, 59.410, 498.5, 916], ["20251217", 47067, 51.383, 476.4, 916],
        ["20251208", 42004, 44.495, 461.3, 944], ["20251202", 57587, 61.359, 562.1, 923],
        ["20251128", 11904, 13.300, 104.9, 895], ["20251125", 22868, 24.985, 235.1, 916],
        ["20251122", 51314, 56.020, 445.8, 916], ["20251111", 54735, 59.745, 571.5, 916]
    ]
    df = pd.DataFrame(raw_data, columns=['Date', 'Amount', 'Liters', 'Distance', 'UnitPrice'])
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df['Efficiency'] = df['Distance'] / df['Liters']
    st.session_state.gas_df = df.sort_values('Date', ascending=False)

# 3. [핵심] 주유 입력란 (상단 배치)
st.title("⛽ 스마트 주유 관리 시스템")
with st.expander("➕ 새 주유 기록 입력하기", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1: input_date = st.date_input("날짜")
    with c2: input_amt = st.number_input("금액(원)", step=1000, value=50000)
    with c3: input_lit = st.number_input("주유량(L)", step=0.1, value=50.0)
    with c4: input_dist = st.number_input("주행거리(km)", step=0.1, value=500.0)
    
    if st.button("기록 추가하기", use_container_width=True):
        new_row = pd.DataFrame({
            'Date': [pd.to_datetime(input_date)],
            'Amount': [input_amt],
            'Liters': [input_lit],
            'Distance': [input_dist],
            'UnitPrice': [round(input_amt / input_lit) if input_lit > 0 else 0],
            'Efficiency': [input_dist / input_lit if input_lit > 0 else 0]
        })
        st.session_state.gas_df = pd.concat([new_row, st.session_state.gas_df]).sort_values('Date', ascending=False)
        st.success("기록이 추가되었습니다!")
        st.rerun()

st.divider()

# 4. 데이터 분석 및 그래프
df = st.session_state.gas_df
recent_20 = df.head(20).sort_values('Date') # 그래프용 오름차순

st.subheader("📊 최근 20회 트렌드")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.write("**주유 지출 (원)**")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(recent_20['Date'], recent_20['Amount'], marker='o', color='#2563eb')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=45)
    st.pyplot(fig1)

with col_chart2:
    st.write("**연비 (km/L)**")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(recent_20['Date'], recent_20['Efficiency'], marker='s', color='#10b981')
    ax2.axhline(recent_20['Efficiency'].mean(), color='red', linestyle='--')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# 5. 상세 테이블
st.subheader("📋 전체 내역")
st.dataframe(df.style.format({
    'Amount': '{:,.0f}원',
    'Efficiency': '{:.2f} km/L',
    'Distance': '{:.1f} km',
    'Date': lambda x: x.strftime('%Y-%m-%d')
}), use_container_width=True)
