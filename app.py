import streamlit as st
import pandas as pd
import os

# 설정: 저장할 파일 이름
SAVE_FILE = "fuel_logs.csv"

# 1. CSV 파일 로드 함수 (파일이 없으면 빈 데이터프레임 생성)
def load_data():
    if os.path.exists(SAVE_FILE):
        return pd.read_csv(SAVE_FILE)
    else:
        return pd.DataFrame(columns=["날짜", "주행 거리(km)", "연료량(L)", "연비(km/L)"])

# 2. 데이터 저장 함수
def save_data(df):
    df.to_csv(SAVE_FILE, index=False, encoding='utf-8-sig')

st.title("⛽ 자동차 연비 영구 기록장")

# 데이터 불러오기
df_logs = load_data()

# 3. 입력 섹션
with st.form("fuel_input_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        distance = st.number_input("주행 거리 (km)", min_value=0.0, step=0.1)
    with col2:
        fuel = st.number_input("사용 연료량 (L)", min_value=0.1, step=0.1)
    
    date = st.date_input("주유 날짜")
    submit_btn = st.form_submit_button("기록 저장하기")

# 4. 저장 로직
if submit_btn:
    if fuel > 0:
        efficiency = round(distance / fuel, 2)
        
        # 새로운 행 생성
        new_entry = pd.DataFrame([[date, distance, fuel, efficiency]], 
                                 columns=["날짜", "주행 거리(km)", "연료량(L)", "연비(km/L)"])
        
        # 기존 데이터에 추가 후 저장
        df_logs = pd.concat([df_logs, new_entry], ignore_index=True)
        save_data(df_logs)
        
        st.success(f"✅ 저장 완료! 계산된 연비: {efficiency} km/L")
        st.balloons() # 축하 효과
    else:
        st.error("연료량은 0보다 커야 합니다.")

---

### 5. 데이터 확인 및 통계
st.subheader("📋 전체 주유 기록")

if not df_logs.empty:
    # 표 출력 (최신순으로 보기 위해 reversed 활용 가능)
    st.dataframe(df_logs.sort_values(by="날짜", ascending=False), use_container_width=True)
    
    # 간단한 요약 통계
    avg_eff = df_logs["연비(km/L)"].mean()
    total_dist = df_logs["주행 거리(km)"].sum()
    
    c1, c2 = st.columns(2)
    c1.metric("누적 주행 거리", f"{total_dist:,.1f} km")
    c2.metric("평균 연비", f"{avg_eff:.2f} km/L")

    # 데이터 삭제 기능 (선택 사항)
    if st.button("전체 기록 삭제"):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
            st.warning("모든 기록이 삭제되었습니다. 페이지를 새로고침하세요.")
else:
    st.info("기록된 데이터가 없습니다. 첫 기록을 입력해보세요!")
