import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 (시네마틱 모드) ---
st.set_page_config(page_title="Math Cinema", page_icon="🎬", layout="wide")

# --- 2. 🎨 High-End CSS (Apple/Netflix Style) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;600;800&family=Noto+Sans+KR:wght@300;500;700&display=swap');
    
    /* [Global] Deep Cinematic Dark */
    .stApp {
        background-color: #000000 !important;
        color: #E5E5E5 !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
    }

    /* [Typography] Apple Style Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        letter-spacing: -1.5px;
        color: #FFFFFF !important;
    }
    
    /* [Hero Title] Pixar Intro Style */
    .hero-container {
        text-align: center; padding: 60px 0;
        background: radial-gradient(circle at center, #2b2b2b 0%, #000000 70%);
    }
    .hero-title {
        font-size: 5rem; font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #888888 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px rgba(255,255,255,0.1);
        margin-bottom: 10px;
    }
    .hero-subtitle {
        color: #888; font-size: 1.2rem; font-weight: 300; letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* [Glassmorphism Card] Netflix Style Containers */
    .glass-card {
        background: rgba(30, 30, 30, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px; margin-bottom: 30px;
        transition: transform 0.3s ease;
    }
    .glass-card:hover { border-color: rgba(255, 255, 255, 0.3); }

    /* [Educational Badge] Tag Style */
    .math-badge {
        display: inline-block; padding: 5px 12px;
        border-radius: 20px; background: rgba(0, 122, 255, 0.2);
        color: #409CFF; font-size: 0.8rem; font-weight: 700;
        margin-bottom: 15px; border: 1px solid rgba(0, 122, 255, 0.4);
    }

    /* [Custom Tabs] Minimalist */
    div[data-baseweb="tab-list"] { background: transparent !important; gap: 30px; border-bottom: 1px solid #333; }
    button[data-baseweb="tab"] {
        background: transparent !important; border: none !important;
        color: #666 !important; font-size: 1.1rem !important; font-weight: 500 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFF !important; font-weight: 700 !important;
        border-bottom: 2px solid #FFF !important;
    }

    /* [Play Button] High Contrast Action */
    .stButton>button {
        background: #FFFFFF !important; color: #000000 !important;
        border: none; border-radius: 12px;
        height: 60px; font-size: 1.1rem; font-weight: 700; letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        width: 100%;
    }
    .stButton>button:hover {
        transform: scale(1.02); box-shadow: 0 0 30px rgba(255, 255, 255, 0.2);
    }
    
    /* [Input Field] Dark Mode Optimized */
    .stTextInput input {
        background: #111 !important; color: #FFF !important;
        border: 1px solid #333 !important; border-radius: 12px !important;
        text-align: center; letter-spacing: 3px; font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 🎻 Cinematic Audio Engine (Motif-Based) ---
# 숫자 하나를 '음표'가 아닌 '테마(Motif)'로 해석합니다.

def get_wave(freq, duration, type="piano"):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), False)
    
    if type == "piano": # 부드러운 피아노 (Sine + Harmonics)
        return 0.6*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)*np.exp(-2*t) + 0.1*np.sin(2*np.pi*freq*3*t)*np.exp(-3*t)
    elif type == "strings": # 웅장한 현악기 (Sawtooth Filtered)
        return 0.4*np.sin(2*np.pi*freq*t) + 0.4*np.sin(2*np.pi*(freq*1.01)*t) + 0.2*np.sin(2*np.pi*(freq*0.99)*t)
    elif type == "bass": # 영화관 둥- 하는 베이스
        return 0.8*np.sin(2*np.pi*(freq*0.5)*t) + 0.2*np.sin(2*np.pi*freq*t)
    return np.zeros_like(t)

def apply_envelope(wave, duration, type="long"):
    length = len(wave)
    if type == "percussive": # 피아노/벨
        env = np.exp(np.linspace(0, -3, length))
    else: # 스트링/패드 (서서히 켜짐)
        att = int(length * 0.2)
        rel = int(length * 0.4)
        sus = length - att - rel
        env = np.concatenate([np.linspace(0, 1, att), np.full(sus, 1.0), np.linspace(1, 0, rel)])
    
    if len(env) != length: env = np.resize(env, length)
    return wave * env

def create_motif(digit, bpm):
    # D Lydian Scale (Pixar/Disney 느낌의 몽환적인 스케일)
    # D(레) E(미) F#(파#) G#(솔#) A(라) B(시) C#(도#)
    scale = [293.66, 329.63, 369.99, 415.30, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    
    beat_sec = 60.0 / bpm
    idx = int(digit) if digit.isdigit() else 0
    base_freq = scale[idx % len(scale)]
    
    # [핵심] 숫자별 '음악적 프레이즈' (2~4초 길이)
    # 단순히 '띵'이 아니라, '따-다-단~' 하는 멜로디 덩어리를 만듭니다.
    
    motif_waves = []
    
    # 1. 멜로디 라인 (Piano/Celesta)
    if idx % 3 == 0: # 상승하는 희망찬 멜로디
        sequence = [(base_freq, 0.5), (base_freq*1.25, 0.5), (base_freq*1.5, 2.0)]
    elif idx % 3 == 1: # 감성적인 아르페지오
        sequence = [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 2.0)]
    else: # 웅장한 롱 노트
        sequence = [(base_freq, 3.0)]
        
    for f, dur in sequence:
        dur_s = dur * beat_sec
        w = get_wave(f, dur_s, "piano")
        w = apply_envelope(w, dur_s, "percussive")
        motif_waves.append(w)
        
    melody_layer = np.concatenate(motif_waves)
    total_len = len(melody_layer)
    
    # 2. 배경 화음 (Strings) - 웅장함 추가
    pad_freq = base_freq * 0.5 # 1옥타브 아래
    pad_layer = get_wave(pad_freq, total_len/44100, "strings")
    pad_layer += get_wave(pad_freq * 1.5, total_len/44100, "strings") # 5도 화음
    pad_layer = apply_envelope(pad_layer, total_len/44100, "long") * 0.4
    
    # 3. 서브 베이스 (Cinematic Bass) - 2옥타브 아래
    bass_layer = get_wave(base_freq * 0.25, total_len/44100, "bass")
    bass_layer = apply_envelope(bass_layer, total_len/44100, "long") * 0.5
    
    # 믹싱
    return melody_layer + pad_layer + bass_layer

def compose_cinematic_score(nums, bpm):
    track = [create_motif(char, bpm) for char in nums if char.isdigit()]
    if not track: return None
    
    # 트랙 연결 및 리버브(공간감) 추가
    full = np.concatenate(track)
    
    # Reverb (Concert Hall)
    delay = int(44100 * 0.4)
    reverb = np.zeros(len(full) + delay)
    reverb[:len(full)] += full
    reverb[delay:] += full * 0.5
    
    m = np.max(np.abs(reverb))
    return reverb / m * 0.95 if m > 0 else reverb

# --- 4. Main UI Structure ---

# [Hero Section]
st.markdown("""
<div class="hero-container">
    <div class="hero-title">MATH CINEMA</div>
    <div class="hero-subtitle">Original Soundtrack generated by Numbers</div>
</div>
""", unsafe_allow_html=True)

# [Main Content]
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.markdown("### 💿 Select Theme")
    
    tab1, tab2, tab3 = st.tabs(["⭕ Infinite Pi", "📐 Pythagoras", "✨ Golden Ratio"])
    
    with tab1:
        nums = "314159265358979323846264338327950288419716939937510"
        title = "원주율 (Pi, 3.14...)"
        badge = "중1 수학: 원의 성질"
        desc = """
        원은 시작과 끝이 없는 도형입니다. 원주율(π) 또한 영원히 반복되지 않는 숫자의 나열이죠.
        이 불규칙한 숫자들이 만들어내는 **'예측 불가능한 멜로디'**는 마치 우리네 인생과 닮아 있습니다.
        """
    with tab2:
        nums = "141421356237309504880168872420969807856967187537694"
        title = "루트 2 (Square Root 2)"
        badge = "중3 수학: 실수와 무리수"
        desc = """
        정사각형의 대각선 길이는 자로 정확히 잴 수 없는 '무리수'입니다.
        인류가 처음으로 발견한 이 '비밀스러운 숫자'는 
        단단하고 웅장한 **대서사시 같은 음악**을 만들어냅니다.
        """
    with tab3:
        nums = "161803398874989484820458683436563811772030917980576"
        title = "황금비 (Golden Ratio)"
        badge = "중2 수학: 닮음과 비"
        desc = """
        1 : 1.618. 자연이 가장 사랑하는 비율입니다.
        꽃잎의 배열부터 은하계의 나선까지, 
        이 비율을 음악으로 옮기면 **가장 편안하고 아름다운 화음**이 흐릅니다.
        """

    # [Educational Card - Netflix Style]
    st.markdown(f"""
    <div class="glass-card">
        <span class="math-badge">{badge}</span>
        <h2>{title}</h2>
        <p style="color:#AAA; line-height:1.6; font-size:1.05rem;">{desc}</p>
        <br>
        <div style="display:flex; justify-content:space-between; color:#666; font-size:0.9rem;">
            <span>Genere: Cinematic / Classical</span>
            <span>Duration: Infinite</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom Input
    user_in = st.text_input("Custom Number Sequence", placeholder="Type your special numbers...")
    if user_in: nums = "".join(filter(str.isdigit, user_in))

with col2:
    st.markdown("### 🎼 Visualizer")
    
    if nums:
        # [Visualizer - Apple Music Style]
        # Smooth Area Chart with Gradient
        digits = [int(d) for d in nums[:30] if d != '0']
        df = pd.DataFrame({'Time': range(len(digits)), 'Pitch': digits})
        
        c = alt.Chart(df).mark_area(
            interpolate='basis', # 아주 부드러운 곡선
            fillOpacity=0.6
        ).encode(
            x=alt.X('Time', axis=None),
            y=alt.Y('Pitch', axis=None, scale=alt.Scale(domain=[-2, 12])),
            color=alt.value("white")
        ).properties(
            height=300, 
            background='transparent'
        ).configure_view(strokeWidth=0)
        
        st.altair_chart(c, use_container_width=True)
        
        # Play Button Logic
        if st.button("▶ Play Cinematic Score"):
            with st.spinner("Composing Original Soundtrack..."):
                # BPM 80 (느리고 웅장하게)
                audio_data = compose_cinematic_score(nums, bpm=80)
                
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                
                st.audio(virtual_file, format='audio/wav')
                
                # "Now Playing" Toast
                st.toast(f"Now Playing: {title}", icon="🎵")

    else:
        st.info("Please select a theme or enter numbers.")

# --- 5. Footer (Credits) ---
st.markdown("""
<div style="text-align:center; color:#444; margin-top:50px; font-size:0.8rem;">
    Mathematics × Music Visualization Project<br>
    Designed for Middle School Education
</div>
""", unsafe_allow_html=True)
