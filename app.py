import streamlit as st

# 1. 페이지 설정 (모바일 브라우저 최적화)
st.set_page_config(
    page_title="스마트 주유 계산기",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 모바일 맞춤형 디자인 (CSS)
st.markdown("""
    <style>
    /* 전체 배경 및 여백 조절 */
    .main { background-color: #f9f9f9; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* 입력창 라벨 스타일 */
    .stNumberInput label { font-size: 1.1rem !important; font-weight: bold; color: #333; }
    
    /* 결과 박스 디자인 */
    .result-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px 20px;
        border-radius: 20px;
        text-align: center;
        margin-top: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .result-label { font-size: 1.2rem; opacity: 0.9; margin-bottom: 10px; }
    .result-value { font-size: 3rem; font-weight: 800; }
    .result-unit { font-size: 1.5rem; margin-left: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⛽ 주유량 계산기")
st.write("단가와 금액을 입력하면 주유량이 자동 계산됩니다.")

# 3. 입력 섹션 (세로로 배치하여 터치 편의성 증대)
# 단가 입력
input_price = st.number_input(
    "💰 리터당 단가 (원)", 
    min_value=0, 
    value=1650, 
    step=10,
    format="%d"
)

# 주유 금액 입력
input_money = st.number_input(
    "💵 주유할 금액 (원)", 
    min_value=0, 
    value=50000, 
    step=1000,
    format="%d"
)

# 4. 계산 로직
if input_price > 0:
    total_liters = input_money / input_price
else:
    total_liters = 0.0

# 5. 결과 표시 (모바일 강조형)
st.markdown(f"""
    <div class="result-container">
        <div class="result-label">예상 주유량</div>
        <div class="result-value">
            {total_liters:.2f}<span class="result-unit">L</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 6. 하단 부가 기능 (인증키 등)
st.markdown("---")
with st.expander("🔑 시스템 정보"):
    st.info(f"현재 설정 단가: {input_price:,}원 / 주유 금액: {input_money:,}원")
    st.code("인증키: Tt8x4uYTSKufMeLmE-ir3Q")
    st.caption("v1.0.0 | Mobile Optimized")
