import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
from datetime import datetime

# 1. 전체 데이터 로드 및 파싱 (제공해주신 모든 데이터 포함)
RAW_DATA = """
20210511  50897  58.43L  588.0k  871
20210525  50216  57.67L  592.9k  871
... (중략: 여기에 처음 주신 100여 개의 데이터를 모두 복사해서 넣으세요) ...
20260310  53183 58.060L 506.1k 916 oil
20260314  19182 21.629L 184.0k 916 oil
"""

DB_FILE = 'gas_history.csv'

def parse_raw_text(text):
    data_list = []
    lines = text.strip().split('\n')
    for line in lines:
        # 공백이 여러 개인 경우를 대비해 정규식 사용
        parts = re.split(r'\s+', line.strip())
        if len(parts) >= 5:
            try:
                # 날짜 처리
                date_val = pd.to_datetime(parts[0], format='%Y%m%d')
                # 주유량 숫자만 추출 (L 제거)
                liters = float(re.sub(r'[lL]', '', parts[2]))
                # 누적거리 숫자만 추출 (k, K 제거)
                odo = float(re.sub(r'[kK]', '', parts[3]))
                
                data_list.append({
                    '날짜': date_val,
                    '금액': int(parts[1]),
                    '주유량': liters,
                    '누적거리': odo,
                    '단가': int(parts[4]),
                    '주유소': parts[5] if len(parts) > 5 else 'oil'
                })
            except Exception as e: continue
    return pd.DataFrame(data_list)

def get_data():
    if not os.path.exists(DB_FILE):
        df = parse_raw_text(RAW_DATA)
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)
        df['날짜'] = pd.to_datetime(df['날짜'])
    return df

# 2. 화면 구성
st.set_page_config(page_title="월간 주유 대시보드", layout="wide")
st.title("⛽ 월간 주유 관리 및 전체 데이터 현황")

df = get_data()
current_month = datetime.now().month
current_year = datetime.now().year

# 3. 상단 지표 (누적 -> 이번 달 기준)
this_month_df = df[(df['날짜'].dt.year == current_year) & (df['날짜'].dt.month == current_month)]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(f"{current_month}월 총 지출", f"{this_month_df['금액'].sum():,}")
with col2:
    st.metric(f"{current_month}월 주유량", f"{this_month_df['주유량'].sum():.1f} L")
with col3:
    st.metric(f"{current_month}월 평균 단가", f"{int(this_month_df['단가'].mean()) if not this_month_df.empty else 0:,}")
with col4:
    st.metric(f"{current_month}월 주유 횟수", f"{len(this_month_df)}회")

st.divider()

# 4. 차트 영역
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📅 월별 지출 추이 (전체 기간)")
    # 월별로 데이터 그룹화
    df_monthly = df.set_index('날짜').resample('M')['금액'].sum().reset_index()
    fig1 = px.line(df_monthly, x='날짜', y='금액', markers=True, 
                  labels={'금액': '주유비(원)', '날짜': '연도-월'})
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("⛽ 주유소 선호도")
    fig2 = px.pie(df, names='주유소', values='금액', hole=0.3)
    st.plotly_chart(fig2, use_container_width=True)

# 5. 전체 데이터 표출 (정렬 및 필터 기능 포함)
st.subheader("📜 전체 주유 기록 (최신순)")
# 날짜 형식 예쁘게 출력
display_df = df.sort_values('날짜', ascending=False).copy()
display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d')
st.dataframe(display_df, use_container_width=True, height=500)

# 6. 데이터 내려받기 (백업용)
csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button("📥 전체 데이터 CSV 다운로드", csv, "gas_data_backup.csv", "text/csv")
