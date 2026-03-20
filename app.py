import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh 

# 1. 페이지 설정 및 1초마다 자동 갱신 (시계 흐름용)
st.set_page_config(page_title="차량 관리 가계부", layout="centered")
st_autorefresh(interval=1000, key="fuelevent")

# 세션 상태 초기화 (주행거리 컬럼 추가)
if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = pd.DataFrame(columns=['일시', '주유소', '주행거리(km)', '단가(원)', '금액(원)', '주유량(L)'])

# 2. 한국 시간(KST) 함수
def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

# 3. 디자인 (모바일 최적화 및 다크 모드 시계)
st.markdown("""
    <style>
    .clock-box {
        background: #1e1e1e; color: #00ff00; padding: 15px;
        border-radius: 15px; text-align: center; font-family: monospace;
        margin-bottom: 20px; border: 2px solid #333;
    }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.8rem; font-weight: bold; }
    .res-card { 
        background: #f8f9fa; padding: 15px; border-radius: 15px; 
        text-align: center; border: 1px solid #dee2e6; margin: 10px 0;
    }
    .input-label { font-weight: bold; margin-bottom: 5px; color: #333; }
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

st.title("⛽ 48러 9208 주유기록")

# 4. 입력 섹션
with st.container():
    # 주유소 선택
    station_options = ["oil bank", "SK", "GS 칼텍스", "E1", "기타"]
    selected_station = st.selectbox("📍 주유소 선택", station_options)
    
    final_station_name = selected_station
    if selected_station == "기타":
        final_station_name = st.text_input("주유소 이름을 입력하세요", placeholder="예: 알뜰주유소")
    
    # 주행거리 및 금액 입력
    col_km = st.columns(1)[0]
    with col_km:
        # 마지막 입력된 주행거리를 참고하여 초기값 설정 가능 (데이터가 있을 경우)
        last_km = st.session_state.fuel_df['주행거리(km)'].max() if not st.session_state.fuel_df.empty else 0
        mileage = st.number_input("🛣️ 현재 주행거리 (km)", min_value=0, value=int(last_km), step=1)
        if last_km > 0:
            st.caption(f"이전 기록 주행거리: {last_km:,} km")

    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("단가 (원)", min_value=1, value=1650, step=10)
    with c2:
        money = st.number_input("금액 (원)", min_value=0, value=50000, step=1000)
    
    calc_l = round(money / price, 2) if price > 0 else 0.0
    st.markdown(f"<div class='res-card'>예상 주유량: <b style='color:#007bff; font-size:1.5rem;'>{calc_l} L</b></div>", unsafe_allow_html=True)

    if st.button("🚀 기록 저장하기", type="primary"):
        if selected_station == "기타" and not final_station_name:
            st.error("주유소 이름을 입력해주세요!")
        elif mileage <= 0:
            st.warning("주행거리를 입력해주세요!")
        else:
            save_time = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([{
                '일시': save_time,
                '주유소': final_station_name,
                '주행거리(km)': mileage,
                '단가(원)': price,
                '금액(원)': money,
                '주유량(L)': calc_l
            }])
            st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, new_row], ignore_index=True)
            st.success(f"✅ {final_station_name} ({mileage}km) 저장 완료!")
            st.rerun()

# 5. 추이 분석 및 내역
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 데이터 분석", "📜 기록 관리"])

    with tab1:
        df_recent = st.session_state.fuel_df.tail(20).copy()
        df_recent['라벨'] = df_recent['주유소'] + "(" + pd.to_datetime(df_recent['일시']).dt.strftime('%m/%d') + ")"
        
        st.subheader("🛣️ 주행거리 증가 추이")
        st.line_chart(df_recent.set_index('라벨')['주행거리(km)'])

        st.subheader("💰 지출 금액 추이")
        st.bar_chart(df_recent.set_index('라벨')['금액(원)'], color="#007bff")

    with tab2:
        st.subheader("전체 기록 (최신순)")
        rev_df = st.session_state.fuel_df.iloc[::-1]
        for idx, row in rev_df.iterrows():
            with st.expander(f"📍 {row['주유소']} | {row['주행거리(km)']} km | {row['금액(원)']}원"):
                st.write(f"• 일시: {row['일시']}")
                st.write(f"• 상세: {row['주유량(L)']}L (단가 {row['단가(원)']}원)")
                if st.button(f"기록 삭제", key=f"del_{idx}"):
                    st.session_state.fuel_df = st.session_state.fuel_df.drop(idx).reset_index(drop=True)
                    st.rerun()
else:
    st.info("기록된 데이터가 없습니다.")
