import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol 2025", page_icon="🎄", layout="wide")

# --- 2. 🎨 2025 Neo-Glass Design (CSS) ---
st.markdown("""
<style>
    /* [폰트] 현대적인 고딕 (Pretendard) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* [전체 테마 강제 적용 - 다크 모드] */
    .stApp {
        background-color: #050505 !important;
        color: #FFFFFF !important;
        font-family: 'Pretendard', sans-serif !important;
    }
    
    /* 모든 텍스트 강제 화이트 (가독성 해결) */
    h1, h2, h3, h4, p, span, div, label {
        color: #E0E0E0 !important;
    }

    /* [눈 내리는 효과 - 심플하고 모던하게] */
    .snowflake { position: fixed; top: -10px; z-index: 0; color: rgba(255,255,255,0.3); font-size: 1em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [헤더 디자인 - 네온 글로우] */
    .neo-header {
        text-align: center; margin-bottom: 50px; padding-top: 20px;
    }
    .neo-title {
        font-size: 4rem; font-weight: 800; letter-spacing: -2px;
        background: linear-gradient(to right, #fff, #999);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(255,255,255,0.2);
    }
    .neo-sub {
        font-size: 1.1rem; color: #666 !important; font-weight: 500; letter-spacing: 2px; text-transform: uppercase;
    }

    /* [컨텐츠 카드 - 글래스모피즘] */
    .glass-box {
        background: rgba(20, 20, 20, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .glass-box:hover {
        border-color: rgba(255, 255, 255, 0.2);
    }

    /* [탭 디자인 - 아이폰 스타일 세그먼트 컨트롤] */
    div[data-baseweb="tab-list"] {
        background-color: rgba(255,255,255,0.05);
        padding: 5px; border-radius: 15px; display: inline-flex; justify-content: center; width: 100%;
    }
    button[data-baseweb="tab"] {
        background-color: transparent !important; border: none !important; color: #888 !important; border-radius: 10px !important; flex: 1;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #333 !important; color: #fff !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* [재생 버튼 - 네온 엑센트] */
    .stButton>button {
        background: #FFFFFF !important; color: #000 !important; border: none; height: 60px;
        font-size: 1.1rem; font-weight: 800; border-radius: 12px; width: 100%;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background: #00FF88 !important; /* 네온 그린 호버 */
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.4); transform: scale(1.01);
    }

    /* [입력창] */
    .stTextInput input {
        background-color: #111 !important; border: 1px solid #333 !important; color: #fff !important;
        text-align: center; font-size: 1.2rem; letter-spacing: 3px; border-radius: 12px;
    }

    /* [교육용 뱃지] */
    .tag {
        display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;
        margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# 눈 효과 JS
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(10, 20)}s; animation-delay:{np.random.uniform(0, 10)}s;">.</div>' for _ in range(50)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (에러 원천 봉쇄) ---

def generate_wave(freq, duration, type="bell"):
    sr = 44100
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if type == "bell": 
        return 0.6*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)*np.exp(-2*t) + 0.1*np.sin(2*np.pi*freq*4*t)
    elif type == "strings":
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*0.5*t)
    elif type == "choir":
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*0.998*t)
    elif type == "sleigh":
        noise = np.random.uniform(-1, 1, len(t))
        return 0.1 * noise * np.sin(2*np.pi*3000*t) * np.exp(-10*t)
    return np.zeros(num_samples)

# [FIX] 길이 강제 맞춤 함수 (Numpy Array Broadcasting Error 해결)
def match_len(wave, length):
    if len(wave) == length: return wave
    elif len(wave) > length: return wave[:length]
    else: return np.pad(wave, (0, length - len(wave)), 'constant')

def apply_envelope(wave, duration, type="short"):
    length = len(wave)
    if type == "short": 
        env = np.exp(np.linspace(0, -5, length))
    else:
        # 안전한 Envelope 생성
        att = int(length * 0.2)
        rel = int(length * 0.3)
        sus = length - att - rel
        if sus < 0: sus = 0
        env = np.concatenate([np.linspace(0, 1, att), np.full(sus, 1.0), np.linspace(1, 0, rel)])
    
    # Envelope 길이도 Wave와 강제 동기화
    env = match_len(env, length)
    return wave * env

def compose_music(nums, bpm, style):
    # 안전한 스케일 (모든 숫자에 대응)
    scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    beat_sec = 60.0 / bpm
    full_track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        base_freq = scale[idx % len(scale)]
        
        # 멜로디 생성
        notes = []
        if style == "joyful": # 셔플
            if idx % 2 == 0: notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)]
            else: notes = [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        elif style == "waltz": # 3박자
            notes = [(base_freq, 1.0), (base_freq*1.25, 1.0), (base_freq*1.5, 1.0)]
        else: # 롱노트
            notes = [(base_freq, 4.0)]
            
        melody_waves = []
        for f, d in notes:
            dur = d * beat_sec
            inst = "bell" if style != "holy" else "choir"
            env = "short" if style != "holy" else "long"
            w = generate_wave(f, dur, inst)
            w = apply_envelope(w, dur, env)
            melody_waves.append(w)
            
        melody = np.concatenate(melody_waves)
        total_len = len(melody)
        
        # 반주 추가 (길이 강제 보정 적용)
        pad = generate_wave(base_freq * 0.5, total_len/44100, "strings")
        pad = match_len(pad, total_len) # 핵심 Fix
        pad = apply_envelope(pad, total_len/44100, "long") * 0.3
        
        sleigh = np.zeros(total_len)
        if style == "joyful":
            sleigh = generate_wave(0, total_len/44100, "sleigh")
            sleigh = match_len(sleigh, total_len) * 0.3
            
        full_track.append(melody + pad + sleigh)
        
    if not full_track: return None
    full = np.concatenate(full_track)
    
    # 리버브 & 노멀라이즈
    delay = int(44100 * 0.4)
    res = np.zeros(len(full) + delay)
    res[:len(full)] += full
    res[delay:] += full * 0.4
    
    m = np.max(np.abs(res))
    return res / m * 0.95 if m > 0 else res

# --- 4. UI Layout & Logic ---

st.markdown("""
<div class="neo-header">
    <div class="neo-title">MATH CAROL</div>
    <div class="neo-sub">2025 WINTER COLLECTION</div>
</div>
""", unsafe_allow_html=True)

# 탭 (독립적 작동을 위해 함수화)
t1, t2, t3, t4 = st.tabs(["중1 도형", "중2 순환소수", "중3 무리수", "My Carol"])

def render_section(key_id, tag_text, title, desc, default_nums, style):
    c1, c2 = st.columns([1, 1], gap="large")
    
    with c1:
        st.markdown(f"""
        <div class="glass-box" style="height:100%">
            <span class="tag" style="background:rgba(255,255,255,0.1); color:#aaa;">{tag_text}</span>
            <h2 style="margin: 15px 0; color:#fff;">{title}</h2>
            <div style="color:#bbb; line-height:1.6; font-size:1rem;">{desc}</div>
            <br>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        if key_id == "t4":
            user_in = st.text_input("숫자를 입력하세요", value="", placeholder="12251225", key=f"input_{key_id}")
            if user_in: final_nums = "".join(filter(str.isdigit, user_in))
        
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-box">', unsafe_allow_html=True)
        
        # [NEW] 진짜 트리 모양 좌표 계산 (Coordinate Tree)
        if final_nums:
            digits = [int(d) for d in final_nums[:28] if d != '0']
            tree_data = []
            
            # 트리 구조 생성 (1 -> 2 -> 3 -> 4 ...)
            # 층(Layer)마다 노드 개수를 늘려서 삼각형 모양 생성
            layer = 1
            idx = 0
            while idx < len(digits):
                nodes_in_layer = layer # 1층엔 1개, 2층엔 2개...
                for i in range(nodes_in_layer):
                    if idx >= len(digits): break
                    
                    # X 좌표: 중앙(0)을 기준으로 좌우 대칭 배치
                    x_pos = (i - (nodes_in_layer - 1) / 2) * 1.5
                    # Y 좌표: 위에서 아래로
                    y_pos = -layer * 2
                    
                    d = digits[idx]
                    # 색상: 숫자에 따라 다르게 (Altair Color Scheme)
                    # 크기: 숫자가 클수록 큼
                    tree_data.append({'x': x_pos, 'y': y_pos, 'note': d, 'size': d*50 + 100})
                    idx += 1
                layer += 1
                
            df = pd.DataFrame(tree_data)
            
            # Altair 차트
            # 테마 색상 지정
            colors = {'joyful': 'reds', 'waltz': 'greens', 'holy': 'oranges'}
            
            # 트리 꼭대기 별
            star = pd.DataFrame({'x': [0], 'y': [0], 'note': [10], 'size': [500]})
            
            # 차트 그리기
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=1).encode(
                x=alt.X('x', axis=None),
                y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=colors[style]), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='yellow', size=500).encode(
                x='x', y='y'
            )
            
            final_chart = (base + top).properties(height=350, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)
            st.caption("▲ 숫자들이 쌓여 만들어진 멜로디 트리")

        # 재생 버튼
        if st.button(f"Play Music", key=f"btn_{key_id}"):
            with st.spinner("Processing..."):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
        st.markdown('</div>', unsafe_allow_html=True)

# 탭 내용 렌더링
with t1:
    render_section("t1", "중1 도형", "Pi (π) Jingle", 
                   "<b>3.141592...</b><br>원주율의 불규칙함이 만드는 즐거운 셔플 리듬 캐롤입니다.", 
                   "314159265358979323846264338327950288419716939937510", "joyful")
with t2:
    render_section("t2", "중2 유리수", "Recurring Decimal Waltz", 
                   "<b>0.142857...</b><br>순환소수(1/7)의 반복되는 패턴이 우아한 왈츠가 됩니다.", 
                   "142857142857142857142857142857142857142857", "waltz")
with t3:
    render_section("t3", "중3 무리수", "Root 2 Holy Night", 
                   "<b>1.414213...</b><br>무리수 루트2의 깊이감을 웅장한 합창으로 표현했습니다.", 
                   "141421356237309504880168872420969807856967187537694", "holy")
with t4:
    render_section("t4", "자유 탐구", "Custom Carol", 
                   "나만의 숫자를 입력해 세상에 하나뿐인 캐롤을 만들어보세요.", 
                   "12251225", "joyful")

st.markdown("<br><div style='text-align:center; color:#555; font-size:0.8rem;'>Designed by AI • 2025 Edition</div>", unsafe_allow_html=True)
