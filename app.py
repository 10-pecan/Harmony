import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Symphony: Middle School", page_icon="🏫", layout="wide")

# --- 2. 디자인 (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;500;700&display=swap');
    
    .stApp {
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    h1, h2, h3, label { color: #ffffff !important; }
    p, span, div { color: #c9d1d9; }

    /* 타이틀 */
    .neo-title {
        font-size: 3.5rem; font-weight: 800; text-align: center;
        background: linear-gradient(to right, #4facfe, #00f2fe);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.5);
        margin-top: 20px;
    }
    .sub-title {
        text-align: center; color: #8b949e !important; margin-bottom: 50px;
    }

    /* 카드 */
    .glass-card {
        background: rgba(30, 30, 40, 0.6);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px; margin-bottom: 25px;
    }

    /* 탭 & 버튼 커스텀 */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #4facfe !important; border-bottom: 3px solid #4facfe !important; font-weight: bold !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        color: #fff !important; border: none; height: 65px; border-radius: 12px;
        font-size: 1.3rem; font-weight: 800;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.4);
    }
    
    /* [NEW] 친절한 설명 박스 */
    .easy-desc {
        background-color: #161b22;
        border-left: 4px solid #4facfe;
        padding: 15px;
        border-radius: 0 10px 10px 0;
        margin-top: 15px;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #e6edf3;
    }
    .easy-desc b { color: #4facfe; }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (안정화 버전) ---
# (이전과 동일한 로직 사용 - 에러 방지 포함)

def generate_wave(freq, duration, wave_type="sine"):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, False)
    if wave_type == "sine": return np.sin(2 * np.pi * freq * t)
    elif wave_type == "saw": return 0.5 * (2 * (freq * t - np.floor(freq * t + 0.5)))
    elif wave_type == "pad": return np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 1.01 * t)
    return np.zeros(num_samples)

def match_length(wave, target_len):
    if len(wave) == target_len: return wave
    elif len(wave) > target_len: return wave[:target_len]
    else: return np.pad(wave, (0, target_len - len(wave)), 'constant')

def apply_envelope(wave, duration, attack_ratio=0.1, release_ratio=0.4):
    total_len = len(wave)
    attack = int(total_len * attack_ratio)
    release = int(total_len * release_ratio)
    sustain = total_len - attack - release
    if sustain < 0: sustain = 0
    env = np.concatenate([np.linspace(0, 1, attack), np.full(sustain, 1.0), np.linspace(1, 0, release)])
    return wave * match_length(env, total_len)

def apply_chorus(wave):
    chorus1 = np.interp(np.arange(0, len(wave), 0.995), np.arange(0, len(wave)), wave)
    chorus2 = np.interp(np.arange(0, len(wave), 1.005), np.arange(0, len(wave)), wave)
    min_len = min(len(wave), len(chorus1), len(chorus2))
    return wave[:min_len] + 0.5 * chorus1[:min_len] + 0.5 * chorus2[:min_len]

def generate_melody_phrase(digit, bpm):
    scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    quarter_note = 60.0 / bpm
    eighth_note = quarter_note / 2
    
    phrases = {
        '1': ([0, 1, 2, 0], [eighth_note]*4, 0, [0, 2, 4]),
        '2': ([1, 2, 3, 1], [eighth_note]*4, 1, [1, 3, 5]),
        '3': ([2, 4, 2], [quarter_note, eighth_note, eighth_note], 2, [2, 4, 6]),
        '4': ([3, 5, 7], [quarter_note]*3, 3, [3, 5, 7]),
        '5': ([4, 3, 2, 1], [eighth_note]*4, 4, [4, 6, 8]),
        '6': ([5, 7, 9], [quarter_note, quarter_note, quarter_note*2], 5, [5, 7, 9]),
        '7': ([6, 5, 4], [quarter_note, eighth_note, eighth_note], 4, [4, 6, 8]),
        '8': ([7, 4, 2, 0], [eighth_note]*4, 0, [0, 2, 4]),
        '9': ([8, 7, 6, 5, 4], [eighth_note]*5, 4, [4, 6, 8]),
        '0': ([], [quarter_note*2], 0, [])
    }
    
    if digit not in phrases or digit == '0': return np.zeros(int(44100 * quarter_note * 2))
    indices, durations, bass_idx, chord_indices = phrases[digit]
    
    melody_pieces = []
    for idx, dur in zip(indices, durations):
        tone = generate_wave(scale[idx], dur, "saw")
        tone = apply_envelope(tone, dur, 0.05, 0.2)
        melody_pieces.append(tone)
    melody_wave = np.concatenate(melody_pieces)
    target_len = len(melody_wave)
    
    pad_wave = np.zeros(target_len)
    total_dur = sum(durations)
    for idx in chord_indices:
        tone = generate_wave(scale[idx], total_dur, "pad")
        pad_wave += match_length(tone, target_len)
    pad_wave = apply_envelope(pad_wave, total_dur, 0.3, 0.5)
    pad_wave = apply_chorus(pad_wave) * 0.4
    
    bass_wave = generate_wave(scale[bass_idx]*0.5, total_dur, "sine")
    bass_wave = match_length(bass_wave, target_len)
    bass_wave = apply_envelope(bass_wave, total_dur, 0.1, 0.3) * 0.6
    
    mix = melody_wave + pad_wave + bass_wave
    mx = np.max(np.abs(mix))
    return mix / mx * 0.9 if mx > 0 else mix

def numbers_to_epic_music(number_str, bpm):
    track = [generate_melody_phrase(char, bpm) for char in number_str if char.isdigit()]
    return np.concatenate(track) if track else None

# --- 4. 메인 UI 구성 ---

st.markdown('<div class="neo-title">MATH SYMPHONY</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">중학교 수학책 속에 숨겨진 웅장한 오케스트라</div>', unsafe_allow_html=True)

col_L, col_R = st.columns([1, 1.4], gap="large")

with col_L:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📚 교과서 속 숫자들")
    
    tab1, tab2 = st.tabs(["🔥 BEST 5", "🖊️ 자유 입력"])
    
    with tab1:
        # [핵심] 중학생 맞춤형 5대 테마
        theme = st.radio("연주할 테마를 고르세요", 
                 [
                     "1. 원주율 (π) - 동그라미의 비밀", 
                     "2. 루트 2 (√2) - 정사각형의 대각선", 
                     "3. 루트 3 (√
