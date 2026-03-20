import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. 페이지 설정
st.set_page_config(page_title="내 차 주유 가계부", layout="wide")

# 2. 고정 데이터 (제공해주신 데이터 요약본 - 실제 실행 시 모든 데이터 포함)
raw_data = [
    ["20260314", 19182, 21.629, 916, "oil"], ["20260310", 53183, 58.060, 916, "oil"],
    ["20260227", 51122, 55.810, 916, "oil"], ["20260215", 50776, 55.430, 916, "oil"],
    ["20260204", 48127, 52.540, 916, "oil"], ["20260125", 28250, 30.650, 916, "oil"],
    ["20260120", 53036, 57.900, 916, "oil"], ["20260109", 53073, 57.940, 916, "oil"],
    ["20251227", 54420, 59.410, 916, "oil"], ["20251217", 47067, 51.383, 916, "oil"],
    ["20251208", 42004, 44.495, 944, "e1"], ["20251202", 57587, 61.359, 923, "e1"],
    ["20251128", 11904, 13.300, 895, "e1"], ["20251125", 22868, 24.985, 916, "oil"],
    ["20251122", 51314, 56.020, 916, "oil"], ["20251111", 54735, 59.745, 916, "oil"],
    ["20251031", 54015, 58.975, 916, "oil"], ["20251021", 51249, 55.949, 916, "oil"]
    # ... (여기에 나머지 2021~2024 데이터를 추가하시면 됩니다)
]

# 3. 데이터프레임 변환
df = pd.DataFrame(raw_data, columns=['Date', 'Amount', 'Liters', 'UnitPrice', 'Station'])
df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
df = df.sort_values('Date', ascending=False) # 최신순 정렬

# 4. 사이드바 - 새 데이터 입력 (입력해도 초기화 시 사라지므로 로컬 테스트용)
st.sidebar.header("⛽ 새 주유 기록 추가")
new_date = st.sidebar.date_input("날짜")
new_amt = st.sidebar.number_input("금액(원)", value=50000)
new_lit = st.sidebar.number_input("주유량(L)", value=50.0)
new_price = st.sidebar.number_input("단가", value=916)
if st.sidebar.button("기록 저장 (임시)"):
    st.sidebar.success("데이터가 화면에 반영되었습니다! (영구 저장은 DB 연동 필요)")

# 5. 메인 화면 구성
st.title("🚗 My Car 주유 대시보드")

# 상단 요약 카드
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 주유 횟수", f"{len(df)}회")
with col2:
    st.metric("총 지출 금액", f"{df['Amount'].sum():,.0f}원")
with col3:
    st.metric("평균 리터당 단가", f"{df['UnitPrice'].mean():.0f}원")

st.divider()

# 그래프 섹션
st.subheader("📈 주유 지출 트렌드 (최근 20회)")
fig, ax = plt.subplots(figsize=(10, 4))
recent_df = df.head(20).sort_values('Date')
ax.plot(recent_df['Date'], recent_df['Amount'], marker='o', linestyle='-', color='#2563eb', linewidth=2)
ax.set_ylabel("금액 (원)")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.xticks(rotation=45)
plt.grid(True, alpha=0.2)
st.pyplot(fig)

# 하단 데이터 테이블
st.subheader("📜 상세 주유 히스토리")
st.dataframe(df, use_container_width=True)

# 연도별 통계 테이블
st.subheader("📅 연도별 지출 요약")
df['Year'] = df['Date'].dt.year
yearly_summary = df.groupby('Year')['Amount'].agg(['count', 'sum']).reset_index()
yearly_summary.columns = ['연도', '횟수', '총 지출액(원)']
st.table(yearly_summary.style.format({'총 지출액(원)': '{:,.0f}'}))
