import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 기존 데이터 복구 및 초기화 (이곳에 기존 데이터를 입력해두면 사라지지 않습니다)
# 예시: ['날짜', '단가(원)', '금액(원)', '주유량(L)']
initial_data = [
    ["2026-03-01 10:00", 1630, 50000, 30.67],
    ["2026-03-05 18:30", 1640, 60000, 36.59],
    ["2026-03-12 09:15", 1650, 45000, 27.27],
    # 여기에 과거 데이터를 ["날짜", 단가, 금액, 주유량] 형식으로 계속 추가하세요.
]

if 'fuel_df' not in st.session_state:
    # 기존 데이터가 있다면 불러오고, 없으면 빈 데이터프레임 생성
    if initial_data:
        st.session_state.fuel_df = pd.DataFrame(initial_data, columns=['날짜', '단가(원)', '금액(원)', '주유량(L)'])
    else:
        st.session_state.fuel_df = pd.DataFrame(columns=['날짜', '단가(원)', '금액(원)', '주유량(L)'])

# 2. 페이지 설정 및 모바일 CSS
st.set_page_config(page_title="주유 지출 분석", layout="centered")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border: 1px solid #eee; padding: 10px; border-radius: 12px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5rem; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("⛽ 주유 지출 & 최근 20회 추이")

# 3. 주유 입력 섹션
with st.expander("➕ 새 주유 기록 입력", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("리터당 단가", min_value=1, value=1650)
    with c2:
        money = st.number_input("주유 금액", min_value=0, value=50000, step=1000)
    
    calc_l = round(money / price, 2) if price > 0 else 0.0
    st.info(f"계산된 주유량: {calc_l} L")

    if st.button("내역 저장하기"):
        new_row = {
            '날짜': datetime.now().strftime("%Y-%m-%d %H:%M"),
            '단가(원)': price,
            '금액(원)': money,
            '주유량(L)': calc_l
        }
        st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("기록 완료!")
        st.rerun()

# 4. 데이터 시각화 (최근 20회)
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    
    # 최근 20회만 필터링
    df_20 = st.session_state.fuel_df.tail(20).copy()
    df_20['날짜_간략'] = pd.to_datetime(df_20['날짜']).dt.strftime('%m/%d')

    tab1, tab2 = st.tabs(["📊 지출 추이", "📜 전체 내역"])

    with tab1:
        st.subheader("최근 20회 지출 금액 (원)")
        st.bar_chart(df_20.set_index('날짜_간략')['금액(원)'])
        
        st.subheader("최근 20회 주유량 (L)")
        st.line_chart(df_20.set_index('날짜_간략')['주유량(L)'])

        # 통계 요약
        col_a, col_b = st.columns(2)
        col_a.metric("최근 총 지출", f"{df_20['금액(원)'].sum():,}")
        col_b.metric("최근 평균 단가", f"{int(df_20['단가(원)'].mean()):,}")

    with tab2:
        st.dataframe(st.session_state.fuel_df.iloc[::-1], use_container_width=True, hide_index=True)
        
        # 데이터 내보내기 버튼 (모바일에서 텍스트로 복사 가능)
        st.download_button(
            "📥 전체 데이터 CSV 다운로드",
            st.session_state.fuel_df.to_csv(index=False).encode('utf-8-sig'),
            "fuel_history.csv",
            "text/csv"
        )
else:
    st.warning("표출할 데이터가 없습니다. 먼저 주유 내역을 입력해주세요.")
