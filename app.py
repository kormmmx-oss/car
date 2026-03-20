import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_autorefresh import st_autorefresh  # 실시간 갱신용 라이브러리
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 설정 및 실시간 리프레시 설정 (1초마다 자동 갱신)
st.set_page_config(page_title="실시간 주유 가계부", layout="centered")

# 1초(1000ms)마다 이 코드를 다시 실행하여 시계를 흐르게 함
count = st_autorefresh(interval=1000, key="fueleventcounter")

def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

# 2. 구글 시트 연결 (URL을 본인의 시트 주소로 변경하세요)
SHEET_URL = "여기에_본인의_구글시트_URL을_넣으세요"
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 모바일 최적화 CSS
st.markdown("""
    <style>
    .live-clock-container {
        background: linear-gradient(135deg, #000000 0%, #434343 100%);
        color: #00ff00;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        margin-bottom: 25px;
        border: 2px solid #333;
    }
    .time-main { font-size: 2.8rem; font-weight: 900; font-family: 'Courier New', monospace; line-height: 1; }
    .date-sub { font-size: 1rem; opacity: 0.8; margin-top: 5px; }
    .stMetric { background-color: #ffffff; border-radius: 15px; padding: 10px; border: 1px solid #eee; }
    .stButton>button { width: 100%; border-radius: 15px; height: 3.8rem; font-size: 1.2rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. 실시간 한국 시간 표출 (1초마다 변함)
kst_now = get_kst_now()
st.markdown(f"""
    <div class="live-clock-container">
        <div class="time-main">{kst_now.strftime('%H:%M:%S')}</div>
        <div class="date-sub">🇰🇷 {kst_now.strftime('%Y년 %m월 %d일 (%a)')}</div>
    </div>
    """, unsafe_allow_html=True)

st.title("⛽ 스마트 주유 기록기")

# 5. 입력 및 실시간 계산
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("리터당 단가 (원)", min_value=1, value=1650)
    with c2:
        money = st.number_input("주유 금액 (원)", min_value=0, value=50000, step=1000)
    
    calc_l = round(money / price, 2) if price > 0 else 0.0
    st.metric(label="이번 예상 주유량", value=f"{calc_l} L", delta_color="normal")

    # 저장 버튼
    if st.button("🚀 현재 시간으로 기록 저장", type="primary"):
        save_time = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 데이터 저장 로직
        new_data = pd.DataFrame([{
            "일시": save_time,
            "단가(원)": price,
            "금액(원)": money,
            "주유량(L)": calc_l
        }])
        
        try:
            existing_data = conn.read(spreadsheet=SHEET_URL)
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_data)
            st.success(f"✅ {save_time} 저장 완료!")
        except:
            st.error("구글 시트 연결을 확인해주세요.")

# 6. 추이 분석 (최신순)
try:
    df = conn.read(spreadsheet=SHEET_URL)
    if not df.empty:
        st.markdown("---")
        df_20 = df.tail(20)
        df_20['시각'] = pd.to_datetime(df_20['일시']).dt.strftime('%H:%M')
        
        st.subheader("📊 최근 지출 추이 (20회)")
        st.bar_chart(df_20.set_index('시각')['금액(원)'], color="#4F8BF9")
        
        with st.expander("📜 전체 내역 보기"):
            st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
except:
    pass
