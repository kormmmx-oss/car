import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. 설정 및 데이터 로드
DB_FILE = 'gas_history.csv'

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['날짜'] = pd.to_datetime(df['날짜'])
        return df
    return pd.DataFrame(columns=['날짜', '금액', '주유량', '주행거리(k)', '단가', '주유소'])

# 2. 메인 화면 구성
st.set_page_config(page_title="차계부 대시보드", layout="wide")
st.title("🚗 나의 주유 관리 대시보드")

# 사이드바: 데이터 입력창
with st.sidebar:
    st.header("📝 새 주유 기록 입력")
    with st.form("input_form", clear_on_submit=True):
        date = st.date_input("날짜", datetime.now())
        amount = st.number_input("주유 금액 (원)", min_value=0, step=1000)
        liters = st.number_input("주유량 (L)", min_value=0.0, step=0.1)
        odometer = st.number_input("주행거리 (k)", min_value=0.0, step=0.1)
        unit_price = st.number_input("단가 (원/L)", min_value=0, step=1)
        station = st.selectbox("주유소", ["oil", "sk", "e1", "gs", "soil", "oilb"])
        
        submitted = st.form_submit_button("저장하기")
        
        if submitted:
            new_data = pd.DataFrame([[date, amount, liters, odometer, unit_price, station]], 
                                    columns=['날짜', '금액', '주유량', '주행거리(k)', '단가', '주유소'])
            df = load_data()
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("데이터가 성공적으로 저장되었습니다!")

# 3. 대시보드 시각화
df = load_data()

if not df.empty:
    # 상단 요약 지표 (KPI)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 주유 횟수", f"{len(df)} 회")
    col2.metric("총 지출 금액", f"{df['금액'].sum():,} 원")
    col3.metric("평균 단가", f"{int(df['단가'].mean()):,} 원/L")
    col4.metric("총 주유량", f"{df['주유량'].sum():.1f} L")

    st.divider()

    # 차트 영역
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📅 월별 지출 추이")
        df_monthly = df.set_index('날짜').resample('M')['금액'].sum().reset_index()
        fig1 = px.line(df_monthly, x='날짜', y='금액', markers=True, title="월간 주유비 변화")
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("⛽ 주유소별 이용 비중")
        fig2 = px.pie(df, names='주유소', values='금액', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    # 데이터 표 출력
    st.subheader("📜 최근 주유 기록 (최신순)")
    st.dataframe(df.sort_values(by='날짜', ascending=False), use_container_width=True)
else:
    st.info("데이터가 없습니다. 왼쪽 사이드바에서 첫 기록을 입력해 주세요!")
