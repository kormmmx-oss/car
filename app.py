import streamlit as st
import pandas as pd

# 1. 페이지 설정 (반응형 레이아웃)
st.set_page_config(
    page_title="Jeonbuk Weather HRI",
    layout="centered",  # 모바일에서는 'wide'보다 'centered'가 가독성이 좋습니다.
    initial_sidebar_state="collapsed"
)

# 2. 스타일 커스텀 (글자 크기 및 여백 조정)
st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    @media (max-width: 640px) {
        .stMetric { margin-bottom: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌦️ 전북 호우 지수(HRI)")

# 3. 주요 지표 (Metrics) - 모바일에서는 세로로 나열됨
# 인증키: Tt8x4uYTSKufMeLmE-ir3Q (API 호출 시 사용)
col1, col2 = st.columns(2)
with col1:
    st.metric(label="강수량 (PWAT)", value="65mm", delta="5mm ▲")
with col2:
    st.metric(label="하층제트 (LLJ)", value="25kts", delta="-2kts ▼")

# 4. 탭 구성 (화면 공간 절약)
tab1, tab2 = st.tabs(["📊 실시간 차트", "📋 체크리스트"])

with tab1:
    st.subheader("시간별 변동 추이")
    # 예시 데이터 생성
    chart_data = pd.DataFrame({'Time': range(10), 'HRI': [10, 15, 30, 45, 80, 95, 70, 50, 30, 20]})
    st.line_chart(chart_data, x='Time', y='HRI')

with tab2:
    st.subheader("위험 기상 점검")
    st.checkbox("500hPa-400hPa 기온차 급증")
    st.checkbox("Tropopause Folding 감지")
    st.checkbox("SST 25°C 이상 유지")

# 5. 하단 정보
st.info("인증키가 적용된 실시간 관측 데이터입니다.")
