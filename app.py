import streamlit as st
import pandas as pd
from datetime import datetime
import time

# 1. 실시간 갱신을 위한 설정 (1초마다 자동 리프레시)
# 이 기능이 있어야 사용자가 아무것도 안 해도 시간이 흘러갑니다.
def autorefresh(interval_ms):
    st.empty()
    st.write(
        f"""
        <script>
            setTimeout(function(){{
                window.location.reload();
            }}, {interval_ms});
        </script>
        """,
        unsafe_allow_html=True,
    )

# 2. 페이지 설정 및 데이터 초기화
st.set_page_config(page_title="실시간 주유 가계부", layout="centered")

if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = pd.DataFrame(columns=['일시', '단가(원)', '금액(원)', '주유량(L)'])

# 3. 모바일 최적화 CSS
st.markdown("""
    <style>
    .live-time-box {
        font-size: 1.5rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        padding: 15px;
        background: linear-gradient(90deg, #ff4b4b 0%, #ff8a8a 100%);
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        margin-bottom: 25px;
    }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; font-weight: bold; font-size: 1.1rem; }
    .result-card { 
        background: #ffffff; padding: 20px; border-radius: 15px; 
        text-align: center; border: 2px solid #f0f2f6; margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 현재 시간 실시간 표출 (한국 시간 기준)
now = datetime.now()
st.markdown(f"""
    <div class="live-time-box">
        🕒 현재 시간<br>
        <span style="font-size: 2rem;">{now.strftime('%H:%M:%S')}</span><br>
        <span style="font-size: 0.9rem; opacity: 0.8;">{now.strftime('%Y-%m-%d (%a)')}</span>
    </div>
    """, unsafe_allow_html=True)

st.title("⛽ 스마트 주유 기록기")

# 5. 주유 정보 입력 및 계산
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("리터당 단가", min_value=1, value=1650, step=10)
    with c2:
        money = st.number_input("주유 금액", min_value=0, value=50000, step=1000)
    
    calc_l = round(money / price, 2) if price > 0 else 0.0
    
    st.markdown(f"""
        <div class="result-card">
            <div style="color:#666; font-size:0.9rem;">이번 주유량</div>
            <div style="font-size: 2.2rem; color: #1976d2; font-weight: bold;">{calc_l} L</div>
        </div>
        """, unsafe_allow_html=True)

    # 버튼 클릭 시점의 시간을 변수에 고정하여 저장
    if st.button("🚀 지금 이 시간에 저장하기", type="primary"):
        save_moment = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{
            '일시': save_moment,
            '단가(원)': price,
            '금액(원)': money,
            '주유량(L)': calc_l
        }])
        st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, new_row], ignore_index=True)
        st.success(f"✅ {save_moment} 기록 완료!")
        st.rerun()

# 6. 추이 그래프 및 내역 관리
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 지출 추이", "📋 내역 관리"])

    with tab1:
        df_plot = st.session_state.fuel_df.tail(20).copy()
        df_plot['표시시간'] = pd.to_datetime(df_plot['일시']).dt.strftime('%m/%d %H:%M')
        st.subheader("최근 20회 지출 금액")
        st.bar_chart(df_plot.set_index('표시시간')['금액(원)'])

    with tab2:
        rev_df = st.session_state.fuel_df.iloc[::-1]
        for idx, row in rev_df.iterrows():
            with st.expander(f"📍 {row['일시']} | {row['금액(원)']}원"):
                st.write(f"단가: {row['단가(원)']}원 / 주유량: {row['주유량(L)']}L")
                if st.button(f"삭제", key=f"del_{idx}"):
                    st.session_state.fuel_df = st.session_state.fuel_df.drop(idx).reset_index(drop=True)
                    st.rerun()
