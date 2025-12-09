import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io

# --- 페이지 설정 ---
st.set_page_config(page_title="Harmonia: Sound of Math", page_icon="🎹", layout="centered")

# --- 스타일 (감성적이고 차분한 디자인) ---
st.markdown("""
<style>
    .stApp { background-color: #1e1e1e; color: #f0f0f0; }
    h1 { font-family: 'Georgia', serif; color: #E0E0E0; }
    .stButton>button { background-color: #8B5FBF; color: white; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 음악 생성 로직 (수학 → 주파수 변환) ---
def generate_tone(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # 부드러운 사인파 (Sine Wave) 생성
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    return tone

def numbers_to_melody(number_str, speed, octave):
    # C Major Scale (도레미파솔라시도...) 주파수
    # 숫자에 따라 음을 매핑 (0: 쉼표, 1: 도, 2: 레 ...)
    base_freqs = {
        '1': 261.63, # C4 (도)
        '2': 293.66, # D4 (레)
        '3': 329.63, # E4 (미)
        '4': 349.23, # F4 (파)
        '5': 392.00, # G4 (솔)
        '6': 440.00, # A4 (라)
        '7': 493.88, # B4 (시)
        '8': 523.25, # C5 (높은 도)
        '9': 587.33, # D5 (높은 레)
        '0': 0       # 쉼표
    }
    
    melody = []
    duration = 1.0 / speed # 속도 조절
    
    for char in number_str:
        if char in base_freqs:
            freq = base_freqs[char]
            # 옥타브 조절 (x2 하거나 /2 하면 옥타브가 바뀜)
            if freq > 0:
                freq = freq * (2 ** (octave - 4)) 
            
            tone = generate_tone(freq, duration)
            
            # 음 끝을 부드럽게 처리 (Fade out)
            decay = np.linspace(1, 0, len(tone))
            tone = tone * decay
            
            melody.append(tone)
            
    return np.concatenate(melody)

# --- 메인 UI ---
st.title("🎹 Harmonia")
st.markdown("### 숫자의 규칙 속에 숨겨진 멜로디를 찾습니다.")
st.write("수학 상수나 의미 있는 숫자를 입력해보세요.")

st.divider()

# 입력 받기
col1, col2 = st.columns([2, 1])

with col1:
    option = st.selectbox("어떤 숫자를 연주할까요?", 
                         ["원주율 (Pi, π)", "오일러의 수 (e)", "황금비 (Phi, φ)", "직접 입력"])
    
    if option == "원주율 (Pi, π)":
        num_input = "314159265358979323846264338327950288419716939937510"
    elif option == "오일러의 수 (e)":
        num_input = "271828182845904523536028747135266249775724709369995"
    elif option == "황금비 (Phi, φ)":
        num_input = "161803398874989484820458683436563811772030917980576"
    else:
        num_input = st.text_input("숫자를 입력하세요 (예: 친구 생일 19951225)", "12345678")

    # 숫자 정제 (숫자만 남기기)
    clean_nums = ''.join(filter(str.isdigit, num_input))

with col2:
    bpm = st.slider("연주 속도 (Speed)", 1, 10, 4)
    octave = st.select_slider("음역대 (Octave)", options=[3, 4, 5], value=4)

# --- 시각화 및 재생 ---
if clean_nums:
    st.markdown(f"**Play Sequence:** `{clean_nums[:20]}...`")
    
    # 1. 시각화 (숫자를 막대 그래프로 표현해 악보처럼 보이게 함)
    digits = [int(d) for d in clean_nums if d != '0']
    st.bar_chart(digits, height=150)
    
    # 2. 오디오 생성 버튼
    if st.button("🎵 연주 시작 (Generate Music)", use_container_width=True):
        with st.spinner("숫자를 주파수로 변환하는 중..."):
            audio_data = numbers_to_melody(clean_nums, bpm, octave)
            
            # 오디오 데이터를 메모리에 저장
            virtual_file = io.BytesIO()
            # 44100Hz 샘플링 레이트로 저장
            write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
            
            st.success("연주 준비 완료!")
            st.audio(virtual_file, format='audio/wav')
            
            st.caption("Tip: 0은 쉼표, 1~9는 도~높은 레에 해당합니다.")

else:
    st.warning("연주할 숫자가 없습니다.")

# --- 감성 멘트 ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-style: italic; color: gray;">
    "Mathematics is music for the mind; Music is mathematics for the soul." <br>
    - Pythagoras (reinterpreted)
</div>
""", unsafe_allow_html=True)
