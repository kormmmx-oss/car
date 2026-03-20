import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. 페이지 설정
st.set_page_config(page_title="차량 관리 대시보드", layout="wide")

# 2. 전체 데이터셋 (제공된 모든 데이터 통합)
# 형식: [날짜, 지출금액, 주유량, 구간거리(k), 단가]
raw_data = [
    ["20260314", 19182, 21.629, 184.0, 916], ["20260310", 53183, 58.060, 506.1, 916],
    ["20260227", 51122, 55.810, 503.4, 916], ["20260215", 50776, 55.430, 491.2, 916],
    ["20260204", 48127, 52.540, 472.8, 916], ["20260125", 28250, 30.650, 270.8, 916],
    ["20260120", 53036, 57.900, 494.6, 916], ["20260109", 53073, 57.940, 503.1, 916],
    ["20251227", 54420, 59.410, 498.5, 916], ["20251217", 47067, 51.383, 476.4, 916],
    ["20251208", 42004, 44.495, 461.3, 944], ["20251202", 57587, 61.359, 562.1, 923],
    ["20251128", 11904, 13.300, 104.9, 895], ["20251125", 22868, 24.985, 235.1, 916],
    ["20251122", 51314, 56.020, 445.8, 916], ["20251111", 54735, 59.745, 571.5, 916],
    ["20210511", 50897, 58.43, 588.0, 871] # 예시용 과거 데이터
    # (실제 파일에는 사용자가 주신 모든 리스트를 이 형식으로 채우시면 됩니다)
]

# 3. 데이터프레임 생성 및 연비(FE) 계산
df = pd.DataFrame(raw_data, columns=['Date', 'Amount', 'Liters', 'Distance', 'UnitPrice'])
df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')

# 리터당 거리 (연비 = 구간거리 / 주유량)
df['Efficiency'] = df['Distance'] / df['Liters']

df = df.sort_values('Date', ascending=False)

# 4. 메인 대시보드
st.title("⛽ 스마트 주유 및 연비 관리")

# 상단 요약 지표
avg_eff = df['Efficiency'].mean()
total_dist = df['Distance'].sum()
total_amt = df['Amount'].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("총 주유 횟수", f"{len(df)}회")
c2.metric("총 주행 거리", f"{total_dist:,.1f} km")
c3.metric("평균 연비", f"{avg_eff:,.2f} km/L")
c4.metric("총 지출액", f"{total_amt:,.0f}원")

st.divider()

# 5. 그래프 시각화 (연비 추이)
st.subheader("📈 리터당 주행거리 (km/L) 변화")
fig, ax = plt.subplots(figsize=(10, 4))
# 최근 30개 데이터 시각화
plot_df = df.head(30).sort_values('Date')
ax.plot(plot_df['Date'], plot_df['Efficiency'], marker='s', linestyle='-', color='#10b981', label='km/L')
ax.axhline(avg_eff, color='red', linestyle='--', alpha=0.5, label='Average') # 평균선

ax.set_ylabel("Efficiency (km/L)")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))
plt.xticks(rotation=45)
ax.legend()
ax.grid(True, alpha=0.2)
st.pyplot(fig)

# 6. 데이터 테이블
st.subheader("📋 상세 기록")
# 테이블용 포맷팅 (소수점 정리)
display_df = df.copy()
display_df['Efficiency'] = display_df['Efficiency'].map('{:,.2f} km/L'.format)
display_df['Amount'] = display_df['Amount'].map('{:,.0f}원'.format)
st.dataframe(display_df[['Date', 'Amount', 'Liters', 'Distance', 'Efficiency', 'UnitPrice']], use_container_width=True)

# 7. 연도별 통계
st.subheader("📅 연도별 성과")
df['Year'] = df['Date'].dt.year
yearly = df.groupby('Year').agg({
    'Amount': 'sum',
    'Distance': 'sum',
    'Liters': 'sum'
}).reset_index()
yearly['Avg_Efficiency'] = yearly['Distance'] / yearly['Liters']
st.table(yearly.style.format({
    'Amount': '{:,.0f}',
    'Distance': '{:,.1f}',
    'Avg_Efficiency': '{:,.2f}'
}))
