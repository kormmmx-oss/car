import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh 

# 1. 페이지 설정 및 1초마다 자동 갱신
st.set_page_config(page_title="차량 연비 관리자", layout="centered")
st_autorefresh(interval=1000, key="fuelevent")

# 세션 상태 초기화 (연비 컬럼 추가)
if 'fuel_df' not in st.session_state:
    st.session_state.fuel_df = pd.DataFrame(columns=['일시', '주유소', '주행거리(km)', '주행차이(km)', '단가(원)', '금액(원)', '주유량(L)', '연비(km/L)'])

# 2. 한국 시간(KST) 함수
def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

# 3. 디자인 (모바일 최적화)
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
    .efficiency-val { font-size: 2rem; color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 실시간 시계
kst_now = get_kst_now()
st.markdown(f"""
    <div class="clock-box">
        <div style="font-size: 2.5rem; font-weight: 900;">{kst_now.strftime('%H:%M:%S')}</div>
        <div style="font-size: 1rem; opacity: 0.8;">{kst_now.strftime('%Y-%m-%d %a')}</div>
    </div>
    """, unsafe_allow_html=True)

st.title("🚗48러 9208 주유 기록")

# 4. 입력 섹션
with st.container():
    station_options = ["oil bank", "SK", "GS 칼텍스", "E1", "기타"]
    selected_station = st.selectbox("📍 주유소 선택", station_options)
    final_station_name = selected_station
    if selected_station == "기타":
        final_station_name = st.text_input("주유소 이름 입력")

    # 주행거리 입력 및 자동 연비 계산 준비
    last_km = st.session_state.fuel_df['주행거리(km)'].max() if not st.session_state.fuel_df.empty else 0
    mileage = st.number_input("🛣️ 현재 주행거리 (km)", min_value=0, value=int(last_km), step=1)
    
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("단가 (원)", min_value=1, value=1650, step=10)
    with c2:
        money = st.number_input("금액 (원)", min_value=0, value=50000, step=1000)
    
    # 계산 로직
    calc_l = round(money / price, 2) if price > 0 else 0.0
    diff_km = mileage - last_km if last_km > 0 else 0
    # 연비 계산: 주행차이 / 주유량 (직전 주유량 기준이 정확하나, 편의상 현재 주유량으로 계산 예시)
    fuel_efficiency = round(diff_km / calc_l, 2) if calc_l > 0 and diff_km > 0 else 0.0

    st.markdown(f"""
        <div class="res-card">
            <div style="color:#666; font-size:0.9rem;">이번 주유 연비 분석</div>
            <div class="efficiency-val">{fuel_efficiency} <span style="font-size:1.2rem;">km/L</span></div>
            <div style="font-size:0.9rem; color:#888;">주행 차이: {diff_km}km | 주유량: {calc_l}L</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🚀 연비 데이터 저장하기", type="primary"):
        if mileage <= last_km and last_km > 0:
            st.error("현재 주행거리는 이전 기록보다 커야 합니다!")
        elif selected_station == "기타" and not final_station_name:
            st.warning("주유소 이름을 입력해주세요!")
        else:
            save_time = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([{
                '일시': save_time,
                '주유소': final_station_name,
                '주행거리(km)': mileage,
                '주행차이(km)': diff_km,
                '단가(원)': price,
                '금액(원)': money,
                '주유량(L)': calc_l,
                '연비(km/L)': fuel_efficiency
            }])
            st.session_state.fuel_df = pd.concat([st.session_state.fuel_df, new_row], ignore_index=True)
            st.success("연비 기록이 완료되었습니다!")
            st.rerun()

# 5. 분석 및 관리
if not st.session_state.fuel_df.empty:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📊 연비/지출 추이", "📜 기록 관리"])

    with tab1:
        df_plot = st.session_state.fuel_df.tail(20).copy()
        df_plot['라벨'] = df_plot['주유소'] + "(" + pd.to_datetime(df_plot['일시']).dt.strftime('%m/%d') + ")"
        
        st.subheader("📈 구간 연비 추이 (km/L)")
        # 연비 데이터가 있는 것만 필터링해서 그래프 표시
        eff_df = df_plot[df_plot['연비(km/L)'] > 0]
        if not eff_df.empty:
            st.line_chart(eff_df.set_index('라벨')['연비(km/L)'], color="#28a745")
        
        st.subheader("💰 지출 및 주행거리")
        st.bar_chart(df_plot.set_index('라벨')['금액(원)'])

    with tab2:
        rev_df = st.session_state.fuel_df.iloc[::-1]
        for idx, row in rev_df.iterrows():
            eff_text = f" | 연비: {row['연비(km/L)']} km/L" if row['연비(km/L)'] > 0 else ""
            with st.expander(f"📍 {row['주유소']} ({row['주행거리(km)']}km){eff_text}"):
                st.write(f"• 일시: {row['일시']}")
                st.write(f"• 상세: {row['금액(원)']}원 ({row['주유량(L)']}L) / 주행: {row['주행차이(km)']}km")
                if st.button(f"삭제", key=f"del_{idx}"):
                    st.session_state.fuel_df = st.session_state.fuel_df.drop(idx).reset_index(drop=True)
                    st.rerun()
else:
    st.info("기록된 데이터가 없습니다.")
