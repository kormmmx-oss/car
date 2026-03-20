import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
# 반드시 requirements.txt에 streamlit-autorefresh 추가 필요
from streamlit_autorefresh import st_autorefresh 

# 1. 페이지 설정 및 1초마다 자동 갱신 설정
st.set_page_config(page_title="실시간 주유 기록", layout="centered")

# 1000ms(1초)마다 이 앱을 처음부터 다시 실행시켜 시간을 흐르게 합니다.
st_autorefresh(interval=1000, key="daterefresh")

# 데이터 초기화
if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = pd.DataFrame(columns=['일시', '단가(원)', '금액(원)', '주유량(L)'])

# 2. 한국 시간(KST) 계산 함수
def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

# 3. 디자인 (모바일 최적화)
st.markdown("""
    <style>
    .clock-vibe {
        background: #000000;
        color: #00ff00;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        font-family: 'Courier New', monospace;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        margin-bottom: 25px;
    }
    .stButton>button { width: 100%; border-radius: 15px; height: 3.8rem; font-weight: bold; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# 4. 상단 실시간 시계 (1초마다 숫자가 바뀝니다)
kst_now = get_kst_now()
st.markdown(f"""
    <div class="clock-vibe">
        <div style="font-size: 3rem; font-weight: 900;">{kst_now.strftime('%H:%M:%S')}</div>
        <div style="font-size: 1rem; opacity: 0.8;">{kst_now.strftime('%Y-%m-%d (%a)')}</div>
    </div>
    """, unsafe_allow_html=True)

st.title("⛽ 스마트 주유 기록기")

# 5. 입력창 및 자동 계산
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("리터당 단가", min_value=1, value=1650, step=10)
    with c2:
        money = st.number_input("주유 금액", min_value=0, value=50000, step=1000)
    
    calc_l = round(money / price, 2) if price > 0 else 0.0
    st.metric("이번 예상 주유량", f"{calc_l} L")

    if st.button("🚀 지금 이 시간에 저장", type="primary"):
        save_time = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{
            '일시': save_time,
            '단가(원)': price,
            '금액(원)': money,
            '주유량(L)': calc_l
        }])
        st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, new_row], ignore_index=True)
        st.toast(f"✅ {save_time} 저장 완료!")

# 6. 통계 및 내역 관리
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 지출 추이", "🗑️ 내역 삭제"])
    
    with tab1:
        df_20 = st.session_state.fuel_df.tail(20).copy()
        df_20['시각'] = pd.to_datetime(df_20['일시']).dt.strftime('%H:%M')
        st.bar_chart(df_20.set_index('시각')['금액(원)'])
        
    with tab2:
        rev_df = st.session_state.fuel_df.iloc[::-1]
        for idx, row in rev_df.iterrows():
            with st.expander(f"📍 {row['일시']} | {row['금액(원)']}원"):
                if st.button(f"삭제하기", key=f"del_{idx}"):
                    st.session_state.fuel_df = st.session_state.fuel_df.drop(idx).reset_index(drop=True)
                    st.rerun()
