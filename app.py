import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol", page_icon="🎄", layout="wide")

# --- 2. 디자인 (크리스마스 테마 & 눈 내리는 효과) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@400;700&family=Pretendard:wght@300;500;700&display=swap');
    
    .stApp {
        background-color: #0F2027 !important; /* 깊은 겨울 밤색 */
        background: linear-gradient(to bottom, #0F2027, #203A43, #2C5364);
        color: #FFFFFF !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    h1, h2, h3, label { color: #ffffff !important; text-shadow: 0 0 10px #FFD700; }
    p, span, div { color: #E0E0E0; }

    /* [눈 내리는 효과] */
    .snowflake {
        position: fixed; top: 0; z-index: 9999;
        color: #FFF; font-size: 1em; opacity: 0.8;
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { transform: translateY(-10vh); }
        100% { transform: translateY(110vh); }
    }

    /* 타이틀 (크리스마스 폰트) */
    .carol-title {
        font-family: 'Mountains of Christmas', cursive;
        font-size: 4.5rem; font-weight: 700; text-align: center;
        color: #D42426; /* 산타 레드 */
        text-shadow: 2px 2px 0 #165B33, 0 0 20px #FF0000;
        margin-top: 20px;
    }
    .sub-title {
        text-align: center; color: #8FBC8F !important; margin-bottom: 50px; font-size: 1.2rem;
    }

    /* 카드 디자인 (얼음 유리 느낌) */
    .ice-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        padding: 30px; margin-bottom: 25px;
        backdrop-filter: blur(8px);
    }

    /* 탭 커스텀 */
    div[data-baseweb="tab-list"] { background-color: transparent !important; }
    button[data-baseweb="tab"] { color: #AAAAAA !important; border: none !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #D42426 !important; /* 레드 */
        border-bottom: 3px solid #165B33 !important; /* 그린 */
        font-weight: bold !important; background-color: #FFFFFF !important;
        border-radius: 10px 10px 0 0;
    }
    
    /* 재생 버튼 (골드 & 레드) */
    .stButton>button {
        background: linear-gradient(45deg, #D42426, #FFD700) !important;
        color: #fff !important; border: 2px solid #FFF; height: 70px; border-radius: 50px;
        font-size: 1.5rem; font-weight: 800;
        box-shadow: 0 0 20px rgba(212, 36, 38, 0.6);
    }
    .stButton>button:hover { transform: scale(1.05); }

    /* 비주얼라이저 막대 (지팡이 사탕 색) */
    .bar {
        width: 10px; background: repeating-linear-gradient(45deg, #FF0000, #FF0000 10px, #FFFFFF 10px, #FFFFFF 20px);
        border-radius: 5px; animation: bounce 1s infinite ease-in-out;
    }
    
    /* 설명 박스 */
    .gift-desc {
        background-color: #165B33; /* 트리 그린 */
        border-left: 5px solid #D42426;
        padding: 15px; border-radius: 10px;
        color: #FFF; margin-top: 15px;
    }
    .gift-desc b { color: #FFD700; }
</style>
""", unsafe_allow_html=True)

# --- 3. 눈 내리는 애니메이션 HTML 주입 ---
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(1,100)}vw; animation-duration:{np.random.randint(5,15)}s; animation-delay:{np.random.randint(0,5)}s;">❄</div>' for _ in range(20)])
    st.markdown(snow_html, unsafe_allow_html=True)

create_snow()

# --- 4. 오디오 엔진 (캐롤 사운드: Bell & Organ) ---

def generate_wave(freq, duration, wave_type="sine"):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if wave_type == "bell": # 영롱한 종소리 (FM Synthesis 느낌)
        return np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * (freq * 2.0) * t) + 0.3 * np.sin(2 * np.pi * (freq * 3.5) * t)
    elif wave_type == "organ": # 따뜻한 오르간 (Sine 합)
        return np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2 * t) + 0.2 * np.sin(2 * np.pi * freq * 4 * t)
    return np.zeros(num_samples)

def match_length(wave, target_len):
    if len(wave) == target_len: return wave
    elif len(wave) > target_len: return wave[:target_len]
    else: return np.pad(wave, (0, target_len - len(wave)), 'constant')

def apply_envelope(wave, duration, attack_ratio=0.01, release_ratio=0.9):
    # 종소리는 시작이 빠르고(Attack 짧음) 길게 여운이 남음(Release 김)
    total_len = len(wave)
    attack = int(total_len * attack_ratio)
    release = int(total_len * release_ratio)
    sustain = total_len - attack - release
    if sustain < 0: sustain = 0
    env = np.concatenate([np.linspace(0, 1, attack), np.full(sustain, 1.0), np.linspace(1, 0, release)])
    
    # 지수 함수적 감쇠 (더 종소리 같음)
    decay_curve = np.exp(np.linspace(0, -5, total_len))
    
    return wave * match_length(env, total_len) * decay_curve

def generate_carol_phrase(digit, bpm):
    # C Major Scale (Happy Holiday Feel)
    # 도 레 미 파 솔 라 시 높은도
    scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    
    quarter_note = 60.0 / bpm
    eighth_note = quarter_note / 2
    
    # 캐롤스러운 리듬 패턴
    phrases = {
        '1': ([0, 2, 4], [quarter_note]*3, 0, [0, 4, 7]), # 도 미 솔 (Triad)
        '2': ([1, 3, 5], [quarter_note]*3, 1, [1, 5, 8]), # 레 파 라
        '3': ([2, 4, 2], [eighth_note, eighth_note, quarter_note], 2, [0, 2, 4]), # 미솔미
        '4': ([3, 3, 5], [quarter_note, quarter_note, quarter_note], 3, [3, 5, 7]), # 파파라
        '5': ([4, 4, 4], [quarter_note]*3, 4, [0, 4, 7]), # 솔솔솔 (징글벨 느낌)
        '6': ([5, 4, 3, 2], [eighth_note]*4, 0, [3, 5, 7]), 
        '7': ([7, 6, 5], [quarter_note]*3, 4, [4, 6, 8]),
        '8': ([7, 4, 7], [eighth_note, eighth_note, quarter_note], 0, [0, 4, 7]),
        '9': ([0, 4, 7, 4], [eighth_note]*4, 0, [0, 4, 7]),
        '0': ([], [quarter_note*2], 0, [])
    }
    
    if digit not in phrases or digit == '0': return np.zeros(int(44100 * quarter_note * 2))
    indices, durations, bass_idx, chord_indices = phrases[digit]
    
    # 1. Bell Melody (영롱한 종소리)
    melody_pieces = []
    for idx, dur in zip(indices, durations):
        tone = generate_wave(scale[idx], dur, "bell")
        tone = apply_envelope(tone, dur, 0.01, 0.9)
        melody_pieces.append(tone)
    melody_wave = np.concatenate(melody_pieces)
    target_len = len(melody_wave)
    
    # 2. Organ Pad (따뜻한 배경음)
    pad_wave = np.zeros(target_len)
    total_dur = sum(durations)
    for idx in chord_indices:
        tone = generate_wave(scale[idx], total_dur, "organ")
        pad_wave += match_length(tone, target_len)
    pad_wave = pad_wave * np.linspace(0, 1, target_len) # 서서히 커지는 느낌
    pad_wave = match_length(pad_wave, target_len) * 0.3
    
    mix = melody_wave + pad_wave
    mx = np.max(np.abs(mix))
    return mix / mx * 0.9 if mx > 0 else mix

def numbers_to_carol(number_str, bpm):
    track = [generate_carol_phrase(char, bpm) for char in number_str if char.isdigit()]
    return np.concatenate(track) if track else None

# --- 5. 메인 UI ---

st.markdown('<div class="carol-title">Math Carol</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🎅 산타가 보내온 수학 선물 (Ho-Ho-Ho!)</div>', unsafe_allow_html=True)

# Session State
if 'audio_file' not in st.session_state: st.session_state.audio_file = None
if 'is_generated' not in st.session_state: st.session_state.is_generated = False

col_L, col_R = st.columns([1, 1.4], gap="large")

with col_L:
    st.markdown('<div class="ice-card">', unsafe_allow_html=True)
    st.markdown("### 🎁 선물 상자 고르기")
    
    tab1, tab2 = st.tabs(["🎄 크리스마스 트리", "🧦 내 양말"])
    
    with tab1:
        theme = st.radio("연주할 캐롤 테마", 
                 [
                     "1. 루돌프 코 (π) - 반짝이는 원주율", 
                     "2. 굴뚝 각도 (√2) - 산타의 대각선", 
                     "3. 눈사람 비율 (φ) - 황금 비율",
                     "4. 선물 리본 (1/7) - 무한 반복",
                 ], label_visibility="collapsed")
        
        if "루돌프" in theme:
            nums = "314159265358979323846264338327950288419716939937510"
            desc = "<b>🔴 루돌프 코 (Pi):</b> 동그란 루돌프 코처럼 끝이 없는 숫자예요. 종소리가 3번, 1번, 4번... 이렇게 울릴 거예요!"
        elif "굴뚝" in theme:
            nums = "141421356237309504880168872420969807856967187537694"
            desc = "<b>📐 굴뚝 각도 (Root 2):</b> 산타가 굴뚝을 타고 내려올 때 가장 완벽한 각도! 정사각형 선물 상자의 대각선 길이랍니다."
        elif "눈사람" in theme:
            nums = "161803398874989484820458683436563811772030917980576"
            desc = "<b>⛄ 눈사람 비율 (Golden):</b> 눈사람 머리와 몸통의 비율이 1:1.618일 때 제일 귀엽대요. 자연이 만든 캐롤을 들어보세요."
        else:
            nums = "142857142857142857142857142857142857142857142857142"
            desc = "<b>🎀 선물 리본 (1/7):</b> 리본을 묶듯이 계속 반복되는 숫자예요. 징글벨처럼 신나는 리듬이 반복됩니다."

        st.markdown(f"<div class='gift-desc'>{desc}</div>", unsafe_allow_html=True)

    with tab2:
        user_in = st.text_input("숫자 입력 (예: 1225)", placeholder="1225")
        if user_in: nums = ''.join(filter(str.isdigit, user_in))
        elif 'nums' not in locals(): nums = "12251225"

    st.write("")
    bpm = st.slider("🛷 썰매 속도 (BPM)", 80, 180, 120)
    st.markdown('</div>', unsafe_allow_html=True)

with col_R:
    st.markdown('<div class="ice-card">', unsafe_allow_html=True)
    st.markdown("### 🔔 캐롤 연주하기")
    
    if nums:
        digits = [int(d) for d in nums[:25] if d != '0']
        chart_data = pd.DataFrame({'Time': range(len(digits)), 'Note': digits})
        
        # 크리스마스 컬러 차트 (레드/그린)
        c = alt.Chart(chart_data).mark_bar(cornerRadius=5).encode(
            x=alt.X('Time', axis=None),
            y=alt.Y('Note', axis=None, scale=alt.Scale(domain=[0, 10])),
            color=alt.condition(
                alt.datum.Note % 2 == 0,
                alt.value("#D42426"), # 짝수는 레드
                alt.value("#165B33")  # 홀수는 그린
            )
        ).properties(height=150).configure_view(strokeWidth=0)
        
        st.altair_chart(c, use_container_width=True)
        
        st.write("")
        
        if st.button("🎄 Merry Math-mas! (재생)", use_container_width=True):
            with st.spinner("산타가 악보를 가져오는 중... 🛷"):
                audio_data = numbers_to_carol(nums, bpm)
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                
                st.session_state.audio_file = virtual_file
                st.session_state.is_generated = True

        if st.session_state.is_generated:
            # 지팡이 사탕 비주얼라이저
            st.markdown("""
            <div class="visualizer-container" style="display:flex; justify-content:center; gap:5px; height:50px; align-items:flex-end; margin-bottom:10px;">
                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="
