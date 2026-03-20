import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 초기 데이터 설정 (기존 데이터 보존용)
# 브라우저 메모리에 저장되므로, 영구 보존을 원하시면 이 리스트에 직접 추가해두세요.
if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = pd.DataFrame(columns=['날짜', '단가(원)', '금액(원)', '주유량(L)'])

# 2. 모바일 최적화 스타일
st.set_page_config(page_title="주유 지출 관리", layout="centered")
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .delete-btn>div>button { background-color: #ff4b4b; color: white; border: none; height: 2rem; }
    .result-card { 
        background: #f0f7ff; padding: 15px; border-radius: 15px; 
        text-align: center; border: 1px solid #d0e3ff; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⛽ 주유 기록 & 삭제 관리")

# 3. 입력 섹션
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("리터당 단가", min_value=1, value=1650, step=10)
    with c2:
        money = st.number_input("주유 금액", min_value=0, value=50000, step=1000)
    
    calc_l = round(money / price, 2) if price > 0 else 0.0
    st.markdown(f"<div class='result-card'>이번 주유량: <b>{calc_l} L</b></div>", unsafe_allow_html=True)

    if st.button("➕ 데이터 저장하기", type="primary"):
        new_row = pd.DataFrame([{
            '날짜': datetime.now().strftime("%y/%m/%d %H:%M"),
            '단가(원)': price,
            '금액(원)': money,
            '주유량(L)': calc_l
        }])
        st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, new_row], ignore_index=True)
        st.rerun()

# 4. 데이터 시각화 및 개별 삭제 기능
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 지출 추이", "🗑️ 내역 관리/삭제"])

    with tab1:
        # 최근 20회 지출 추이 그래프
        df_20 = st.session_state.fuel_df.tail(20)
        st.subheader("최근 20회 지출 금액")
        st.bar_chart(df_20.set_index('날짜')['금액(원)'])
        
        col_a, col_b = st.columns(2)
        col_a.metric("최근 총액", f"{df_20['금액(원)'].sum():,}")
        col_b.metric("평균 단가", f"{int(df_20['단가(원)'].mean()):,}")

    with tab2:
        st.subheader("기록된 내역 (최신순)")
        # 데이터를 역순으로 표시 (최신 것이 위로)
        display_df = st.session_state.fuel_df.iloc[::-1].copy()
        
        for index, row in display_df.iterrows():
            with st.expander(f"📍 {row['날짜']} | {row['금액(원)']}원 ({row['주유량(L)']}L)"):
                st.write(f"단가: {row['단가(원)']}원")
                # 삭제 버튼 생성 (고유 키 부여)
                if st.button(f"🗑️ 이 항목 삭제", key=f"del_{index}"):
                    st.session_state.fuel_df = st.session_state.fuel_df.drop(index).reset_index(drop=True)
                    st.warning("항목이 삭제되었습니다.")
                    st.rerun()
        
        st.markdown("---")
        if st.button("⚠️ 전체 기록 초기화"):
            if st.checkbox("정말로 모두 삭제하시겠습니까?"):
                st.session_state.fuel_df = pd.DataFrame(columns=['날짜', '단가(원)', '금액(원)', '주유량(L)'])
                st.rerun()
else:
    st.info("표출할 데이터가 없습니다. 먼저 주유 내역을 입력해주세요.")
