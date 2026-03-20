import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 및 상태 초기화
st.set_page_config(page_title="내 차 주유 가계부", layout="centered")

if 'fuel_history' not in st.session_state:
    # 예시 데이터 초기값 (리스트 형태)
    st.session_state.fuel_history = pd.DataFrame(columns=['날짜', '단가(원)', '금액(원)', '주유량(L)'])

# 2. 모바일 최적화 스타일 (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4CAF50; color: white; }
    .result-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #4CAF50;
        margin-bottom: 20px;
    }
    .result-value { font-size: 2.5rem; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

st.title("⛽ 주유 기록기")

# 3. 입력 섹션
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("리터당 단가(원)", min_value=0, value=1650, step=10)
    with col2:
        money = st.number_input("주유 금액(원)", min_value=0, value=50000, step=1000)

    # 주유량 계산
    fuel_amount = round(money / price, 2) if price > 0 else 0.0

    st.markdown(f"""
        <div class="result-box">
            <div style="color: #666;">계산된 주유량</div>
            <div class="result-value">{fuel_amount} L</div>
        </div>
        """, unsafe_allow_html=True)

    # 주유 기록 버튼
    if st.button("📝 현재 주유 내역 저장"):
        new_data = {
            '날짜': datetime.now().strftime("%m-%d %H:%M"),
            '단가(원)': price,
            '금액(원)': money,
            '주유량(L)': fuel_amount
        }
        st.session_state.fuel_history = pd.concat([st.session_state.fuel_history, pd.DataFrame([new_data])], ignore_index=True)
        st.success("기록이 저장되었습니다!")

# 4. 분석 및 그래프 섹션
if not st.session_state.fuel_history.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 주유 추이 그래프", "📜 상세 내역"])

    with tab1:
        st.subheader("최근 주유량 변동")
        # 선형 그래프 표시 (최근 기록 기준)
        st.line_chart(st.session_state.fuel_history.set_index('날짜')['주유량(L)'], use_container_width=True)
        
        st.subheader("주유 금액 합계")
        total_spent = st.session_state.fuel_history['금액(원)'].sum()
        st.info(f"총 주유 누적 금액: {total_spent:,} 원")

    with tab2:
        st.subheader("전체 주유 로그")
        # 모바일에서 보기 편하도록 최신순으로 정렬하여 표시
        st.dataframe(st.session_state.fuel_history.iloc[::-1], use_container_width=True, hide_index=True)
        
        if st.button("❌ 전체 기록 삭제"):
            st.session_state.fuel_history = pd.DataFrame(columns=['날짜', '단가(원)', '금액(원)', '주유량(L)'])
            st.rerun()
else:
    st.info("아직 저장된 주유 내역이 없습니다. 위 버튼을 눌러 첫 기록을 남겨보세요!")
