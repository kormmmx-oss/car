import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh 

# 1. 페이지 설정 및 1초마다 자동 갱신 (시계 흐름용)
st.set_page_config(page_title="주유소 기록부", layout="centered")
st_autorefresh(interval=1000, key="fuelevent")

# 데이터 저장 구조 변경 (주유소 컬럼 추가)
if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = pd.DataFrame(columns=['일시', '주유소', '단가(원)', '금액(원)', '주유량(L)'])

# 2. 한국 시간(KST) 함수
def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

# 3. 모바일 최적화 디자인
st.markdown("""
    <style>
    .clock-box {
        background: #1e1e1e; color: #00ff00; padding: 15px;
        border-radius: 15px; text-align: center; font-family: monospace;
        margin-bottom: 20px; border: 2px solid #333;
    }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; font-weight: bold; }
    .res-card { 
        background: #ffffff; padding: 15px; border-radius: 15px; 
        text-align: center; border: 1px solid #eee; margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 실시간 시계 표출
kst_now = get_kst_now()
st.markdown(f"""
    <div class="clock-box">
        <div style="font-size: 2.5rem; font-weight: 900;">{kst_now.strftime('%H:%M:%S')}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">{kst_now.strftime('%Y-%m-%d %a')}</div>
    </div>
    """, unsafe_allow_html=True)

st.title("⛽ 스마트 주유 기록기")

# 4. 입력 섹션 (주유소 이름 추가)
with st.container():
    # 주유소 이름 입력 (최근 입력값 기억 기능은 없으나 텍스트로 입력)
    gas_station = st.text_input("📍 주유소 이름", placeholder="예: 전주 행복주유소")
    
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("리터당 단가", min_value=1, value=1650, step=10)
    with c2:
        money = st.number_input("주유 금액", min_value=0, value=50000, step=1000)
    
    calc_l = round(money / price, 2) if price > 0 else 0.0
    st.markdown(f"<div class='res-card'>예상 주유량: <b style='color:#007bff; font-size:1.5rem;'>{calc_l} L</b></div>", unsafe_allow_html=True)

    if st.button("🚀 주유 내역 저장하기", type="primary"):
        if not gas_station:
            st.warning("주유소 이름을 입력해주세요!")
        else:
            save_time = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([{
                '일시': save_time,
                '주유소': gas_station,
                '단가(원)': price,
                '금액(원)': money,
                '주유량(L)': calc_l
            }])
            st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, new_row], ignore_index=True)
            st.success(f"✅ {gas_station} 저장 완료!")
            st.rerun()

# 5. 추이 분석 및 내역 (주유소 정보 포함)
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 지출 추이", "📜 상세 내역"])

    with tab1:
        df_recent = st.session_state.fuel_df.tail(20).copy()
        # 그래프 라벨에 주유소 이름도 살짝 포함
        df_recent['라벨'] = df_recent['주유소'] + "(" + pd.to_datetime(df_recent['일시']).dt.strftime('%m/%d') + ")"
        
        st.subheader("최근 20회 지출 금액")
        st.bar_chart(df_recent.set_index('라벨')['금액(원)'])

    with tab2:
        st.subheader("기록 관리 (최신순)")
        rev_df = st.session_state.fuel_df.iloc[::-1]
        for idx, row in rev_df.iterrows():
            with st.expander(f"📍 {row['주유소']} | {row['금액(원)']}원"):
                st.write(f"• 일시: {row['일시']}")
                st.write(f"• 상세: {row['주유량(L)']}L (단가 {row['단가(원)']}원)")
                if st.button(f"이 기록 삭제", key=f"del_{idx}"):
                    st.session_state.fuel_df = st.session_state.fuel_df.drop(idx).reset_index(drop=True)
                    st.rerun()
else:
    st.info("기록된 주유 내역이 없습니다.")
