import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Royal Math Symphony", page_icon="🎄", layout="wide")

# --- 2. 최고급 디자인 (Royal Winter Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Noto+Serif+KR:wght@300;500;700&display=swap');
    
    /* [배경] 깊은 밤의 오로라 (Royal Navy & Gold) */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1a2a6c, #b21f1f, #fdbb2d) !important; /* 오로라 느낌 */
        background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364) !important; /* 깊은 겨울밤 */
        color: #fdfdfd !important;
        font-family: 'Noto Serif KR', serif !important;
    }

    /* [눈 내리는 효과 - 우아하게] */
    .snowflake {
        position: fixed; top: -10px; z-index: 0;
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.2em; text-shadow: 0 0 5px #FFF;
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { transform: translateY(-10vh) rotate(0deg); opacity: 0; }
        20% { opacity: 1; }
        100% { transform: translateY(110vh) rotate(360deg); opacity: 0.2; }
    }

    /* [타이포그래피] 황금빛 세리프 */
    .royal-title {
        font-family: 'Cinzel', serif;
        font-size: 4.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(to bottom, #FFD700, #FDB931);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-top: 30px; letter-spacing: 5px;
    }
    .royal-sub {
        text-align: center; font-family: 'Noto Serif KR', serif;
        color: #cbd5e1; font-size: 1.1rem; letter-spacing: 2px;
        margin-bottom: 50px; font-weight: 300;
    }

    /* [카드 UI - 프로스트 글래스] */
    .glass-panel {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 215, 0, 0.2); /* 금테 */
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        margin-bottom: 30px;
    }

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { background: transparent !important; gap: 10px; }
    button[data-baseweb="tab"] {
        color: #888 !important; border: none !important; font-family: 'Cinzel', serif !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFD700 !important; border-bottom: 2px solid #FFD700 !important;
        font-weight: bold !important; background: transparent !important;
    }

    /* [버튼 - 골드 그라데이션] */
    .stButton>button {
        background: linear-gradient(135deg, #FFD700 0%, #FDB931 100%) !important;
        color: #0F2027 !important;
        border: none; width: 100%; height: 70px;
        font-family: 'Cinzel', serif; font-size: 1.5rem; font-weight: 700;
        border-radius: 8px;
        box-shadow: 0 0 30px rgba(253, 185, 49, 0.4);
        transition: all 0.5s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 50px rgba(253, 185, 49, 0.7);
    }

    /* [설명 텍스트] */
    .docent-text {
        border-left: 3px solid #FFD700;
        padding-left: 20px; margin-top: 20px;
        color: #e2e8f0; line-height: 1.8; font-size: 1rem;
    }
    .docent-text b { color: #FFD700; }
</style>
""", unsafe_allow_html=True)

# --- 3. ❄️ 눈 내리는 효과 JS ---
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(10, 20)}s; animation-delay:{np.random.uniform(0, 10)}s; font-size:{np.random.uniform(0.8, 1.5)}em;">❄</div>' for _ in range(40)])
    st.markdown(snow_html, unsafe_allow_html=True)

create_snow()

# --- 4. 🎻 Grand Audio Engine (Layering & Composition) ---

def generate_wave(freq, duration, type="sine"):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), False)
    
    if type == "bell": # [멜로디] 튜블러 벨 (크리스마스 종소리)
        # 기본음 + 비화음성 배음(Inharmonicity)으로 금속성 구현
        return 0.5*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2.0*t) + 0.2*np.sin(2*np.pi*freq*5.2*t)*np.exp(-3*t)
        
    elif type == "strings": # [화음] 현악기 섹션
        # 톱니파 + 저음 보강 + 비브라토 효과
        vibrato = 1 + 0.001 * np.sin(2 * np.pi * 5 * t)
        return 0.4*np.sin(2*np.pi*freq*vibrato*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*2*t)
    
    elif type == "choir": # [코러스] 천상의 합창 (Formant 느낌)
        # 여러 개의 사인파를 미세하게 겹쳐서 '아~' 소리 흉내
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*0.998*t) + 0.3*np.sin(2*np.pi*freq*1.002*t)
        
    return np.zeros_like(t)

def apply_envelope(wave, duration, type="long"):
    total = len(wave)
    if type == "bell": # 종소리는 때리자마자 크고(Attack 0) 길게 사라짐
        env = np.exp(np.linspace(0, -3, total))
    else: # 스트링/합창은 천천히 커졌다(Attack) 천천히 사라짐
        attack = int(total * 0.3)
        release = int(total * 0.3)
        sustain = total - attack - release
        env = np.concatenate([np.linspace(0, 1, attack), np.full(sustain, 1.0), np.linspace(1, 0, release)])
    
    # 길이 보정
    if len(env) != total: env = np.resize(env, total)
    return wave * env

def apply_reverb(audio, decay=0.7, delay_ms=400):
    # [Concert Hall Reverb] 대성당 같은 울림
    delay_samples = int(44100 * (delay_ms / 1000))
    res = np.zeros(len(audio) + delay_samples)
    res[:len(audio)] += audio
    res[delay_samples:] += audio * decay
    return res

def compose_orchestra(nums, bpm):
    # D Major Scale (겨울/캐롤 느낌)
    # D(레) E(미) F#(파#) G(솔) A(라) B(시) C#(도#)
    scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    
    # [핵심] 숫자 하나를 '프레이즈(Phrase)'로 확장
    # 예: 숫자 1 -> "레-미-파#" (아르페지오) + D Major 코드
    beat_sec = 60.0 / bpm
    
    full_track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        base_freq = scale[idx % len(scale)]
        
        # 1. Melody (Bell) - 아르페지오 패턴 생성
        # 숫자에 따라 멜로디 패턴을 다르게 함
        melody_pattern = []
        if idx % 3 == 0: # 상승 패턴
            melody_pattern = [(base_freq, 0.5), (base_freq*1.25, 0.5), (base_freq*1.5, 1.0)] # 미-솔-도
        elif idx % 3 == 1: # 하강 패턴
            melody_pattern = [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 1.0)]
        else: # 도약 패턴
            melody_pattern = [(base_freq, 0.5), (base_freq*2, 1.0), (base_freq, 0.5)]

        segment_audio = []
        
        # 멜로디 합성
        for freq, dur_beat in melody_pattern:
            dur_sec = dur_beat * beat_sec
            wave = generate_wave(freq, dur_sec, "bell")
            wave = apply_envelope(wave, dur_sec, "bell")
            segment_audio.append(wave)
        
        melody_layer = np.concatenate(segment_audio)
        seg_len = len(melody_layer)
        
        # 2. Harmony (Strings) - 웅장한 배경 코드
        # 3도 아래, 5도 아래 화음을 섞음
        pad_freq = base_freq * 0.5 # 한 옥타브 아래
        pad = generate_wave(pad_freq, seg_len/44100, "strings")
        pad += generate_wave(pad_freq * 1.5, seg_len/44100, "strings") # 5도 화음
        pad = apply_envelope(pad, seg_len/44100, "long") * 0.4 # 볼륨 조절
        
        # 3. Choir (Chorus) - 천상의 코러스 (숫자가 클 때만 등장)
        choir = np.zeros_like(pad)
        if idx > 5:
            choir = generate_wave(pad_freq * 2, seg_len/44100, "choir")
            choir = apply_envelope(choir, seg_len/44100, "long") * 0.3
            
        # 레이어 합치기
        mix = melody_layer + pad + choir
        full_track.append(mix)
        
    if not full_track: return None
    
    # 전체 트랙 연결 및 리버브
    raw_audio = np.concatenate(full_track)
    final_audio = apply_reverb(raw_audio, decay=0.6, delay_ms=500)
    
    # 노멀라이즈
    m = np.max(np.abs(final_audio))
    return final_audio / m * 0.95 if m > 0 else final_audio

# --- 5. UI Layout ---

st.markdown('<div class="royal-title">ROYAL SYMPHONY</div>', unsafe_allow_html=True)
st.markdown('<div class="royal-sub">The Sound of Mathematics for Christmas</div>', unsafe_allow_html=True)

col_center = st.columns([1, 2.5, 1])[1]

with col_center:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    
    tab_pi, tab_gold, tab_root, tab_user = st.tabs(["⭕ Eternal Pi", "✨ Golden Ratio", "📐 Root Two", "💌 My Number"])
    
    with tab_pi:
        nums = "314159265358979323846264338327950288419716939937510"
        title = "원주율 (Pi, π)"
        math_desc = """
        <b>"영원히 끝나지 않는 겨울밤의 노래"</b><br>
        원주율은 원의 둘레를 지름으로 나눈 비율입니다. 소수점 아래 숫자들이 규칙 없이 무한히 이어지죠. 
        이 불규칙함이 음악으로 변하면, 마치 흩날리는 눈송이처럼 예측할 수 없는 아름다운 선율이 됩니다.
        """
    with tab_gold:
        nums = "161803398874989484820458683436563811772030917980576"
        title = "황금비 (Golden Ratio, φ)"
        math_desc = """
        <b>"신의 지문이 남긴 완벽한 화음"</b><br>
        1:1.618... 자연계에서 가장 아름답고 안정적인 비율입니다. 
        소라 껍데기의 나선, 꽃잎의 배열, 파르테논 신전까지. 
        이 비율을 음악으로 옮기면 가장 편안하고 성스러운 캐롤이 탄생합니다.
        """
    with tab_root:
        nums = "141421356237309504880168872420969807856967187537694"
        title = "루트 2 (Square Root 2)"
        math_desc = """
        <b>"최초의 비밀스러운 무리수"</b><br>
        한 변이 1인 정사각형의 대각선 길이입니다. 피타고라스 학파가 이 숫자를 발견하고 
        세상의 비밀을 풀었다고 믿었죠. 깊고 단단한 정사각형의 구조가 웅장한 오케스트라로 표현됩니다.
        """
    with tab_user:
        u_in = st.text_input(" ", placeholder="기념일이나 좋아하는 숫자를 입력하세요")
        nums = "".join(filter(str.isdigit, u_in)) if u_in else "12251225"
        title = "당신의 숫자 (Your Number)"
        math_desc = """
        <b>"당신만의 특별한 크리스마스"</b><br>
        입력하신 숫자는 이 세상에 하나뿐인 악보가 됩니다. 
        당신의 생일, 전화번호, 혹은 소중한 날짜가 어떤 캐롤로 변주되는지 들어보세요.
        """

    # 수학 도슨트 (설명)
    st.markdown(f"### {title}", unsafe_allow_html=True)
    st.markdown(f'<div class="docent-text">{math_desc}</div>', unsafe_allow_html=True)
    
    st.write("")
    st.write("")

    # 시각화 (황금빛 입자)
    if nums:
        digits = [int(d) for d in nums[:20] if d != '0']
        df = pd.DataFrame({
            'x': range(len(digits)), 'y': digits, 
            'size': [d*20+50 for d in digits],
            'color': [d for d in digits] # Altair gradient
        })
        
        c = alt.Chart(df).mark_circle().encode(
            x=alt.X('x', axis=None),
            y=alt.Y('y', axis=None, scale=alt.Scale(domain=[-2, 12])),
            size=alt.Size('size', legend=None),
            color=alt.Color('y', scale=alt.Scale(scheme='goldorange'), legend=None),
            tooltip=['y']
        ).properties(height=150, background='transparent').configure_view(strokeWidth=0)
        
        st.altair_chart(c, use_container_width=True)
    
    st.write("")
    
    # Play Button
    if st.button("🎻 PLAY ROYAL SYMPHONY"):
        with st.spinner("Conductor is ready... 🎼"):
            # BPM 85: 웅장하고 여유로운 템포
            audio = compose_orchestra(nums, bpm=85)
            
            virtual_file = io.BytesIO()
            write(virtual_file, 44100, (audio * 32767).astype(np.int16))
            st.audio(virtual_file, format='audio/wav')

    st.markdown('</div>', unsafe_allow_html=True)
