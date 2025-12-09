import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol: Black Label", page_icon="🎄", layout="wide")

# --- 2. 🎨 Modern Luxury Design (CSS) ---
st.markdown("""
<style>
    /* [Font] Apple/Toss 스타일의 현대적인 고딕 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* [Global Theme] Deep Matte Black */
    .stApp {
        background-color: #050505 !important;
        font-family: 'Pretendard', -apple-system, system-ui, sans-serif !important;
        color: #FFFFFF !important;
    }

    /* [Snow Effect] 아주 작고 느린 미세 먼지 같은 눈 */
    .snowflake { 
        position: fixed; top: -10px; z-index: 0; 
        color: rgba(255, 255, 255, 0.3); 
        font-size: 0.5rem; /* 아주 작게 */
        animation: fall linear infinite; 
    }
    @keyframes fall { 
        0% { transform: translateY(-10vh); opacity: 0; } 
        20% { opacity: 0.8; }
        100% { transform: translateY(110vh); opacity: 0; } 
    }

    /* [Header] Minimal Typography */
    .hero-container {
        padding: 60px 0 40px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 40px;
    }
    .hero-title {
        font-size: 3.5rem; font-weight: 800; letter-spacing: -1px;
        background: linear-gradient(90deg, #FFFFFF, #888888);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .hero-sub {
        font-size: 1rem; color: #666; font-weight: 500; letter-spacing: 2px; text-transform: uppercase;
    }

    /* [Card] Dark Glassmorphism */
    .glass-card {
        background: rgba(20, 20, 20, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08); /* 초박형 테두리 */
        border-radius: 20px; padding: 40px;
        margin-bottom: 24px;
        backdrop-filter: blur(20px);
    }

    /* [Text Fix] 가독성 강제 확보 */
    h1, h2, h3, h4, strong { color: #FFFFFF !important; }
    p, li, span, div { color: #CCCCCC; } /* 본문은 연한 회색 */
    .desc-box { 
        margin-top: 20px; padding-top: 20px; 
        border-top: 1px solid rgba(255,255,255,0.1); 
        font-size: 0.95rem; line-height: 1.7; color: #999;
    }
    .desc-box b { color: #fff; font-weight: 600; }

    /* [Badge] Pill Shape */
    .badge {
        display: inline-block; padding: 6px 12px; border-radius: 100px;
        font-size: 0.75rem; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.05); color: #fff;
    }

    /* [Tabs] Segmented Control Style */
    div[data-baseweb="tab-list"] { background: transparent !important; gap: 20px; border-bottom: 1px solid #222; }
    button[data-baseweb="tab"] {
        background: transparent !important; border: none !important; color: #555 !important;
        font-weight: 600; font-size: 1rem; padding-bottom: 15px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFF !important; border-bottom: 2px solid #FFF !important;
    }

    /* [Button] Minimal & Solid */
    .stButton>button {
        background-color: #FFFFFF !important; color: #000000 !important;
        border: none; border-radius: 12px; height: 56px; font-weight: 700; font-size: 1rem;
        transition: all 0.2s ease; width: 100%;
    }
    .stButton>button:hover {
        background-color: #E0E0E0 !important; transform: scale(1.01);
    }

    /* [Input] Dark Input */
    .stTextInput input {
        background-color: #111 !important; border: 1px solid #333 !important; color: #fff !important;
        border-radius: 12px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 눈 효과 (미세하게)
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(10, 30)}s; animation-delay:{np.random.uniform(0, 10)}s;">.</div>' for _ in range(60)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (안정성 최우선) ---

def generate_wave(freq, duration, type="bell"):
    sr = 44100; num_samples = int(sr * duration); t = np.linspace(0, duration, num_samples, False)
    if type == "bell": return 0.6*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)*np.exp(-2*t) + 0.1*np.sin(2*np.pi*freq*4*t)
    elif type == "strings": return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*0.5*t)
    elif type == "choir": return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*0.998*t)
    elif type == "sleigh": noise = np.random.uniform(-1, 1, len(t)); return 0.1 * noise * np.sin(2*np.pi*3000*t) * np.exp(-15*t)
    return np.zeros(num_samples)

def match_len(wave, length):
    if len(wave) == length: return wave
    elif len(wave) > length: return wave[:length]
    else: return np.pad(wave, (0, length - len(wave)), 'constant')

def apply_envelope(wave, duration, type="short"):
    length = len(wave)
    if type == "short": env = np.exp(np.linspace(0, -5, length))
    else:
        att = int(length*0.2); rel = int(length*0.3); sus = length - att - rel
        if sus < 0: sus = 0
        env = np.concatenate([np.linspace(0,1,att), np.full(sus,1.0), np.linspace(1,0,rel)])
    env = match_len(env, length); return wave * env

def compose_music(nums, bpm, style):
    # Scale: C Major / D Major / A Minor
    if style == "joyful": scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    elif style == "waltz": scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    else: scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    
    beat_sec = 60.0 / bpm; full_track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit); base_freq = scale[idx % len(scale)]
        
        notes = []
        if style == "joyful": 
            if idx % 2 == 0: notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)]
            else: notes = [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        elif style == "waltz": notes = [(base_freq, 1.0), (base_freq*1.25, 1.0), (base_freq*1.5, 1.0)]
        else: notes = [(base_freq, 4.0)]
            
        melody_waves = []
        for f, d in notes:
            dur = d * beat_sec
            w = generate_wave(f, dur, "bell" if style != "holy" else "choir")
            w = apply_envelope(w, dur, "short" if style != "holy" else "long")
            melody_waves.append(w)
        melody = np.concatenate(melody_waves); total_len = len(melody)
        
        pad = generate_wave(base_freq * 0.5, total_len/44100, "strings"); pad = match_len(pad, total_len)
        pad = apply_envelope(pad, total_len/44100, "long") * 0.3
        
        sleigh = generate_wave(0, total_len/44100, "sleigh"); sleigh = match_len(sleigh, total_len) * 0.3 if style == "joyful" else np.zeros(total_len)
        
        full_track.append(melody + pad + sleigh)
        
    if not full_track: return None
    full = np.concatenate(full_track); delay = int(44100 * 0.4); res = np.zeros(len(full) + delay); res[:len(full)] += full; res[delay:] += full * 0.4
    m = np.max(np.abs(res)); return res / m * 0.95 if m > 0 else res

# --- 4. UI Rendering ---

def render_tab_content(key, badge_text, title, desc, default_nums, style):
    c1, c2 = st.columns([1, 1.2], gap="large")
    
    # [Left: Controller & Info]
    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <span class="badge">{badge_text}</span>
            <h2 style="margin-bottom: 10px;">{title}</h2>
            <div class="desc-box">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        
        # 4번째 탭의 경우 입력창 활성화
        if key == "t4":
            st.markdown('<div class="glass-card" style="padding:20px;">', unsafe_allow_html=True)
            col_in1, col_in2 = st.columns([2, 1])
            with col_in1:
                user_input = st.text_input("Number Input", value="", placeholder="12251225", label_visibility="collapsed", key=f"in_{key}")
                if user_input: final_nums = "".join(filter(str.isdigit, user_input))
            with col_in2:
                # 스타일 선택 라디오
                sel_style = st.selectbox("Style", ["Joyful", "Waltz", "Holy"], key=f"sel_{key}", label_visibility="collapsed")
                if sel_style: style = sel_style.lower()
            st.markdown('</div>', unsafe_allow_html=True)

    # [Right: Visualizer]
    with c2:
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        
        if final_nums:
            # [Visual] 미디어 아트 스타일 트리 (Golden Dots)
            digits = [int(d) for d in final_nums[:45] if d != '0']
            tree_data = []
            
            idx = 0; layer = 1; max_layers = 10
            while idx < len(digits) and layer <= max_layers:
                nodes = layer
                for i in range(nodes):
                    if idx >= len(digits): break
                    # 좌표 계산
                    width = layer * 1.5
                    x = np.linspace(-width/2, width/2, nodes)[i]
                    y = 10 - layer # 위에서 아래로
                    
                    # 데이터 추가
                    tree_data.append({
                        'x': x, 'y': y, 'note': digits[idx], 
                        'size': digits[idx]*30 + 50, # 크기 변동
                        'opacity': digits[idx]/10 + 0.1
                    })
                    idx += 1
                layer += 1
                
            df = pd.DataFrame(tree_data)
            star = pd.DataFrame({'x': [0], 'y': [10], 'note': [10], 'size': [400], 'opacity': [1]})
            
            # 차트: 샴페인 골드 & 화이트 컬러
            colors = {'joyful': ['#FF4B4B', '#FFD700'], 'waltz': ['#2ECC71', '#F1C40F'], 'holy': ['#3498DB', '#FFFFFF']}
            curr_colors = colors.get(style, ['#FFFFFF', '#FFD700'])
            
            base = alt.Chart(df).mark_circle(stroke='white', strokeWidth=1).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(range=curr_colors), legend=None),
                opacity=alt.Opacity('opacity', legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='#FFF', size=400, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=350, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)

        st.write("")
        # 재생 버튼
        if st.button(f"PLAY AUDIO", key=f"btn_{key}"):
            with st.spinner("Rendering Audio..."):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Layout ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">MATH CAROL</div>
    <div class="hero-sub">2025 WINTER COLLECTION • EDUCATIONAL EDITION</div>
</div>
""", unsafe_allow_html=True)

# 탭 구성
t1, t2, t3, t4 = st.tabs(["GRADE 1", "GRADE 2", "GRADE 3", "FREE PLAY"])

with t1:
    render_tab_content("t1", "중1 도형", "Circular Pi (π)", 
        """
        <b>원주율(π)의 불규칙한 아름다움</b><br>
        원은 완벽한 대칭을 이루지만, 그 비율인 파이(3.141592...)는 끝없이 불규칙합니다. 
        이 예측 불가능한 숫자의 배열을 <b>경쾌한 셔플 리듬(Joyful)</b>으로 해석했습니다.
        """, "314159265358979323846264338327950288419716939937510", "joyful")

with t2:
    render_tab_content("t2", "중2 유리수", "Decimal Waltz", 
        """
        <b>순환소수의 규칙적인 춤</b><br>
        1/7 = 0.142857... 처럼 일정한 구간이 반복되는 순환소수는 수학적인 안정감을 줍니다.
        이 규칙성을 <b>우아한 3박자 왈츠(Waltz)</b> 리듬에 담았습니다.
        """, "142857142857142857142857142857142857142857", "waltz")

with t3:
    render_tab_content("t3", "중3 제곱근", "Square Root Harmony", 
        """
        <b>무리수의 깊은 울림</b><br>
        정사각형의 대각선 길이인 루트2(1.414...)는 인류가 처음 발견한 무리수입니다.
        비순환 무한소수의 깊이감을 <b>성스러운 합창(Holy)</b> 사운드로 표현했습니다.
        """, "141421356237309504880168872420969807856967187537694", "holy")

with t4:
    render_tab_content("t4", "자유 탐구", "Create Your Carol", 
        """
        <b>나만의 숫자로 만드는 음악</b><br>
        생일, 기념일 등 소중한 숫자를 입력해보세요. 
        수학적 알고리즘이 당신만을 위한 유일한 캐롤을 작곡해 드립니다.
        """, "12251225", "joyful")

st.markdown("<br><br><div style='text-align:center; color:#444; font-size:0.8rem;'>Designed by AI • 2025 Education Tech</div>", unsafe_allow_html=True)
