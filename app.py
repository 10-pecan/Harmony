import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Symphony", page_icon="🎻", layout="wide")

# --- 2. 디자인 & CSS 애니메이션 (핵심!) ---
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
    div[data-baseweb="tab-list"] { background-color: transparent !important; }
    button[data-baseweb="tab"] { background-color: transparent !important; color: #8b949e !important; border: none !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #4facfe !important; border-bottom: 3px solid #4facfe !important; font-weight: bold !important; background-color: transparent !important;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        color: #fff !important; border: none; height: 65px; border-radius: 12px;
        font-size: 1.3rem; font-weight: 800;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.4);
        width: 100%;
    }
    
    /* 입력창 */
    .stTextInput input {
        background-color: #161b22 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }

    /* 친절한 설명 박스 */
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

    /* [NEW] CSS로 만든 움직이는 비주얼라이저 (절대 안깨짐) */
    .visualizer-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        height: 60px;
        gap: 5px;
        margin-bottom: 20px;
        margin-top: 10px;
    }
    .bar {
        width: 8px;
        background: linear-gradient(to top, #4facfe, #00f2fe);
        border-radius: 5px;
        animation: bounce 1s infinite ease-in-out;
    }
    .bar:nth-child(1) { height: 20px; animation-delay: 0.0s; }
    .bar:nth-child(2) { height: 40px; animation-delay: 0.1s; }
    .bar:nth-child(3) { height: 50px; animation-delay: 0.2s; }
    .bar:nth-child(4) { height: 30px; animation-delay: 0.3s; }
    .bar:nth-child(5) { height: 20px; animation-delay: 0.4s; }
    .bar:nth-child(6) { height: 45px; animation-delay: 0.2s; }
    .bar:nth-child(7) { height: 55px; animation-delay: 0.1s; }
    .bar:nth-child(8) { height: 35px; animation-delay: 0.3s; }
    .bar:nth-child(9) { height: 25px; animation-delay: 0.0s; }
    .bar:nth-child(10) { height: 40px; animation-delay: 0.2s; }

    @keyframes bounce {
        0%, 100% { transform: scaleY(0.3); opacity: 0.5; }
        50% { transform: scaleY(1.2); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 ---
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
    if sustain < 0:
        attack = total_len // 2
        release = total_len - attack
        sustain = 0
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
    pad_wave = match_length(pad_wave, target_len)
    
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

# [FIX] Session State 초기화 (음악 저장용)
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'is_generated' not in st.session_state:
    st.session_state.is_generated = False

col_L, col_R = st.columns([1, 1.4], gap="large")

with col_L:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📚 교과서 속 숫자들")
    
    tab1, tab2 = st.tabs(["🔥 BEST 5", "🖊️ 자유 입력"])
    
    with tab1:
        theme = st.radio("연주할 테마를 고르세요", 
                 [
                     "1. 원주율 (π) - 동그라미의 비밀", 
                     "2. 루트 2 (√2) - 정사각형의 대각선", 
                     "3. 루트 3 (√3) - 정삼각형의 높이",
                     "4. 황금비 (φ) - 가장 아름다운 비율",
                     "5. 순환소수 (1/7) - 도돌이표 숫자"
                 ], label_visibility="collapsed")
        
        if "원주율" in theme:
            nums = "314159265358979323846264338327950288419716939937510"
            desc_title = "⭕ 원주율 (Pi, 3.14...)"
            desc_text = "초등학교 땐 3.14로 배웠지만, 사실은 끝없이 이어지는 무한한 숫자예요. 원의 둘레를 구할 때 꼭 필요하죠!"
        elif "루트 2" in theme:
            nums = "141421356237309504880168872420969807856967187537694"
            desc_title = "📐 루트 2 (Square Root 2, 1.414...)"
            desc_text = "한 변이 1인 정사각형의 대각선 길이! 중3 피타고라스 정리 시간에 맨 처음 배우는 '무리수'의 대표 선수입니다."
        elif "루트 3" in theme:
            nums = "173205080756887729352744634150587236694280525381038"
            desc_title = "🔺 루트 3 (Square Root 3, 1.732...)"
            desc_text = "정삼각형을 반으로 잘랐을 때 나오는 높이예요. 입체도형(정육면체) 대각선 구할 때도 등장하는 단골손님!"
        elif "황금비" in theme:
            nums = "161803398874989484820458683436563811772030917980576"
            desc_title = "✨ 황금비 (Golden Ratio, 1.618...)"
            desc_text = "신용카드, 파르테논 신전, 모나리자의 공통점? 바로 1:1.618 비율이 숨어있다는 것! 인간이 가장 편안함을 느끼는 비율이래요."
        else:
            nums = "142857142857142857142857142857142857142857142857142"
            desc_title = "🔄 순환소수 (1/7, 0.142857...)"
            desc_text = "1 나누기 7을 해보세요. 142857 여섯 숫자가 도돌이표처럼 계속 반복되죠? 음악으로 치면 '무한 반복 재생' 구간입니다."

        st.markdown(f"<div class='easy-desc'><b>{desc_title}</b><br>{desc_text}</div>", unsafe_allow_html=True)

    with tab2:
        user_in = st.text_input("숫자를 입력하세요", placeholder="20250101")
        if user_in: nums = ''.join(filter(str.isdigit, user_in))
        elif 'nums' not in locals(): nums = "314159"

    st.write("")
    bpm = st.slider("🎛️ BPM (빠르기)", 60, 160, 110)
    st.markdown('</div>', unsafe_allow_html=True)

with col_R:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎚️ 비주얼라이저 & 재생")
    
    if nums:
        digits = [int(d) for d in nums[:25] if d != '0']
        chart_data = pd.DataFrame({'Time': range(len(digits)), 'Note': digits})
        
        c = alt.Chart(chart_data).mark_area(
            line={'color':'#4facfe'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#4facfe', offset=0),
                       alt.GradientStop(color='rgba(79, 172, 254, 0)', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x=alt.X('Time', axis=None),
            y=alt.Y('Note', axis=None, scale=alt.Scale(domain=[0, 10]))
        ).properties(height=150).configure_view(strokeWidth=0)
        
        st.altair_chart(c, use_container_width=True)
        
        st.write("")
        
        # 버튼을 누르면 계산 후 Session State에 저장
        if st.button("▶️ 연주 시작 (PLAY)", use_container_width=True):
            with st.spinner("악보를 그리는 중... 🎼"):
                audio_data = numbers_to_epic_music(nums, bpm)
                
                # 가상의 파일로 저장
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                
                # 세션에 저장 (이래야 리셋 안됨!)
                st.session_state.audio_file = virtual_file
                st.session_state.is_generated = True

        # [FIX] 저장된 음악과 비주얼라이저 표시
        if st.session_state.is_generated:
            # 1. CSS 애니메이션 비주얼라이저 (절대 안깨짐)
            st.markdown("""
            <div class="visualizer-container">
                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. 오디오 플레이어
            st.audio(st.session_state.audio_file, format='audio/wav')
            st.success("Now Playing... 🎵")
                
    else:
        st.warning("숫자가 입력되지 않았습니다.")
        
    st.markdown('</div>', unsafe_allow_html=True)
