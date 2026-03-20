import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. 한국 시간(KST) 계산 함수
def get_kst_now():
    # 서버 시간(UTC)에 9시간을 더해 한국 시간으로 변환
    utc_now = datetime.utcnow()
    kst_now = utc_now + timedelta(hours=9)
    return kst_now

# 2. 페이지 설정 및 초기화
st.set_page_config(page_title="한국 시간 주유 기록기", layout="centered")

if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = pd.DataFrame(columns=['일시', '단가(원)', '금액(원)', '주유량(L)'])

# 3. 모바일 최적화 CSS
st.markdown("""
    <style>
    .live-time-box {
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #2c3e50 0%, #000000 100%);
        border-radius: 15px;
        margin-bottom: 20px;
        border: 2px solid #ff4b4b;
    }
    .res-card { 
        background: #ffffff; padding: 20px; border-radius: 15px; 
        text-align: center; border: 1px solid #ddd; margin: 15px 0;
    }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. 상단 실시간 한국 시간 표시
kst_now = get_kst_now()
st.markdown(f"""
    <div class="live-time-box">
        🇰🇷 대한민국 표준시 (KST)<br>
        <span style="font-size: 2.2rem;">{kst_now.strftime('%H:%M:%S')}</span><br>
        <span style="font-size: 1rem; opacity: 0.8;">{kst_now.strftime('%Y년 %m월 %d일')}</span>
    </div>
    """, unsafe_allow_html=True)

st.title("⛽ 스마트 주유 기록기")

# 5. 입력 및 자동 계산
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("리터당 단가 (원)", min_value=1, value=1650, step=10)
    with c2:
        money = st.number_input("주유 금액 (원)", min_value=0, value=50000, step=1000)
    
    calc_l = round(money / price, 2) if price > 0 else 0.0
    
    st.markdown(f"""
        <div class="res-card">
            <div style="color:#666; font-size:0.9rem;">이번 예상 주유량</div>
            <div style="font-size: 2.2rem; color: #ff4b4b; font-weight: bold;">{calc_l} L</div>
        </div>
        """, unsafe_allow_html=True)

    # 저장 버튼 (클릭 시 한국 시간으로 기록)
    if st.button("🚀 현재 한국 시간으로 기록", type="primary"):
        # 저장하는 시점의 한국 시간을 다시 계산
        save_kst = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{
            '일시': save_kst,
            '단가(원)': price,
            '금액(원)': money,
            '주유량(L)': calc_l
        }])
        st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, new_row], ignore_index=True)
        st.success(f"✅ {save_kst} 기록 완료!")
        time.sleep(0.5)
        st.rerun()

# 6. 추이 분석 및 내역
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 최근 20회 추이", "📋 내역 관리"])

    with tab1:
        df_plot = st.session_state.fuel_df.tail(20).copy()
        # 그래프 하단 시간 가독성 개선
        df_plot['시각'] = pd.to_datetime(df_plot['일시']).dt.strftime('%m/%d %H:%M')
        
        st.subheader("최근 주유 금액 변동")
        st.bar_chart(df_plot.set_index('시각')['금액(원)'], color="#2c3e50")
        
        st.subheader("최근 주유량 변동")
        st.line_chart(df_plot.set_index('시각')['주유량(L)'], color="#ff4b4b")

    with tab2:
        rev_df = st.session_state.fuel_df.iloc[::-1]
        for idx, row in rev_df.iterrows():
            with st.expander(f"📍 {row['일시']} | {row['금액(원)']}원"):
                st.write(f"단가: {row['단가(
