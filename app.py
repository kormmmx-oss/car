import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 파일 경로 설정 (데이터 저장용)
DATA_FILE = "fuel_history.csv"

# 2. 데이터 불러오기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['날짜', '단가(원)', '금액(원)', '주유량(L)'])

# 3. 데이터 저장 함수
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 4. 페이지 설정
st.set_page_config(page_title="주유 기록장", layout="centered")

# 데이터 초기화
if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = load_data()

# 모바일 UI 스타일
st.markdown("""
    <style>
    .stNumberInput label { font-size: 1rem !important; font-weight: bold; }
    .result-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #3498db;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .res-val { font-size: 2.2rem; font-weight: bold; color: #2980b9; }
    .stButton>button { width: 100%; border-radius: 12px; background-color: #3498db; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("⛽ 스마트 주유 기록기")

# 5. 입력 및 실시간 계산
col1, col2 = st.columns(2)
with col1:
    price = st.number_input("단가 (원)", min_value=1, value=1650, step=10)
with col2:
    money = st.number_input("금액 (원)", min_value=0, value=50000, step=1000)

calc_fuel = round(money / price, 2) if price > 0 else 0.0

st.markdown(f"""
    <div class="result-card">
        <div style="color: #555;">이번 주유 예상량</div>
        <div class="res-val">{calc_fuel} L</div>
    </div>
    """, unsafe_allow_html=True)

if st.button("🚀 주유 내역 저장하기"):
    new_entry = {
        '날짜': datetime.now().strftime("%Y-%m-%d %H:%M"),
        '단가(원)': price,
        '금액(원)': money,
        '주유량(L)': calc_fuel
    }
    # 데이터 업데이트 및 파일 저장
    st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, pd.DataFrame([new_entry])], ignore_index=True)
    save_data(st.session_state.fuel_df)
    st.success("내역이 안전하게 저장되었습니다!")
    st.rerun()

# 6. 저장된 데이터 표시 섹션
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 주유 추이", "📜 전체 내역"])

    with tab1:
        st.subheader("최근 주유 패턴")
        # 최근 10개 기록 그래프
        recent_df = st.session_state.fuel_df.tail(10)
        st.line_chart(recent_df.set_index('날짜')['주유량(L)'], use_container_width=True)
        
        total_sum = st.session_state.fuel_df['금액(원)'].sum()
        st.metric("누적 총 주유 금액", f"{total_sum:,} 원")

    with tab2:
        st.subheader("상세 기록 리스트")
        # 최신순 정렬 표시
        st.dataframe(
            st.session_state.fuel_df.iloc[::-1], 
            use_container_width=True, 
            hide_index=True
        )
        
        # 데이터 삭제 기능
        if st.checkbox("데이터 관리 도구 열기"):
            if st.button("⚠️ 전체 기록 삭제"):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.session_state.fuel_df = pd.DataFrame(columns=['날짜', '단가(원)', '금액(원)', '주유량(L)'])
                st.warning("모든 데이터가 삭제되었습니다.")
                st.rerun()
else:
    st.info("저장된 데이터가 없습니다. 주유 후 기록 버튼을 눌러보세요.")
