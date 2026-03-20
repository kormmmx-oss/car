import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
from datetime import datetime

# 1. 전체 데이터 로드 (여기에 처음에 주신 긴 텍스트를 모두 붙여넣으세요)
RAW_DATA = """
20210511  50897  58.43L  588.0k  871
... (중략: 모든 데이터를 여기에 복사하세요) ...
20260314  19182 21.629L 184.0k 916 oil
"""

DB_FILE = 'gas_history.csv'

def parse_all_records(text):
    data_list = []
    # 한 줄씩 읽어서 숫자와 텍스트를 정밀하게 추출
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 정규식으로 숫자 및 소수점만 추출 (날짜, 금액, 주유량, 주행거리, 단가 순서)
        # 문자열 내에서 숫자 형태(소수점 포함)를 모두 찾아 리스트로 만듭니다.
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
        
        if len(numbers) >= 5:
            try:
                # 주유소 브랜드 추출 (영문자 조합)
                station_match = re.search(r'[a-zA-Z]+[0-9]*$', line)
                station = station_match.group() if station_match else "oil"
                
                data_list.append({
                    '날짜': pd.to_datetime(numbers[0], format='%Y%m%d'),
                    '금액': int(numbers[1]),
                    '주유량': float(numbers[2]),
                    '주행거리': float(numbers[3]),
                    '단가': int(numbers[4]),
                    '주유소': station.lower()
                })
            except: continue
            
    return pd.DataFrame(data_list)

def get_data():
    # 매번 최신 데이터를 확인하기 위해 텍스트 파싱을 우선합니다.
    # 만약 파일 저장만 원하시면 아래 로직을 조정할 수 있습니다.
    df = parse_all_records(RAW_DATA)
    df = df.sort_values('날짜', ascending=True)
    return df

# 2. 화면 구성
st.set_page_config(page_title="통합 주유 대시보드", layout="wide")
st.title("🚗 전 기간 주유 데이터 분석 (2021-2026)")

df = get_data()

# 3. 상단 지표 (당월 현황)
current_date = datetime.now()
this_month_df = df[(df['날짜'].dt.year == current_date.year) & (df['날짜'].dt.month == current_date.month)]

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("이번 달 지출", f"{int(this_month_df['금액'].sum()):,}원")
with m2:
    st.metric("총 기록 수", f"{len(df)}건")
with m3:
    st.metric("평균 단가", f"{int(df['단가'].mean()):,}원")
with m4:
    st.metric("총 주행거리", f"{df['주행거리'].max() - df['주행거리'].min():,.1f}km")

st.divider()

# 4. 차트 영역
c1, c2 = st.columns(2)

with c1:
    st.subheader("📅 연도별 주유비 지출액")
    df_yearly = df.copy()
    df_yearly['연도'] = df_yearly['날짜'].dt.year
    yearly_chart = df_yearly.groupby('연도')['금액'].sum().reset_index()
    fig1 = px.bar(yearly_chart, x='연도', y='금액', text_auto=',.0f', color='연도')
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("📈 월별 주유비 변동 추이")
    df_monthly = df.set_index('날짜').resample('M')['금액'].sum().reset_index()
    fig2 = px.line(df_monthly, x='날짜', y='금액', markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# 5. 전체 데이터 리스트 표출
st.subheader("📜 전체 주유 기록 리스트")
# 필터 기능 추가 (연도별)
years = ["전체"] + sorted(df['날짜'].dt.year.unique().tolist(), reverse=True)
selected_year = st.selectbox("조회 연도 선택", years)

if selected_year != "전체":
    display_df = df[df['날짜'].dt.year == selected_year].copy()
else:
    display_df = df.copy()

display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d')
st.dataframe(display_df.sort_values('날짜', ascending=False), use_container_width=True, height=600)
