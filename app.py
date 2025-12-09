import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt # 더 예쁜 그래프를 위해 Altair 사용

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Music Lab", page_icon="🎹", layout="wide")

# --- 2. 세련되고 트렌디한 스타일링 (CSS) ---
st.markdown("""
<style>
    /* [폰트 및 기본 컬러 설정] */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Pretendard:wght@300;400;600&display=swap');
    
    :root {
        --bg-color: #FAFAFA; /* 아주 연한 미색 배경 */
        --text-color: #2C3E50; /* 진한 차콜색 텍스트 */
        --accent-color: #FF8E53; /* 포인트 컬러 (코랄 오렌지) */
        --card-bg: #FFFFFF;
        --shadow: 0 10px 30px rgba(0,0,0,0.05); /* 부드러운 그림자 */
    }

    /* 전체 적용 및 다크모드 방어 */
    html, body, .stApp {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: var(--text-color) !important;
    }

    /* [타이포그래피 디자인] */
    .main-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B6B, #FF8E53, #FFC371); /* 세련된 그라데이션 */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #666 !important;
        margin-bottom: 30px;
        font-weight: 400;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    .section-header span { /* 아이콘 배경 */
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px; height: 32px;
        background-color: #FFF0F5; color: #FF6B6B;
        border-radius: 10px; margin-right: 10px;
    }

    /* [카드 UI 디자인] */
    .stylish-card {
        background-color: var(--card-bg);
        padding: 30px;
        border-radius: 24px;
        box-shadow: var(--shadow);
        border: 1px solid rgba(0,0,0,0.03);
        transition: transform 0.3s ease;
    }
    .stylish-card:hover {
        transform: translateY(-5px); /* 마우스 올리면 살짝 떠오름 */
    }

    /* [입력창 및 버튼 디자인] */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border: 1px solid #E0E0E0 !important;
        padding: 10px 15px !important;
        background-color: #F9F9F9 !important;
        transition: all 0.3s;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: var(--accent-color) !important;
        background-color: #FFF !important;
        box-shadow: 0 0 0 3px rgba(255, 142, 83, 0.1) !important;
    }
    
    /* 재생 버튼 */
    .play-button > button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53) !important;
        color: white !important;
        border: none;
        border-radius: 50px;
        height: 60px;
        font-size: 1.2rem;
        font-weight: 700;
        box-shadow: 0 10px 20px rgba(255, 107, 107, 0.3);
        transition: all 0.3s !important;
    }
    .play-button > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 15px 30px rgba(255, 107, 107, 0.4);
    }

    /* [말풍선 팁 디자인] */
    .bubble-tip {
        position: relative;
        background: #EBF5FF; /* 아주 연한 파랑 */
        color: #0056b3 !important;
        padding: 20px 25px;
        border-radius: 20px;
        border-bottom-left-radius: 5px; /* 말풍선 꼬리 느낌 */
        margin-top: 20px;
        line-height: 1.6;
        box-shadow: 0 5px 15px rgba(13, 71, 161, 0.08);
    }
    .bubble-tip b { color: #004085 !important; }
    
    /* 탭 디자인 커스텀 */
    div[data-baseweb="tab-list"] {
        gap: 10px; margin-bottom: 20px;
    }
    button[data-baseweb="tab"] {
        background-color: #F0F0F0 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 8px 16px !important;
        color: #666 !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #2C3E50 !important; /* 선택된 탭 */
        color: #FFF !important;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (기존과 동일) ---
def generate_tone(freq, duration, wave_type):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    if "물방울" in wave_type: wave = np.sin(2 * np.pi * freq * t)
    elif "첼로" in wave_type:
        bass_freq = freq * 0.5
        wave = 0.7 * np.sin(2 * np.pi * bass_freq * t) + 0.3 * np.sin(2 * np.pi * bass_freq * 2 * t)
    else: wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    
    decay = np.exp(-3 * t)
    return wave * decay

def numbers_to_melody(number_str, bpm, wave_type):
    freqs = {'1':261.63,'2':293.66,'3':329.63,'4':349.23,'5':392.00,'6':440.00,'7':493.88,'8':523.25,'9':587.33,'0':0}
    melody = []
    duration = 60.0 / bpm
    for char in number_str:
        if char in freqs:
            f = freqs[char]
            tone = np.zeros(int(44100 * duration)) if f == 0 else generate_tone(f, duration, wave_type)
            melody.append(tone)
    if not melody: return None
    return np.concatenate(melody)

# --- 4. 메인 UI 구성 ---

# 타이틀 영역
st.markdown('<div class="main-title">Math Music Lab.</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">숫자 속에 숨겨진 나만의 멜로디를 발견하세요 🎹</div>', unsafe_allow_html=True)
st.write("")

# 메인 레이아웃 (좌우 분할)
col_control, col_result = st.columns([1, 1.4], gap="large")

# [왼쪽 컨트롤 패널]
with col_control:
    with st.container():
        st.markdown('<div class="stylish-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><span>1️⃣</span> 숫자 고르기</div>', unsafe_allow_html=True)
        
        tab_math, tab_custom = st.tabs(["✨ 유명한 상수", "🖊️ 직접 입력"])
        with tab_math:
            math_choice = st.radio("들어보고 싶은 수는?", ["원주율 (π)", "자연상수 (e)", "황금비 (φ)"], label_visibility="collapsed")
            if "원주율" in math_choice: nums = "314159265358979323846264338327950288419716939937510"
            elif "자연상수" in math_choice: nums = "271828182845904523536028747135266249775724709369995"
            else: nums = "161803398874989484820458683436563811772030917980576"
        with tab_custom:
            user_input = st.text_input("생일이나 기념일을 입력하세요", placeholder="YYYYMMDD")
            if user_input: nums = ''.join(filter(str.isdigit, user_input))
            elif 'nums' not in locals(): nums = "12345678" # 기본값
        
        st.write("") # 여백
        st.markdown('<div class="section-header"><span>2️⃣</span> 사운드 디자인</div>', unsafe_allow_html=True)
        sound_type = st.selectbox("악기 선택", ["🎻 따뜻한 첼로 (Low Bass)", "💧 맑은 물방울 (Sine)", "✨ 반짝이는 소리 (Triangle)"])
        bpm = st.slider("빠르기 (Tempo)", 60, 180, 110)
        st.markdown('</div>', unsafe_allow_html=True) # 카드 닫기

    # 말풍선 팁
    st.markdown("""
    <div class="bubble-tip">
        <b>💡 수학 선생님의 비밀 노트</b><br>
        "소리는 공기의 떨림이야. 숫자가 클수록 빨리 떨려서 높은 소리가 나지! 
        방금 고른 <b>첼로 소리</b>는 파도 모양 그래프 두 개를 수학적으로 섞어서 만든 거란다."
    </div>
    """, unsafe_allow_html=True)

# [오른쪽 결과 패널]
with col_result:
    st.markdown('<div class="stylish-card" style="background-color:#F8FFFF; border-color:#E0F7FA;">', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="color:#00838F;"><span>3️⃣</span> 멜로디 시각화 & 재생</div>', unsafe_allow_html=True)
    
    if nums:
        # [NEW] 젤리 버블 차트 (Altair 사용)
        digits = [int(d) for d in nums[:25] if d != '0'] # 0 제외, 25개만
        chart_data = pd.DataFrame({'Order': range(len(digits)), 'Note': digits, 'Size': [d*10 for d in digits]})

        # Altair 차트 정의 (탱글한 젤리 느낌)
        chart = alt.Chart(chart_data).mark_circle().encode(
            x=alt.X('Order', axis=None), # 축 숨김
            y=alt.Y('Note', axis=None, scale=alt.Scale(domain=[0, 10], padding=1)), # 축 숨김, 여백 줌
            size=alt.Size('Size', legend=None, scale=alt.Scale(range=[150, 1000])), # 크기 범위 설정
            color=alt.Color('Note', legend=None, scale=alt.Scale(scheme='rainbow')), # 무지개색
            tooltip=['Note', 'Order'] # 마우스 오버 시 정보 표시
        ).configure_mark(
            opacity=0.7, # 약간 투명하게
            stroke='white', strokeWidth=2, # 흰색 테두리로 깔끔하게
        ).configure_view(strokeWidth=0).properties(height=300) # 테두리 없앰

        st.caption(f"🎼 연주 시퀀스: {nums[:15]}...")
        st.altair_chart(chart, use_container_width=True)
        
        st.write("") # 여백
        
        # 재생 버튼 (스타일 적용을 위해 컨테이너 사용)
        with st.container():
            st.markdown('<div class="play-button">', unsafe_allow_html=True)
            if st.button("🎵 멜로디 재생하기 (Play)", use_container_width=True):
                with st.spinner("수학 공식을 음악으로 바꾸는 중... 🎧"):
                    audio_data = numbers_to_melody(nums, bpm, sound_type)
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
                    st.balloons()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("왼쪽에서 숫자를 입력해주세요.")
    st.markdown('</div>', unsafe_allow_html=True) # 카드 닫기
