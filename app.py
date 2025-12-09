import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="수의 선율", page_icon="🎼", layout="wide")

# --- 2. 스타일링 (가독성 완벽 개선) ---
st.markdown("""
<style>
    /* 1. 전체 배경: 따뜻한 아이보리색 */
    .stApp {
        background-color: #FDFCF0;
    }
    
    /* 2. 모든 기본 텍스트를 강제로 '진한 회색'으로 고정 (다크모드 방지) */
    html, body, p, div, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #2c3e50 !important; 
        font-family: 'KoPub Batang', serif; /* 명조체 느낌 */
    }
    
    /* 3. 제목 스타일 */
    h1 {
        font-weight: bold;
        color: #1a1a1a !important;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
    }

    /* 4. 수학 설명 박스 디자인 */
    .math-box {
        background-color: #e8f4f8; /* 연한 파랑 */
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* 박스 안의 글씨도 강제 검정 */
    .math-box p, .math-box li, .math-box b {
        color: #333 !important;
    }

    /* 5. 입력창(Input) 글씨 색상 문제 해결 */
    .stTextInput input {
        color: #333 !important;      /* 입력 글씨 검정 */
        background-color: #ffffff;   /* 배경 흰색 */
        border: 1px solid #ddd;
    }
    /* 셀렉트박스(Selectbox) 텍스트 해결 */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff;
        color: #333 !important;
    }
    
    /* 6. 버튼 스타일 (버튼은 어둡게, 글씨는 하얗게) */
    .stButton>button {
        background-color: #2c3e50 !important;
        color: #ffffff !important; /* 버튼 글씨는 흰색 */
        border: none;
        border-radius: 5px;
        padding: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1a252f !important;
    }
    
    /* 7. 탭(Tab) 글씨 색상 */
    button[data-baseweb="tab"] {
        color: #555 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #000 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 ---
def generate_tone(freq, duration, wave_type):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    if wave_type == "부드러운 소리 (Sine)":
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == "단단한 소리 (Square)":
        wave = np.sign(np.sin(2 * np.pi * freq * t)) * 0.5
    else: # Triangle
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
            if f == 0:
                tone = np.zeros(int(44100 * duration))
            else:
                tone = generate_tone(f, duration, wave_type)
            melody.append(tone)
            
    if not melody: return None
    return np.concatenate(melody)

# --- 4. 메인 UI ---

st.title("🎼 수(數)의 선율")
st.markdown("### 수학적 규칙이 아름다운 음악이 되는 곳")
st.markdown("---")

col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("1. 숫자 선택")
    
    tab_math, tab_custom = st.tabs(["수학 상수", "직접 입력"])
    
    with tab_math:
        math_choice = st.radio("들어보고 싶은 상수는?", 
                              ["원주율 (π)", "자연상수 (e)", "황금비 (φ)"])
        
        if "원주율" in math_choice:
            nums = "314159265358979323846264338327950288419716939937510"
            desc = "**원주율(Pi):** 원의 둘레와 지름의 비율입니다. 소수점 아래로 영원히 불규칙하게 이어집니다."
        elif "자연상수" in math_choice:
            nums = "271828182845904523536028747135266249775724709369995"
            desc = "**자연상수(e):** 성장의 한계를 설명하는 수입니다. 미적분학에서 가장 중요하게 다뤄집니다."
        else:
            nums = "161803398874989484820458683436563811772030917980576"
            desc = "**황금비(Phi):** 자연계와 예술에서 발견되는 가장 완벽한 비율(1:1.618)입니다."
            
        st.info(desc)

    with tab_custom:
        user_input = st.text_input("숫자를 입력해보세요 (예: 생년월일 8자리)", placeholder="20240101")
        if user_input:
            nums = ''.join(filter(str.isdigit, user_input))
        elif 'nums' not in locals():
             nums = "12345678"

    st.write("") # 여백
    st.subheader("2. 악기 설정")
    sound_type = st.selectbox("음색 선택", ["부드러운 소리 (Sine)", "단단한 소리 (Square)", "맑은 소리 (Triangle)"])
    bpm = st.slider("빠르기 (BPM)", 60, 180, 120)

    st.write("") 
    # 수학 설명 박스
    st.markdown("""
    <div class="math-box">
        <b>💡 수학 선생님을 위한 Tip</b>
        <ul>
            <li><b>사인파(Sine):</b> $y = \sin(x)$ 그래프처럼 가장 기본적이고 순수한 소리입니다.</li>
            <li><b>주파수(Hz):</b> 1초에 진동하는 횟수입니다. '라(A)'음은 440Hz로 약속되어 있습니다.</li>
            <li><b>감쇠(Decay):</b> 지수함수 $y = e^{-x}$를 곱해서 소리가 자연스럽게 줄어들게 만들었습니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("3. 연주 및 분석")
    
    if nums:
        # 1. 시각화 (차트 색상도 진하게 변경)
        digits = [int(d) for d in nums[:20] if d != '0']
        
        # 차트 제목
        st.caption(f"🎵 선택된 숫자열: {nums[:20]}...")
        
        # 바 차트 (색상 설정은 Streamlit 기본 테마를 따르지만, 배경이 밝아서 잘 보임)
        st.bar_chart(digits, height=180)
        
        st.write("") # 여백
        
        # 2. 플레이어
        if st.button("▶️ 연주 시작 (Play)", use_container_width=True):
            with st.spinner("숫자를 파동으로 변환하고 있습니다..."):
                audio_data = numbers_to_melody(nums, bpm, sound_type)
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                
                st.audio(virtual_file, format='audio/wav')
                st.success("수학이 음악으로 변환되었습니다!")
    else:
        st.warning("숫자를 입력해주세요.")
