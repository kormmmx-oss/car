import streamlit as st
import pandas as pd
from datetime import datetime
import time

# 1. 초기 데이터 설정 (기존 데이터 구조 유지)
if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = pd.DataFrame(columns=['일시', '단가(원)', '금액(원)', '주유량(L)'])

# 2. 페이지 설정 및 모바일 최적화 레이아웃
st.set_page_config(page_title="실시간 주유 가계부", layout="centered")

# CSS 스타일: 시간 표시 및 결과 카드 강조
st.markdown("""
    <style>
    .live-time {
        font-size: 1.3rem;
        font-weight: 800;
        color: #d32f2f;
        text-align: center;
        padding: 10px;
        background-color: #fff5f5;
        border-radius: 10px;
        border: 1px solid #ffcdd2;
        margin-bottom: 20px;
    }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; font-weight: bold; }
    .result-card { 
        background: #f8f9fa; padding: 20px; border-radius: 15px; 
        text-align: center; border: 1px solid #dee2e6; margin: 15px 0;
    }
    .res-val { font-size: 2.2rem; color: #1976d2; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. 실시간 현재 시간 표시 (상단)
# 이 부분은 사용자가 조작할 때마다 현재 시각으로 업데이트됩니다.
now = datetime.now()
current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
st.markdown(f"<div class='live-time'>🕒 현재 시간: {current_time_str}</div>", unsafe_allow_html=True)

st.title("⛽ 스마트 주유 기록기")

# 4. 주유 정보 입력
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("리터당 단가 (원)", min_value=1, value=1650, step=10)
    with col2:
        money = st.number_input("주유 금액 (원)", min_value=0, value=50000, step=1000)
    
    # 실시간 주유량 계산
    calc_l = round(money / price, 2) if price > 0 else 0.0
    
    st.markdown(f"""
        <div class="result-card">
            <div style="color:#666; font-size:0.9rem;">예상 주유량</div>
            <div class="res-val">{calc_l} L</div>
        </div>
        """, unsafe_allow_html=True)

    # 저장 버튼: 클릭 시점의 시간을 데이터에 기록
    if st.button("🚀 현재 시간으로 내역 저장", type="primary"):
        # 버튼을 누른 딱 그 순간의 시간을 캡처
        save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = pd.DataFrame([{
            '일시': save_time,
            '단가(원)': price,
            '금액(원)': money,
            '주유량(L)': calc_l
        }])
        
        # 데이터프레임 합치기
        st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, new_entry], ignore_index=True)
        st.success(f"✅ {save_time} 기록이 완료되었습니다!")
        time.sleep(0.5)
        st.rerun()  # 화면을 새로고침하여 리스트와 그래프에 즉시 반영

# 5. 데이터 시각화 및 관리 (최근 20회 기준)
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 지출 추이 (최근 20회)", "🗑️ 기록 관리"])

    with tab1:
        # 최근 20개 데이터 추출 및 시간 포맷 변경
        df_plot = st.session_state.fuel_df.tail(20).copy()
        df_plot['표시시간'] = pd.to_datetime(df_plot['일시']).dt.strftime('%m/%d %H:%M')
        
        st.subheader("💰 최근 주유 지출 (원)")
        st.bar_chart(df_plot.set_index('표시시간')['금액(원)'], color="#1976d2")
        
        st.subheader("⛽ 최근 주유량 (L)")
        st.line_chart(df_plot.set_index('표시시간')['주유량(L)'], color="#d32f2f")

    with tab2:
        st.subheader("전체 주유 내역 (최신순)")
        # 최신 데이터가 위로 오도록 역순 출력
        rev_df = st.session_state.fuel_df.iloc[::-1].copy()
        
        for idx, row in rev_df.iterrows():
            with st.expander(f"📍 {row['일시']} | {row['금액(원)']}원"):
                st.write(f"• 상세: {row['주유량(L)']} L 주유 (단가 {row['단가(원)']}원)")
                if st.button(f"🗑️ 항목 삭제", key=f"del_{idx}"):
                    st.session_state.fuel_df = st.session_state.fuel_df.drop(idx).reset_index(drop=True)
                    st.rerun()
else:
    st.info("저장된 내역이 없습니다. 정보를 입력하고 저장 버튼을 눌러주세요.")
