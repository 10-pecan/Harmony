import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 (세련된 다크 테마) ---
st.set_page_config(page_title="Neo-Symphony", page_icon="🎹", layout="wide")

# --- 2. 강력한 디자인 업그레이드 (CSS) ---
st.markdown("""
<style>
    /* [폰트 & 기본 배경] 어둡고 세련되게 */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Pretendard:wght@300;500&display=swap');
    
    .stApp {
        background-color: #0d1117 !important; /* 깊은 우주색 */
        color: #c9d1d9 !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    h1, h2, h3, label { color: #ffffff !important; }
    p, span, div { color: #c9d1d9; }

    /* [네온 타이틀] */
    .neo-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(to right, #00f260, #0575e6); /* 네온 그린/블루 */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(5, 117, 230, 0.5);
    }
    .sub-title {
        text-align: center; color: #8b949e !important; margin-bottom: 40px;
    }

    /* [글래스모피즘 카드 UI] */
    .glass-card {
        background: rgba(22, 27, 34, 0.7); /* 반투명 배경 */
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur( 10px );
        -webkit-backdrop-filter: blur( 10px );
        padding: 30px;
        margin-bottom: 25px;
    }

    /* [탭 스타일 완전 정복] - 드디어 해결! */
    /* 탭 컨테이너 배경 투명하게 */
    div[data-baseweb="tab-list"] { background-color: transparent !important; }
    
    /* 선택 안 된 탭 */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #8b949e !important;
        border: none !important;
        font-weight: 500 !important;
    }
    
    /* 선택된 탭 (네온 효과) */
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(5, 117, 230, 0.1) !important; /* 연한 네온 배경 */
        color: #58a6ff !important; /* 밝은 네온 블루 글씨 */
        border-bottom: 3px solid #58a6ff !important;
        font-weight: bold !important;
    }

    /* [입력창 & 버튼] */
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

# --- 3. 오디오 엔진 (Epic & Melodic) ---
# 숫자 하나에 '멜로디 프레이즈'를 매핑하고, 화음과 코러스를 쌓습니다.

def generate_wave(freq, duration, wave_type="sine"):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    if wave_type == "sine":
        return np.sin(2 * np.pi * freq * t)
    elif wave_type == "saw": # 리드 멜로디용 (날카로움)
        return 0.5 * (2 * (freq * t - np.floor(freq * t + 0.5)))
    elif wave_type == "pad": # 화음용 (부드럽고 넓음)
        return np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 1.01 * t)

def apply_envelope(wave, duration, attack_ratio=0.1, release_ratio=0.4):
    total_len = len(wave)
    attack = int(total_len * attack_ratio)
    release = int(total_len * release_ratio)
    sustain = total_len - attack - release
    
    env = np.concatenate([
        np.linspace(0, 1, attack),
        np.full(sustain, 1.0),
        np.linspace(1, 0, release)
    ])
    # 길이 보정
    if len(env) < total_len: env = np.pad(env, (0, total_len - len(env)), 'constant')
    else: env = env[:total_len]
    return wave * env

def apply_chorus(wave):
    # [Chorus Effect] 천상의 목소리처럼 풍성하게 만듦
    # 미세하게 피치가 다른 파형을 여러 개 겹침
    chorus1 = np.interp(np.arange(0, len(wave), 0.995), np.arange(0, len(wave)), wave)
    chorus2 = np.interp(np.arange(0, len(wave), 1.005), np.arange(0, len(wave)), wave)
    
    # 길이 맞추기
    min_len = min(len(wave), len(chorus1), len(chorus2))
    return wave[:min_len] + 0.5 * chorus1[:min_len] + 0.5 * chorus2[:min_len]

def generate_melody_phrase(digit, bpm):
    # C Major Scale Frequencies
    C4, D4, E4, F4, G4, A4, B4 = 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88
    C5, D5, E5 = 523.25, 587.33, 659.25
    
    quarter_note = 60.0 / bpm
    eighth_note = quarter_note / 2
    
    # [핵심] 숫자별 멜로디 프레이즈 및 리듬 정의
    # (음표 리스트, 길이 리스트, 베이스 음, 코드 음)
    phrases = {
        '1': ([C4, D4, E4, C4], [eighth_note]*4, C4/2, [C4, E4, G4]), # 도레미도
        '2': ([D4, E4, F4, D4], [eighth_note]*4, D4/2, [D4, F4, A4]),
        '3': ([E4, G4, E4], [quarter_note, eighth_note, eighth_note], E4/2, [E4, G4, B4]), # 미~ 솔미
        '4': ([F4, A4, C5], [quarter_note]*3, F4/2, [F4, A4, C5]), # 파 라 도
        '5': ([G4, F4, E4, D4], [eighth_note]*4, G4/2, [G4, B4, D5]), # 솔파미레
        '6': ([A4, C5, E5], [quarter_note, quarter_note, quarter_note*2], A4/2, [A4, C5, E5]), # 라 도 미~
        '7': ([B4, A4, G4], [quarter_note, eighth_note, eighth_note], G4/2, [G4, B4, D5]), # 시 라 솔
        '8': ([C5, G4, E4, C4], [eighth_note]*4, C4/2, [C4, E4, G4]), # 높은도 솔 미 도
        '9': ([D5, C5, B4, A4, G4], [eighth_note]*5, G4/2, [G4, B4, D5]),
        '0': ([], [quarter_note*2], 0, []) # 쉼표
    }
    
    if digit not in phrases or digit == '0':
        return np.zeros(int(44100 * quarter_note * 2))
        
    notes, durations, bass_freq, chord_freqs = phrases[digit]
    total_duration = sum(durations)
    
    # 1. Lead Melody (선명한 멜로디)
    melody_wave = np.array([])
    for freq, dur in zip(notes, durations):
        tone = generate_wave(freq, dur, "saw")
        tone = apply_envelope(tone, dur, 0.05, 0.2)
        melody_wave = np.concatenate([melody_wave, tone])
        
    # 2. Harmony Pad (배경 화음 + 코러스 효과)
    pad_wave = np.zeros(len(melody_wave))
    for freq in chord_freqs:
        tone = generate_wave(freq, total_duration, "pad")
        pad_wave += tone
    pad_wave = apply_envelope(pad_wave, total_duration, 0.3, 0.5) # 부드럽게 시작
    pad_wave = apply_chorus(pad_wave) * 0.4 # 코러스 적용 및 볼륨 조절
    
    # 3. Bass (묵직한 저음)
    bass_wave = generate_wave(bass_freq, total_duration, "sine")
    bass_wave = apply_envelope(bass_wave, total_duration, 0.1, 0.3) * 0.6
    
    # 믹싱
    final_mix = melody_wave + pad_wave + bass_wave
    return final_mix / np.max(np.abs(final_mix)) * 0.9 # 볼륨 정규화

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
    
    # 탭 디자인 CSS 적용 확인
    tab_math, tab_custom = st.tabs(["🌌 Cosmic Numbers", "🖊️ Custom Input"])
    
    with tab_math:
        math_choice = st.radio("연주할 테마 선택", 
                              ["Track π (Pi) - 영원한 순환", "Track φ (Golden) - 완벽한 비율", "Track e (Euler) - 성장의 궤적"])
        if "π" in math_choice: nums = "314159265358979323846264338327950288419716939937510"
        elif "φ" in math_choice: nums = "161803398874989484820458683436563811772030917980576"
        else: nums = "271828182845904523536028747135266249775724709369995"

    with tab_custom:
        user_input = st.text_input("나만의 숫자열 입력", placeholder="예: 20240101")
        if user_input: nums = ''.join(filter(str.isdigit, user_input))
        elif 'nums' not in locals(): nums = "314159" # 기본값

    st.write("")
    bpm = st.slider("🎛️ BPM (Tempo)", 60, 160, 100)
    st.markdown('</div>', unsafe_allow_html=True)

    st.info("""
    💡 **사운드 엔진 업그레이드**
    단순한 화음이 아닙니다. 숫자 하나가 **리드 멜로디 + 화음 패드(코러스 효과) + 베이스**로 구성된
    하나의 **짧은 음악 프레이즈(Phrase)**를 재생합니다. 훨씬 다이나믹하고 웅장합니다.
    """)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Visualizer & Playback")
    
    if nums:
        # 네온 스타일 차트
        digits = [int(d) for d in nums[:20] if d != '0']
        chart_data = pd.DataFrame({'Time': range(len(digits)), 'Note': digits})
        
        chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('Time', axis=None),
            y=alt.Y('Note', axis=None, scale=alt.Scale(domain=[0, 10])),
            color=alt.value("#00f260"), # 네온 그린 색상
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
