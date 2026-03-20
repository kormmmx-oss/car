import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
from datetime import datetime

# 1. 기존 텍스트 데이터 (제공해주신 데이터 요약본 - 파싱 로직 포함)
RAW_DATA = """
20210511  50897  58.43L  588.0k  871
20210525  50216  57.67L  592.9k  871
20260310  53183 58.060L 506.1k 916 oil
20260314  19182 21.629L 184.0k 916 oil
""" # (여기에 전달해주신 전체 텍스트를 넣으시면 됩니다)

DB_FILE = 'gas_history.csv'

# 텍스트 데이터를 데이터프레임으로 변환하는 함수
def parse_raw_text(text):
    data_list = []
    lines = text.strip().split('\n')
    for line in lines:
        parts = re.split(r'\s+', line.strip())
        if len(parts) >= 5:
            try:
                data_list.append({
                    '날짜': pd.to_datetime(parts[0], format='%Y%m%d'),
                    '금액': int(parts[1]),
                    '주유량': float(parts[2].replace('L', '').replace('l', '')),
                    '주행거리(k)': float(parts[3].upper().replace('K', '')),
                    '단가': int(parts[4]),
                    '주유소': parts[5] if len(parts) > 5 else 'oil'
                })
            except: continue
    return pd.DataFrame(data_list)

# 데이터 로드 로직 (파일이 없으면 텍스트에서 생성)
def get_full_data():
    if not os.path.exists(DB_FILE):
        df = parse_raw_text(RAW_DATA)
        df.to_csv(DB_FILE, index=False)
        return df
    df = pd.read_csv(DB_FILE)
    df['날짜'] = pd.to_datetime(df['날짜'])
    return df

# 2. 메인 화면 구성
st.set_page_config(page_title="차계부 통합 대시보드", layout="wide")
st.title("📊 통합 주유 관리 대시보드")

df = get_full_data()

# 사이드바: 데이터 입력 및 관리
with st.sidebar:
    st.header("📝 새 기록 추가")
    with st.form("input_form", clear_on_submit=True):
        date = st.date_input("날짜", datetime.now())
        amount = st.number_input("금액 (원)", min_value=0, step=1000)
        liters = st.number_input("주유량 (L)", min_value=0.0, step=0.1)
        odometer = st.number_input("주행거리 (k)", min_value=0.0, step=0.1)
        unit_price = st.number_input("단가", min_value=0, step=1)
        station = st.selectbox("주유소", ["oil", "sk", "e1", "gs", "soil", "oilb"])
        if st.form_submit_button("저장"):
            new_row = pd.DataFrame([[date, amount, liters, odometer, unit_price, station]], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

# 3. 시각화 (기존 데이터 포함)
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("누적 주유 금액", f"{df['금액'].sum():,}원")
    col2.metric("총 주유량", f"{df['주유량'].sum():.1f}L")
    col3.metric("평균 단가", f"{int(df['단가'].mean()):,}원")

    # 연도별 지출 차트
    df['연도'] = df['날짜'].dt.year
    yearly_cost = df.groupby('연도')['금액'].sum().reset_index()
    fig = px.bar(yearly_cost, x='연도', y='금액', title="연도별 주유비 지출액", text_auto=',.0f')
    st.plotly_chart(fig, use_container_width=True)

    # 전체 기록 표 (최신순)
    st.subheader("📜 전체 주유 기록 목록")
    st.dataframe(df.sort_values('날짜', ascending=False), use_container_width=True)
