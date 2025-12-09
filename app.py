import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Snow Globe Symphony", page_icon="❄️", layout="wide")

# --- 2. 🎨 High-End Design (Glassmorphism & Snow) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,600&family=Outfit:wght@200;400;600&display=swap');
    
    /* [배경] 깊은 겨울 밤하늘 (Deep Midnight) */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1B2735 0%, #090A0F 100%) !important;
        color: #E2E8F0 !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* [눈 내리는 효과 - 부드럽고 느리게] */
    .snowflake {
        position: fixed; top: -10px; z-index: 0;
        color: white; opacity: 0.8;
        font-size: 1em;
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { transform: translateY(-10vh) translateX(0px); opacity: 0; }
        20% { opacity: 0.8; }
        100% { transform: translateY(110vh) translateX(20px); opacity: 0.3; }
    }

    /* [타이포그래피] 고급스러운 세리프 폰트 */
    .hero-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 5rem;
        font-weight: 600;
        font-style: italic;
        text-align: center;
        background: linear-gradient(to bottom, #FFFFFF, #94A3B8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 40px;
        letter-spacing: -2px;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.2);
    }
    .hero-sub {
        text-align: center;
        font-family: 'Outfit', sans-serif;
        color: #64748B;
        font-size: 1rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 60px;
    }

    /* [유리 카드 UI (Glassmorphism)] */
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    }

    /* [탭 디자인 - 미니멀] */
    div[data-baseweb="tab-list"] { background: transparent !important; gap: 20px; }
    button[data-baseweb="tab"] {
        background: transparent !important; border: none !important; color: #64748B !important;
        font-family: 'Outfit', sans-serif !important; font-weight: 400 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF !important; font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.5);
    }

    /* [입력창 & 버튼] */
    .stTextInput input {
        background: rgba(0,0,0,0.3) !important;
        border: 1px solid #334155 !important;
        color: white !important;
        text-align: center; letter-spacing: 2px;
    }
    .play-btn-container button {
        background: linear-gradient(135deg, #E2E8F0 0%, #94A3B8 100%) !important;
        color: #0f172a !important;
        border: none;
        width: 100%; height: 70px;
        border-radius: 16px;
        font-size: 1.2rem; font-weight: 600; letter-spacing: 1px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .play-btn-container button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
    }

    /* [설명 텍스트] */
    .poetic-desc {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.4rem; color: #CBD5E1; line-height: 1.6;
        text-align: center; margin-top: 20px; font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ❄️ 눈 내리는 효과 JS/HTML ---
def snow_effect():
    snows = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(8, 15)}s; animation-delay:{np.random.uniform(0, 5)}s; font-size:{np.random.uniform(0.5, 1.5)}em;">.</div>' for _ in range(30)])
    st.markdown(snows, unsafe_allow_html=True)

snow_effect()

# --- 4. 🎻 Rich Audio Engine (Layering) ---

def get_wave(freq, duration, type="sine"):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), False)
    if type == "celesta": # 영롱한 벨 소리
        # 기본음 + 배음(Overtones)을 섞어 금속성 소리 구현
        return 0.6*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t) + 0.1*np.sin(2*np.pi*freq*3.5*t)
    elif type == "strings": # 따뜻한 현악기 패드
        # 톱니파를 부드럽게 필터링한 느낌 (Detuned Saw)
        return 0.4*np.sin(2*np.pi*freq*t) + 0.4*np.sin(2*np.pi*(freq*1.01)*t) 
    return np.zeros_like(t)

def apply_envelope(wave, duration, attack=0.1, release=0.5):
    total = len(wave)
    att_len = int(total * attack)
    rel_len = int(total * release)
    sus_len = total - att_len - rel_len
    if sus_len < 0: sus_len = 0
    
    env = np.concatenate([
        np.linspace(0, 1, att_len),
        np.full(sus_len, 1.0),
        np.linspace(1, 0, rel_len)
    ])
    # 길이 보정
    if len(env) != total: env = np.resize(env, total)
    return wave * env

def apply_reverb(audio, decay=0.6, delay=4000):
    # [공간감] 성당이나 동굴에 있는 듯한 울림 추가
    res = np.zeros(len(audio) + delay)
    res[:len(audio)] += audio
    res[delay:] += audio * decay
    return res

def compose_rich_carol(nums, bpm):
    # D Major Scale (겨울 느낌의 조성)
    # D(레) E(미) F#(파#) G(솔) A(라) B(시) C#(도#) D(레)
    scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    
    # 숫자별 화음 매핑 (Chord Mapping)
    # 1을 누르면 단순히 '레'가 아니라 'D Major 코드'가 깔림
    chords = {
        '1': [0, 2, 4], '2': [1, 3, 5], '3': [2, 4, 6], '4': [3, 5, 7],
        '5': [4, 6, 8], '6': [5, 7, 9], '7': [6, 8, 1], '8': [7, 9, 2],
        '9': [0, 4, 7], '0': []
    }
    
    sec_per_beat = 60.0 / bpm
    full_track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        
        # 1. Melody (Celesta) - 영롱하게
        freq = scale[idx] if idx < len(scale) else scale[0]
        if idx == 0: # 쉼표
            melody = np.zeros(int(44100 * sec_per_beat))
        else:
            melody = get_wave(freq, sec_per_beat, "celesta")
            melody = apply_envelope(melody, sec_per_beat, 0.01, 0.8) # 띵~ 하고 여운
            
        # 2. Background Pad (Strings) - 웅장하게
        pad = np.zeros_like(melody)
        if str(idx) in chords:
            chord_indices = chords[str(idx)]
            for ci in chord_indices:
                # 한 옥타브 낮춰서 깔아줌
                pad_note = get_wave(scale[ci % len(scale)] * 0.5, sec_per_beat, "strings")
                pad += pad_note
            pad = apply_envelope(pad, sec_per_beat, 0.3, 0.3) * 0.4 # 은은하게
            
        # 믹싱
        mix = melody + pad
        full_track.append(mix)
        
    if not full_track: return None
    
    # 트랙 합치기 및 리버브 적용
    raw_audio = np.concatenate(full_track)
    final_audio = apply_reverb(raw_audio)
    
    # 노멀라이즈 (소리 깨짐 방지)
    m = np.max(np.abs(final_audio))
    return final_audio / m * 0.9 if m > 0 else final_audio

# --- 5. UI Layout ---

st.markdown('<div class="hero-title">Winter Math Symphony</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">The Sound of Serendipity</div>', unsafe_allow_html=True)

col_center = st.columns([1, 2, 1])[1] # 중앙 정렬

with col_center:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    
    # 탭
    tab_pi, tab_gold, tab_user = st.tabs(["Eternal Pi (π)", "Golden Ratio (φ)", "My Story"])
    
    with tab_pi:
        target_nums = "314159265358979323846264338327950288419716939937510"
        desc = "끝없이 이어지는 원주율처럼, 우리의 겨울도 영원히 따뜻하기를."
    with tab_gold:
        target_nums = "161803398874989484820458683436563811772030917980576"
        desc = "자연이 빚어낸 가장 완벽한 비율, 황금비가 들려주는 평온한 선율."
    with tab_user:
        u_in = st.text_input(" ", placeholder="Enter your special numbers...")
        target_nums = "".join(filter(str.isdigit, u_in)) if u_in else "12251225"
        desc = "당신의 숫자가 음악이 되어 눈처럼 내려옵니다."

    # 시각화 (Altair Star Chart - 은하수 느낌)
    if target_nums:
        digits = [int(d) for d in target_nums[:30] if d != '0']
        df = pd.DataFrame({
            'x': range(len(digits)), 
            'y': digits, 
            'size': np.random.randint(50, 200, len(digits)),
            'alpha': np.random.uniform(0.3, 0.9, len(digits))
        })
        
        # 별자리 차트
        chart = alt.Chart(df).mark_circle(color='white').encode(
            x=alt.X('x', axis=None),
            y=alt.Y('y', axis=None, scale=alt.Scale(domain=[-2, 12])),
            size=alt.Size('size', legend=None),
            opacity=alt.Opacity('alpha', legend=None),
            tooltip=['y']
        ).properties(height=180, background='transparent').configure_view(strokeWidth=0)
        
        st.altair_chart(chart, use_container_width=True)
    
    st.markdown(f'<div class="poetic-desc">"{desc}"</div>', unsafe_allow_html=True)
    st.write("")
    
    # 재생 버튼
    st.markdown('<div class="play-btn-container">', unsafe_allow_html=True)
    if st.button("❄️ Play Winter Symphony"):
        with st.spinner("Compiling the sounds of winter..."):
            audio = compose_rich_carol(target_nums, bpm=90) # 느리고 감성적인 BPM
            
            virtual_file = io.BytesIO()
            write(virtual_file, 44100, (audio * 32767).astype(np.int16))
            st.audio(virtual_file, format='audio/wav')
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) # End Glass Panel
