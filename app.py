import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io

# --- 1. 페이지 설정 (전문 도구 느낌의 와이드 레이아웃) ---
st.set_page_config(page_title="Math Music Lab", page_icon="🎹", layout="wide")

# --- 2. 스타일링 (미니멀리즘 & 다크 모드) ---
st.markdown("""
<style>
    /* 전체 배경: 깊은 차콜색 */
    .stApp { background-color: #121212; color: #e0e0e0; }
    
    /* 헤더 스타일 */
    h1 { font-family: 'Helvetica Neue', sans-serif; font-weight: 100; letter-spacing: 2px; }
    h3 { color: #888; font-weight: 300; }
    
    /* 컨트롤 패널 박스 디자인 */
    .control-panel {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 20px;
    }
    
    /* 오디오 플레이어 커스텀 */
    audio { width: 100%; margin-top: 20px; }
    
    /* 버튼 스타일 (전문 장비 버튼 느낌) */
    .stButton>button {
        background-color: #2c2c2c;
        color: #00d4ff;
        border: 1px solid #00d4ff;
        border-radius: 4px;
        font-weight: bold;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #00d4ff;
        color: #121212;
        box-shadow: 0 0 10px #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (수학적 파형 합성) ---
class ToneGenerator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def get_wave(self, freq, duration, wave_type="Sine"):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # 파형 함수 (수학적 구현)
        if wave_type == "Sine (Pure)":
            wave = np.sin(2 * np.pi * freq * t)
        elif wave_type == "Square (Retro)":
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave_type == "Sawtooth (Sharp)":
            wave = 2 * (freq * t - np.floor(freq * t + 0.5))
        else:
            wave = np.sin(2 * np.pi * freq * t) # 기본값
            
        return wave

    def apply_envelope(self, wave, duration):
        # ADSR (Attack, Decay, Sustain, Release) 엔벨로프 적용
        total_samples = len(wave)
        attack_len = int(total_samples * 0.1) # 10%
        decay_len = int(total_samples * 0.1)  # 10%
        release_len = int(total_samples * 0.2) # 20%
        sustain_len = total_samples - attack_len - decay_len - release_len
        
        # 선형 보간 (Linear Interpolation)
        attack = np.linspace(0, 1, attack_len)
        decay = np.linspace(1, 0.7, decay_len)
        sustain = np.full(sustain_len, 0.7)
        release = np.linspace(0.7, 0, release_len)
        
        envelope = np.concatenate([attack, decay, sustain, release])
        
        # 길이 맞추기 (오차 보정)
        if len(envelope) < total_samples:
            envelope = np.pad(envelope, (0, total_samples - len(envelope)), 'constant')
        elif len(envelope) > total_samples:
            envelope = envelope[:total_samples]
            
        return wave * envelope

# --- 4. 음악 이론 (음계 매핑) ---
SCALES = {
    "C Major (밝음/기본)": [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88], # 도레미파솔라시
    "A Minor (슬픔/감성)": [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00], # 라시도레미파솔
    "Pentatonic (동양적)": [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33], # 도레미솔라 (5음계)
    "Whole Tone (몽환적)": [261.63, 293.66, 329.63, 369.99, 415.30, 466.16, 523.25]  # 온음계
}

def generate_melody(numbers, bpm, scale_name, wave_type, octave_shift):
    gen = ToneGenerator()
    melody = []
    duration = 60.0 / bpm # 1박자 길이
    
    scale_freqs = SCALES[scale_name]
    scale_len = len(scale_freqs)
    
    for char in numbers:
        if char.isdigit():
            digit = int(char)
            
            if digit == 0:
                # 0은 쉼표
                tone = np.zeros(int(44100 * duration))
            else:
                # 숫자를 스케일의 인덱스로 변환 (모듈러 연산)
                # 1 -> 첫번째 음, 8 -> 여덟번째 음(한옥타브 위)
                note_idx = (digit - 1) % scale_len
                base_freq = scale_freqs[note_idx]
                
                # 옥타브 처리 (숫자가 크면 높은 음)
                octave_multiplier = 2 ** (octave_shift + (digit - 1) // scale_len)
                freq = base_freq * octave_multiplier
                
                # 파형 생성
                raw_wave = gen.get_wave(freq, duration, wave_type)
                tone = gen.apply_envelope(raw_wave, duration)
                
            melody.append(tone)
            
    if not melody: return None
    return np.concatenate(melody)

# --- 5. UI 레이아웃 ---
st.title("Math Music Lab.")
st.markdown("### The Sonification of Mathematics")
st.markdown("---")

# 좌측: 입력 및 설정 / 우측: 시각화 및 결과
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("#### 1. Input Source")
    with st.container(border=True):
        source_type = st.radio("데이터 소스 선택", ["Mathematical Constant", "Custom Number"], label_visibility="collapsed")
        
        if source_type == "Mathematical Constant":
            const_choice = st.selectbox("상수 선택", ["Pi (π)", "Euler's Number (e)", "Golden Ratio (φ)", "Square Root of 2"])
            if "Pi" in const_choice:
                num_input = "314159265358979323846264338327950288419716939937510"
            elif "e" in const_choice:
                num_input = "271828182845904523536028747135266249775724709369995"
            elif "Golden" in const_choice:
                num_input = "161803398874989484820458683436563811772030917980576"
            else:
                num_input = "141421356237309504880168872420969807856967187537694"
            st.caption(f"값: {num_input[:20]}...")
        else:
            num_input = st.text_input("숫자 입력", value="123456789", placeholder="숫자만 입력됩니다")
            num_input = ''.join(filter(str.isdigit, num_input))

    st.markdown("#### 2. Synthesizer Settings")
    with st.container(border=True):
        scale_opt = st.selectbox("🎵 Musical Scale (음계)", list(SCALES.keys()))
        wave_opt = st.selectbox("🌊 Waveform (음색)", ["Sine (Pure)", "Square (Retro)", "Sawtooth (Sharp)"])
        bpm_val = st.slider("⏱️ Tempo (BPM)", 60, 240, 120)
        octave_val = st.slider("🎹 Octave Shift", -1, 1, 0)

    generate_btn = st.button("Generate Audio Stream", use_container_width=True)

with col_right:
    st.markdown("#### 3. Analysis & Output")
    
    if generate_btn and num_input:
        with st.spinner("Processing Waveforms..."):
            # 오디오 생성
            audio_signal = generate_melody(num_input, bpm_val, scale_opt, wave_opt, octave_val)
            
            # 1. 시각화 (Waveform & Note Map)
            # 숫자를 그래프로 매핑하여 '악보'처럼 보이게 함
            note_data = [int(d) for d in num_input if d != '0'][:50]
            st.caption("Sequence Visualization")
            st.bar_chart(note_data, color="#00d4ff", height=150)
            
            # 2. 오디오 플레이어
            virtual_file = io.BytesIO()
            write(virtual_file, 44100, (audio_signal * 32767).astype(np.int16))
            
            st.success("Audio Synthesis Complete.")
            st.audio(virtual_file, format='audio/wav')
            
            # 3. 상세 정보 (수학적 설명)
            with st.expander("See Mathematical Details"):
                st.markdown(f"""
                - **Length:** {len(num_input)} digits
                - **Scale Used:** {scale_opt}
                - **Wave Function:** """)
                if "Sine" in wave_opt:
                    st.latex(r"y(t) = A \cdot \sin(2\pi f t)")
                elif "Square" in wave_opt:
                    st.latex(r"y(t) = A \cdot \text{sgn}(\sin(2\pi f t))")
                else:
                    st.latex(r"y(t) = 2A(ft - \lfloor ft + 0.5 \rfloor)")
                    
            # 4. 다운로드
            st.download_button(
                label="Download .WAV",
                data=virtual_file,
                file_name=f"math_music_{wave_opt.split()[0]}.wav",
                mime="audio/wav"
            )
            
    elif not num_input:
        st.info("좌측 패널에서 데이터를 입력해주세요.")
    else:
        st.write("Ready to synthesize.")
        st.markdown("""
        > "Music is the arithmetic of the soul, which counts without being aware of it."  
        > — Gottfried Wilhelm Leibniz
        """)
