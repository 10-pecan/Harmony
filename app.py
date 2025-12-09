import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd # 귀여운 그래프를 위해 pandas 추가

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Music", page_icon="🎵", layout="wide")

# --- 2. 스타일링 (초강력 글자색 고정 & 귀여운 디자인) ---
st.markdown("""
<style>
    /* [핵심] 모든 글자색을 강제로 진한 검정(#111)으로 고정! */
    html, body, h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown, .stSelectbox, .stSlider {
        color: #111111 !important;
    }
    
    /* 배경은 무조건 깨끗한 흰색 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 폰트: 둥글둥글하고 귀여운 느낌의 고딕체 */
    * { font-family: 'Jua', 'Pretendard', sans-serif !important; }
    
    /* 제목 스타일 */
    h1 { font-size: 3rem; letter-spacing: -2px; color: #FF6B6B !important; } /* 제목은 귀여운 코랄색 */
    h5 { color: #555 !important; }
    
    /* 카드 박스 디자인 (둥글고 그림자 있게) */
    .modern-card {
        background-color: #FFF0F5; /* 연한 분홍색 배경 */
        padding: 25px;
        border-radius: 20px;
        border: 3px solid #FFD1DC; /* 테두리도 귀엽게 */
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(255, 182, 193, 0.3);
    }
    
    /* 팁 박스 (말풍선) */
    .tip-box {
        background-color: #E3F2FD;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #BBDEFB;
        color: #0D47A1 !important;
        font-size: 1rem;
    }
    .tip-box b { color: #1565C0 !important; }

    /* 입력창 & 버튼 */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #fff !important;
        color: #333 !important;
        border-radius: 12px;
        border: 2px solid #eee;
    }
    /* 재생 버튼 */
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53) !important; /* 그라데이션 버튼 */
        color: #fff !important;
        border-radius: 50px;
        height: 55px;
        font-size: 1.2rem;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 10px rgba(255, 107, 107, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (그대로 유지) ---
def generate_tone(freq, duration, wave_type):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    if wave_type == "💧 맑은 물방울 (Sine)":
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == "🎻 따뜻한 첼로 (Low Bass)":
        bass_freq = freq * 0.5
        wave = 0.7 * np.sin(2 * np.pi * bass_freq * t) + 0.3 * np.sin(2 * np.pi * bass_freq * 2 * t)
    else:
        wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    
    decay = np.exp(-3 * t)
    return wave * decay

def numbers_to_melody(number_str, bpm, wave_type):
    freqs = {
        '1': 261.63, '2': 293.66, '3': 329.63, '4': 349.23,
        '5': 392.00, '6': 440.00, '7': 493.88, '8': 523.25, 
        '9': 587.33, '0': 0
    }
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

st.title("Math Music Lab 🎵")
st.markdown("##### 숫자가 들려주는 나만의 멜로디")
st.write("")

col1, col2 = st.columns([1, 1.3])

with col1:
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown("### 1️⃣ 숫자 고르기")
    
    tab_math, tab_custom = st.tabs(["유명한 숫자", "내 숫자 입력"])
    
    with tab_math:
        math_choice = st.radio("어떤 수의 소리가 궁금한가요?", 
                              ["원주율 (3.14...)", "자연상수 (2.71...)", "황금비 (1.61...)"])
        if "원주율" in math_choice: nums = "314159265358979323846264338327950288419716939937510"
        elif "자연상수" in math_choice: nums = "271828182845904523536028747135266249775724709369995"
        else: nums = "161803398874989484820458683436563811772030917980576"

    with tab_custom:
        user_input = st.text_input("생일이나 기념일을 입력해보세요", placeholder="20241225")
        if user_input: nums = ''.join(filter(str.isdigit, user_input))
        elif 'nums' not in locals(): nums = "12345678"
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown("### 2️⃣ 악기 설정")
    sound_type = st.selectbox("어떤 악기로 연주할까요?", 
                             ["🎻 따뜻한 첼로 (Low Bass)", "💧 맑은 물방울 (Sine)", "✨ 반짝이는 소리 (Triangle)"])
    bpm = st.slider("빠르기 (Tempo)", 60, 180, 110)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="tip-box">
        <b>💡 수학 선생님의 비밀 노트</b><br><br>
        <b>1. 소리는 떨림이야!</b><br>
        숫자가 클수록 더 빨리 떨려서 높은 소리가 나요.<br>
        <b>2. 첼로 소리의 비밀</b><br>
        파도 모양 그래프(사인파) 두 개를 섞으면 신기하게 첼로 소리가 나요!<br>
        <b>3. 소리가 작아지는 이유</b><br>
        미끄럼틀 모양(지수함수) 그래프를 곱해줘서 소리가 부드럽게 사라지는 거예요.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="modern-card" style="background-color:#F0F8FF; border-color:#B0E0E6;">', unsafe_allow_html=True)
    st.markdown("### 3️⃣ 연주 & 시각화")
    
    if nums:
        # [NEW] 귀여운 그래프를 위한 데이터 가공
        digits = [int(d) for d in nums[:30] if d != '0']
        # 데이터프레임 생성 (인덱스=순서, 값=높이)
        chart_data = pd.DataFrame({'Note': digits}).reset_index()
        
        st.caption(f"🎼 통통 튀는 음표들: {nums[:20]}...")
        
        # [NEW] 귀여운 산점도(Scatter Chart) 그리기
        # x축: 순서, y축: 음 높이, size: 음 높이에 비례해서 커짐, color: 알록달록
        st.vega_lite_chart(chart_data, {
            'mark': {'type': 'circle', 'tooltip': True},
            'encoding': {
                'x': {'field': 'index', 'type': 'ordinal', 'axis': None}, # X축 숨김
                'y': {'field': 'Note', 'type': 'quantitative', 'axis': None, 'scale': {'domain': [0, 10]}}, # Y축 숨김
                'size': {'field': 'Note', 'type': 'quantitative', 'scale': {'range': [100, 1000]}, 'legend': None}, # 크기 조절
                'color': {'field': 'Note', 'type': 'nominal', 'scale': {'scheme': 'rainbow'}, 'legend': None} # 무지개색
            },
            'height': 250
        }, use_container_width=True)
        
        st.write("")
        
        if st.button("▶️ 재생하기 (Play)", use_container_width=True):
            with st.spinner("수학을 음악으로 바꾸는 중... 🎧"):
                audio_data = numbers_to_melody(nums, bpm, sound_type)
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                st.audio(virtual_file, format='audio/wav')
                st.balloons()
    else:
        st.warning("숫자를 입력해주세요.")
    st.markdown('</div>', unsafe_allow_html=True)
