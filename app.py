import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. 페이지 설정 및 상태 초기화
st.set_page_config(page_title="실시간 주유 가계부", layout="centered")

# 데이터 저장을 위한 세션 상태 초기화 (새로고침 전까지 유지)
if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = pd.DataFrame(columns=['일시', '단가(원)', '금액(원)', '주유량(L)'])

# 2. 한국 시간(KST) 계산 함수
def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

# 3. 모바일 최적화 및 실시간 시각화 CSS
st.markdown("""
    <style>
    .live-clock {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        color: #00ff00;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        font-family: 'Courier New', monospace;
        border: 2px solid #444;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; font-weight: bold; }
    .result-card { 
        background: #ffffff; padding: 20px; border-radius: 15px; 
        text-align: center; border: 1px solid #eee; margin: 15px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 실시간 시간 표출 (JS를 이용한 클라이언트 사이드 시계)
# Streamlit 서버 부하 없이 브라우저에서 직접 시간이 흐르게 합니다.
st.markdown(f"""
    <div class="live-clock" id="clock-container">
        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">🇰🇷 대한민국 표준시 (KST)</div>
        <div id="live-time" style="font-size: 2.2rem; font-weight: 900;">{get_kst_now().strftime('%H:%M:%S')}</div>
        <div style="font-size: 1rem; margin-top: 5px;">{get_kst_now().strftime('%Y-%m-%d (%a)')}</div>
    </div>
    <script>
        function updateClock() {{
            const now = new Date();
            // 서버 시간차를 고려하여 한국 시간으로 계산
            const kst = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (9 * 3600000));
            const hours = String(kst.getHours()).padStart(2, '0');
            const minutes = String(kst.getMinutes()).padStart(2, '0');
            const seconds = String(kst.getSeconds()).padStart(2, '0');
            document.getElementById('live-time').innerText = hours + ":" + minutes + ":" + seconds;
        }}
        setInterval(updateClock, 1000);
    </script>
    """, unsafe_allow_html=True)

st.title("⛽ 스마트 주유 기록기")

# 5. 입력 및 주유량 계산
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("리터당 단가 (원)", min_value=1, value=1650, step=10)
    with c2:
        money = st.number_input("주유 금액 (원)", min_value=0, value=50000, step=1000)
    
    calc_l = round(money / price, 2) if price > 0 else 0.0
    
    st.markdown(f"""
        <div class="result-card">
            <div style="color:#666; font-size:0.9rem;">이번 예상 주유량</div>
            <div style="font-size: 2.5rem; color: #007bff; font-weight: bold;">{calc_l} L</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🚀 현재 시간으로 기록 저장", type="primary"):
        save_time = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{
            '일시': save_time,
            '단가(원)': price,
            '금액(원)': money,
            '주유량(L)': calc_l
        }])
        st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, new_row], ignore_index=True)
        st.success(f"✅ {save_time} 저장되었습니다!")
        time.sleep(0.5)
        st.rerun()

# 6. 추이 분석 및 내역 관리 (최근 20회)
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 지출 추이", "🗑️ 내역 삭제"])

    with tab1:
        df_plot = st.session_state.fuel_df.tail(20).copy()
        df_plot['시각'] = pd.to_datetime(df_plot['일시']).dt.strftime('%m/%d %H:%M')
        
        st.subheader("💰 최근 20회 지출 금액")
        st.bar_chart(df_plot.set_index('시각')['금액(원)'])
        
        st.subheader("⛽ 최근 20회 주유량")
        st.line_chart(df_plot.set_index('시각')['주유량(L)'])

    with tab2:
        st.subheader("기록 관리 (최신순)")
        rev_df = st.session_state.fuel_df.iloc[::-1]
        for idx, row in rev_df.iterrows():
            with st.expander(f"📍 {row['일시']} | {row['금액(원)']}원"):
                st.write(f"단가: {row['단가(원)']}원 / 주유량: {row['주유량(L)']}L")
                if st.button(f"이 항목 삭제", key=f"del_{idx}"):
                    st.session_state.fuel_df = st.session_state.fuel_df.drop(idx).reset_index(drop=True)
                    st.rerun()
else:
    st.info("기록된 주유 데이터가 없습니다.")
