import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="수의 선율", page_icon="🎼", layout="wide")

# --- 2. 스타일링 (깔끔하고 교육적인 느낌) ---
st.markdown("""
<style>
    .stApp { background-color: #FDFCF0; color: #333; } /* 따뜻한 종이 색감 */
    h1 { font-family: 'KoPub Batang', serif; color: #1a1a1a; }
    .math-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
        font-size: 0.9em;
    }
    .stButton>button {
        background-color: #333;
        color: white;
        border-radius: 5px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (단순화된 버전) ---
def generate_tone(freq, duration, wave_type):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 수학적 파형 생성
    if wave_type == "부드러운 소리 (Sine)":
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == "단단한 소리 (Square)":
        wave = np.sign(np.sin(2 * np.pi * freq * t)) * 0.5
    else: # 맑은 소리 (Triangle)
        wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        
    # 소리 끝을 부드럽게 (Decay) - 지수 함수 활용
    decay = np.exp(-3 * t)
    return wave * decay

def numbers_to_melody(number_str, bpm, wave_type):
    # C Major Scale (다장조) - 피타고라스 음계 기반
    # 1=도, 2=레, 3=미, 4=파, 5=솔, 6=라, 7=시, 8=높은도, 9=높은레, 0=쉼표
    freqs = {
        '1': 261.63, '2': 293.66, '3': 329.63, '4': 349.23,
        '5': 392.00, '6': 440.00, '7': 493.88, '8': 523.25, 
        '9': 587.33, '0': 0
    }
    
    melody = []
    duration = 60.0 / bpm # 1박자의 시간(초)
    
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

col1, col2 = st.columns([1, 1.5])

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
        user_input = st.text_input("숫자를 입력해보세요 (예: 생년월일)", placeholder="12345678")
        if user_input:
            nums = ''.join(filter(str.isdigit, user_input))
        elif 'nums' not in locals(): # 사용자 입력이 없고 상수 탭도 아닐 때
             nums = "12345678"

    st.subheader("2. 악기 설정")
    sound_type = st.selectbox("음색 선택", ["부드러운 소리 (Sine)", "단단한 소리 (Square)", "맑은 소리 (Triangle)"])
    bpm = st.slider("빠르기 (BPM)", 60, 180, 120)

    # 수학 설명 박스
    st.markdown("""
    <div class="math-box">
        <b>💡 수학 선생님을 위한 Tip</b><br>
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
        # 시각화 (악보처럼)
        digits = [int(d) for d in nums[:20] if d != '0']
        st.bar_chart(digits, height=150, color="#333333")
        st.caption(f"선택된 숫자열: {nums[:20]}...")
        
        if st.button("🎵 연주 시작 (Play)", use_container_width=True):
            with st.spinner("숫자를 파동으로 변환하고 있습니다..."):
                audio_data = numbers_to_melody(nums, bpm, sound_type)
                
                # 메모리에 오디오 파일 생성
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                
                st.audio(virtual_file, format='audio/wav')
                st.success("수학이 음악으로 변환되었습니다!")
    else:
        st.warning("숫자를 입력해주세요.")
