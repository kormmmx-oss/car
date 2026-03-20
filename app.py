import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. 페이지 설정
st.set_page_config(page_title="차량 관리 대시보드", layout="wide")

# 2. 전체 데이터셋 (제공된 모든 기록 포함)
# [날짜, 지출금액, 주유량, 구간거리(k), 단가]
raw_data = [
    ["20260314", 19182, 21.629, 184.0, 916], ["20260310", 53183, 58.060, 506.1, 916],
    ["20260227", 51122, 55.810, 503.4, 916], ["20260215", 50776, 55.430, 491.2, 916],
    ["20260204", 48127, 52.540, 472.8, 916], ["20260125", 28250, 30.650, 270.8, 916],
    ["20260120", 53036, 57.900, 494.6, 916], ["20260109", 53073, 57.940, 503.1, 916],
    ["20251227", 54420, 59.410, 498.5, 916], ["20251217", 47067, 51.383, 476.4, 916],
    ["20251208", 42004, 44.495, 461.3, 944], ["20251202", 57587, 61.359, 562.1, 923],
    ["20251128", 11904, 13.300, 104.9, 895], ["20251125", 22868, 24.985, 235.1, 916],
    ["20251122", 51314, 56.020, 445.8, 916], ["20251111", 54735, 59.745, 571.5, 916],
    ["20251031", 54015, 58.975, 584.5, 916], ["20251021", 51249, 55.949, 509.0, 916],
    ["20251009", 48273, 52.700, 491.8, 916], ["20251001", 49849, 54.420, 509.2, 916],
    ["20250926", 23495, 25.650, 224.9, 916], ["20250923", 52560, 57.379, 446.1, 916]
]

# 3. 데이터프레임 변환 및 전처리
df = pd.DataFrame(raw_data, columns=['Date', 'Amount', 'Liters', 'Distance', 'UnitPrice'])
df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
df['Efficiency'] = df['Distance'] / df['Liters']  # km/L 계산

# 전체 데이터를 날짜 내림차순(최신순)으로 정렬
df = df.sort_values('Date', ascending=False)

# 4. 메인 화면 구성
st.title("⛽ 최신 주유 및 연비 분석 (Recent 20)")

# 상단 요약 (최근 20회 기준 통계)
recent_20 = df.head(20)
avg_eff_20 = recent_20['Efficiency'].mean()
total_amt_20 = recent_20['Amount'].sum()

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("최근 20회 총 지출", f"{total_amt_20:,.0f}원")
with c2:
    st.metric("최근 20회 평균 연비", f"{avg_eff_20:.2f} km/L")
with c3:
    st.metric("최신 주유 단가", f"{recent_20.iloc[0]['UnitPrice']}원")

st.divider()

# 5. 그래프 시각화 (최근 20회 추세)
st.subheader("📊 최근 20회 주유 금액 및 연비 추이")
col_chart1, col_chart2 = st.columns(2)

# 그래프용 데이터는 날짜 오름차순으로 변경 (왼쪽->오른쪽 흐름)
plot_df = recent_20.sort_values('Date')

with col_chart1:
    st.write("**주유 금액 변화 (원)**")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(plot_df['Date'], plot_df['Amount'], marker='o', color='#2563eb', linewidth=2)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=45)
    ax1.grid(True, alpha=0.2)
    st.pyplot(fig1)

with col_chart2:
    st.write("**연비 변화 (km/L)**")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(plot_df['Date'], plot_df['Efficiency'], marker='s', color='#10b981', linewidth=2)
    ax2.axhline(avg_eff_20, color='red', linestyle='--', alpha=0.5) # 평균선
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=45)
    ax2.grid(True, alpha=0.2)
    st.pyplot(fig2)

# 6. 상세 테이블
st.subheader("📋 최근 주유 상세 내역")
st.dataframe(recent_20[['Date', 'Amount', 'Liters', 'Distance', 'Efficiency', 'UnitPrice']].style.format({
    'Amount': '{:,.0f}원',
    'Efficiency': '{:.2f} km/L',
    'Distance': '{:.1f} km'
}), use_container_width=True)
