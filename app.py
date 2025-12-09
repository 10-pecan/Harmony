import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Neo-Symphony", page_icon="🎹", layout="wide")

# --- 2. 디자인 (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Pretendard:wght@300;500&display=swap');
    
    .stApp {
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    h1, h2, h3, label { color: #ffffff !important; }
    p, span, div { color: #c9d1d9; }

    .neo-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(to right, #00f260, #0575e6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(5, 117, 230, 0.5);
    }
    .sub-title {
        text-align: center; color: #8b949e !important; margin-bottom: 40px;
    }

    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        padding: 30px;
        margin-bottom: 25px;
    }

    /* 탭 스타일 */
    div[data-baseweb="tab-list"] { background-color: transparent !important; }
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #8b949e !important;
        border: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(5, 117, 230, 0.1) !important;
        color: #58a6ff !important;
        border-bottom: 3px solid #58a6ff !important;
        font-weight: bold !important;
    }

    .stTextInput input {
        background-color: #0d1117 !important;
        color: #fff !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
    }
    .stButton>button {
        background: linear-gradient(45deg, #00f260, #0575e6) !important;
        color: #fff !important;
        border: none;
        height: 60px; font-size: 1.2rem; font-weight: bold;
        box-shadow: 0 0 15px rgba(5, 117, 230, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(5, 117, 230, 0.7); transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (길이 보정 로직 추가됨) ---

def generate_wave(freq, duration, wave_type="sine"):
    sample_rate = 44100
    # 길이를 정수로 정확하게 변환
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if wave_type == "sine":
        return np.sin(2 * np.pi * freq * t)
    elif wave_type == "saw":
        return 0.5 * (2 * (freq * t - np.floor(freq * t + 0.5)))
    elif wave_type == "pad":
        return np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 1.01 * t)
    return np.zeros(num_samples)

def match_length(wave, target_len):
    """[NEW] 두 파형의 길이를 강제로 맞춰주는 함수 (에러 방지용)"""
    if len(wave) == target_len:
        return wave
    elif len(wave) > target_len:
        return wave[:target_len]
    else:
        return np.pad(wave, (0, target_len - len(wave)), 'constant')

def apply_envelope(wave, duration, attack_ratio=0.1, release_ratio=0.4):
    total_len = len(wave)
    attack = int(total_len * attack_ratio)
    release = int(total_len * release_ratio)
    sustain = total_len - attack - release
    
    # 길이가 0이거나 음수인 경우 방지
    if sustain < 0: sustain = 0
    
    env = np.concatenate([
        np.linspace(0, 1, attack),
        np.full(sustain, 1.0),
        np.linspace(1, 0, release)
    ])
    
    # 길이 보정
    env = match_length(env, total_len)
    return wave * env

def apply_chorus(wave):
    # 코러스 효과
    chorus1 = np.interp(np.arange(0, len(wave), 0.995), np.arange(0, len(wave)), wave)
    chorus2 = np.interp(np.arange(0, len(wave), 1.005), np.arange(0, len(wave)), wave)
    
    # 길이 보정 (가장 짧은 쪽에 맞춤)
    min_len = min(len(wave), len(chorus1), len(chorus2))
    return wave[:min_len] + 0.5 * chorus1[:min_len] + 0.5 * chorus2[:min_len]

def generate_melody_phrase(digit, bpm):
    # 음계 주파수
    C4, D4, E4, F4, G4, A4, B4 = 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88
    C5, D5, E5 = 523.25, 587.33, 659.25
    
    quarter_note = 60.0 / bpm
    eighth_note = quarter_note / 2
    
    phrases = {
        '1': ([C4, D4, E4, C4], [eighth_note]*4, C4/2, [C4, E4, G4]),
        '2': ([D4, E4, F4, D4], [eighth_note]*4, D4/2, [D4, F4, A4]),
        '3': ([E4, G4, E4], [quarter_note, eighth_note, eighth_note], E4/2, [E4, G4, B4]),
        '4': ([F4, A4, C5], [quarter_note]*3, F4/2, [F4, A4, C5]),
        '5': ([G4, F4, E4, D4], [eighth_note]*4, G4/2, [G4, B4, D5]),
        '6': ([A4, C5, E5], [quarter_note, quarter_note, quarter_note*2], A4/2, [A4, C5, E5]),
        '7': ([B4, A4, G4], [quarter_note, eighth_note, eighth_note], G4/2, [G4, B4, D5]),
        '8': ([C5, G4, E4, C4], [eighth_note]*4, C4/2, [C4, E4, G4]),
        '9': ([D5, C5, B4, A4, G4], [eighth_note]*5, G4/2, [G4, B4, D5]),
        '0': ([], [quarter_note*2], 0, [])
    }
    
    if digit not in phrases or digit == '0':
        return np.zeros(int(44100 * quarter_note * 2))
        
    notes, durations, bass_freq, chord_freqs = phrases[digit]
    
    # 1. Lead Melody 생성
    melody_pieces = []
    for freq, dur in zip(notes, durations):
        tone = generate_wave(freq, dur, "saw")
        tone = apply_envelope(tone, dur, 0.05, 0.2)
        melody_pieces.append(tone)
    
    melody_wave = np.concatenate(melody_pieces)
    target_len = len(melody_wave) # [핵심] 이 길이를 기준으로 모두 맞춤!
    
    # 2. Harmony Pad 생성 (길이 강제 보정)
    pad_wave = np.zeros(target_len)
    total_duration = sum(durations) # 근사값
    
    for freq in chord_freqs:
        tone = generate_wave(freq, total_duration, "pad")
        tone = match_length(tone, target_len) # [FIX] 길이 맞추기
        pad_wave += tone
        
    pad_wave = apply_envelope(pad_wave, total_duration, 0.3, 0.5)
    pad_wave = apply_chorus(pad_wave)
    pad_wave = match_length(pad_wave, target_len) # 코러스 후 다시 맞추기
    pad_wave = pad_wave * 0.4 
    
    # 3. Bass 생성 (길이 강제 보정)
    bass_wave = generate_wave(bass_freq, total_duration, "sine")
    bass_wave = match_length(bass_wave, target_len) # [FIX] 길이 맞추기
    bass_wave = apply_envelope(bass_wave, total_duration, 0.1, 0.3) * 0.6
    
    # 4. Final Mix
    final_mix = melody_wave + pad_wave + bass_wave
    
    # 볼륨 정규화
    max_val = np.max(np.abs(final_mix))
    if max_val > 0:
        final_mix = final_mix / max_val * 0.9
        
    return final_mix

def numbers_to_epic_music(number_str, bpm):
    full_track = []
    for char in number_str:
        if char.isdigit():
            phrase = generate_melody_phrase(char, bpm)
            full_track.append(phrase)
            
    if not full_track: return None
    return np.concatenate(full_track)

# --- 4. 메인 UI ---

st.markdown('<div class="neo-title">NEO-SYMPHONY</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">수학적 배열이 만들어내는 웅장한 전자 음악의 세계</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.3], gap="large")

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 💿 Source Data (데이터 소스)")
    
    tab_math, tab_custom = st.tabs(["🌌 Cosmic Numbers", "🖊️ Custom Input"])
    
    with tab_math:
        math_choice = st.radio("연주할 테마 선택", 
                              ["Track π (Pi)", "Track φ (Golden)", "Track e (Euler)"])
        if "π" in math_choice: nums = "314159265358979323846264338327950288419716939937510"
        elif "φ" in math_choice: nums = "161803398874989484820458683436563811772030917980576"
        else: nums = "271828182845904523536028747135266249775724709369995"

    with tab_custom:
        user_input = st.text_input("나만의 숫자열 입력", placeholder="예: 20240101")
        if user_input: nums = ''.join(filter(str.isdigit, user_input))
        elif 'nums' not in locals(): nums = "314159"

    st.write("")
    bpm = st.slider("🎛️ BPM (Tempo)", 60, 160, 100)
    st.markdown('</div>', unsafe_allow_html=True)

    st.info("""
    💡 **사운드 엔진 안정화**
    이제 부동소수점 오차 없이 정확한 길이로 합성되어
    에러 없이 완벽한 하모니를 재생합니다.
    """)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Visualizer & Playback")
    
    if nums:
        digits = [int(d) for d in nums[:20] if d != '0']
        chart_data = pd.DataFrame({'Time': range(len(digits)), 'Note': digits})
        
        chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('Time', axis=None),
            y=alt.Y('Note', axis=None, scale=alt.Scale(domain=[0, 10])),
            color=alt.value("#00f260"),
            tooltip=['Note']
        ).properties(height=250).configure_view(strokeWidth=0)
        
        st.altair_chart(chart, use_container_width=True)
        st.caption(f"Sequence: {nums[:15]}...")
        
        st.write("")
        
        if st.button("▶️ GENERATE EPIC TRACK", use_container_width=True):
            with st.spinner("합성 엔진 가동 중... 사운드 레이어링... 🎧"):
                audio_data = numbers_to_epic_music(nums, bpm)
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                
                st.audio(virtual_file, format='audio/wav')
                st.success("트랙 생성이 완료되었습니다. 볼륨을 높이세요!")
    else:
        st.warning("숫자를 입력해주세요.")
        
    st.markdown('</div>', unsafe_allow_html=True)
