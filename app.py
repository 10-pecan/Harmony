import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Winter Academy", page_icon="🎄", layout="wide")

# --- 2. 🎨 Winter Academy Design (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Serif+KR:wght@400;700&display=swap');
    
    /* [전체 배경: 깊은 칠판색 + 가죽 질감] */
    .stApp {
        background-color: #1B262C !important;
        color: #FDF6E3 !important;
        font-family: 'Gowun Dodum', sans-serif !important;
    }

    /* [눈 효과: 아주 미세한 금가루] */
    .snowflake { position: fixed; top: -10px; z-index: 99; color: rgba(255,255,255,0.2); font-size: 0.8em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [헤더] 클래식한 타이틀 */
    .academy-header {
        text-align: center; padding: 40px 0 20px 0;
        border-bottom: 1px solid #B7950B;
        margin-bottom: 40px;
    }
    .main-title {
        font-family: 'Noto Serif KR', serif; font-size: 3.5rem; font-weight: 700;
        color: #F4D03F; letter-spacing: 2px; text-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }
    .sub-title { color: #AAB7B8; font-size: 1.1rem; margin-top: 10px; letter-spacing: 1px; }

    /* [카드 디자인: 고급스러운 양피지] */
    .paper-card {
        background-color: #FFFDF0; /* 크림색 종이 */
        border: 1px solid #D4AC0D;
        border-radius: 8px;
        padding: 30px;
        color: #2C3E50;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    /* [수학 뱃지] */
    .math-badge {
        display: inline-block; padding: 4px 12px; border-radius: 4px;
        font-size: 0.85rem; font-weight: 700; color: #fff; margin-bottom: 15px;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .bg-red { background-color: #922B21; } /* 버건디 */
    .bg-green { background-color: #196F3D; } /* 딥 그린 */
    .bg-gold { background-color: #B7950B; } /* 앤틱 골드 */
    .bg-navy { background-color: #1A5276; } /* 네이비 */

    /* [설명 텍스트] */
    .desc-text { font-family: 'Noto Serif KR', serif; line-height: 1.8; font-size: 1.05rem; color: #424949; }
    .teacher-comment {
        background-color: #EAFAF1; border-left: 4px solid #27AE60;
        padding: 15px; margin-top: 20px; color: #145A32; font-size: 0.95rem;
    }

    /* [탭 디자인] */
    button[data-baseweb="tab"] {
        color: #999 !important; font-size: 1rem; font-weight: 600;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #F4D03F !important; border-bottom: 2px solid #F4D03F !important;
    }

    /* [버튼] */
    .stButton>button {
        background-color: #145A32 !important; color: #F4D03F !important;
        border: 1px solid #F4D03F !important; border-radius: 5px; height: 55px;
        font-family: 'Noto Serif KR', serif; font-size: 1.2rem; font-weight: 700;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #196F3D !important; box-shadow: 0 0 15px rgba(244, 208, 63, 0.3); }
    
    /* [입력창] */
    .stTextInput input { border: 1px solid #B7950B; background-color: #FFF; color: #333; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(10, 25)}s; animation-delay:{np.random.uniform(0, 10)}s;">❄</div>' for _ in range(40)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (안정화됨) ---

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
        env = np.concatenate([np.linspace(0, 1, att), np.full(sus, 1.0), np.linspace(1, 0, rel)])
    env = match_len(env, length); return wave * env

def compose_music(nums, bpm, style):
    # Scale (Safe Length)
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

# --- 4. UI 렌더링 함수 (HTML 버그 완벽 차단) ---

def render_content(key, badge_cls, badge_text, title, math_latex, desc, default_nums, style, color_scheme):
    c1, c2 = st.columns([1, 1.2], gap="large")
    
    with c1:
        # 카드 시작
        st.markdown('<div class="paper-card">', unsafe_allow_html=True)
        
        # 뱃지 & 제목
        st.markdown(f'<span class="math-badge {badge_cls}">{badge_text}</span>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="color:#2C3E50; margin:5px 0 15px 0;">{title}</h2>', unsafe_allow_html=True)
        
        # 수학 수식 (LaTeX)
        if math_latex:
            st.latex(math_latex)
            
        # 설명
        st.markdown(f'<div class="desc-text">{desc}</div>', unsafe_allow_html=True)
        
        # 선생님 코멘트
        st.markdown(f"""
        <div class="teacher-comment">
            <b>🧑‍🏫 Teacher's Note:</b><br>
            이 숫자들이 음악이 될 수 있는 이유는 <b>'규칙'</b>과 <b>'변화'</b>가 있기 때문이에요.
            수학 공식이 만드는 아름다운 화음을 감상해보세요.
        </div>
        """, unsafe_allow_html=True)
        
        # 입력창 (4번째 탭용)
        final_nums = default_nums
        if key == "t4":
            st.write("")
            user_input = st.text_input("숫자를 입력하세요", value="", key=f"in_{key}")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))
            
        st.markdown('</div>', unsafe_allow_html=True) # 카드 끝

    with c2:
        st.markdown('<div class="paper-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("### 🎄 Melody Tree")
        
        if final_nums:
            # 트리 비주얼라이저
            digits = [int(d) for d in final_nums[:45] if d != '0']
            tree_data = []
            
            idx = 0; layer = 1; max_layers = 10 
            while idx < len(digits) and layer <= max_layers:
                nodes = layer
                for i in range(nodes):
                    if idx >= len(digits): break
                    note = digits[idx]
                    y = 10 - layer 
                    width = layer * 1.5
                    x = np.linspace(-width/2, width/2, nodes)[i]
                    size = note * 50 + 100
                    tree_data.append({'x': x, 'y': y, 'note': note, 'size': size})
                    idx += 1
                layer += 1
            
            df = pd.DataFrame(tree_data)
            star = pd.DataFrame({'x': [0], 'y': [10], 'note': [10], 'size': [600]})
            
            # 차트
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=1).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='#F4D03F', size=600, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=350, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)

        st.write("")
        if st.button(f"🔔 Play Music", key=f"btn_{key}"):
            with st.spinner("음악을 생성하는 중..."):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page ---
st.markdown("""
<div class="academy-header">
    <div class="main-title">Winter Math Academy</div>
    <div class="sub-title">수학의 아름다움을 음악으로 배우는 시간</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["중1: 도형", "중2: 유리수", "중3: 무리수", "자유탐구"])

with t1:
    render_content("t1", "bg-red", "도형의 성질 - 원주율(Pi)", 
        r"\pi \approx 3.141592...", 
        "원은 완벽한 대칭이지만, 그 비율인 파이(π)는 불규칙하게 끝없이 이어집니다. 이 불규칙한 숫자들이 <b>'셔플 리듬(Joyful)'</b>과 만나 썰매를 타는 듯한 신나는 캐롤이 됩니다.", 
        "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_content("t2", "bg-green", "유리수와 순환소수", 
        r"\frac{1}{7} = 0.\dot{1}4285\dot{7}", 
        "1/7은 142857이라는 여섯 자리 숫자가 계속 반복되는 순환소수입니다. 이 규칙적인 패턴은 춤추기 좋은 <b>'3박자 왈츠(Waltz)'</b>와 완벽하게 어울립니다.", 
        "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_content("t3", "bg-gold", "제곱근과 실수 - 무리수", 
        r"\sqrt{2} \approx 1.414213...", 
        "루트2는 인류가 처음 발견한 무리수입니다. 한 변이 1인 정사각형의 대각선 길이기도 하죠. 이 깊이 있는 숫자는 <b>'웅장한 합창(Holy)'</b>으로 표현됩니다.", 
        "141421356237309504880168872420969807856967187537694", "holy", "oranges")

with t4:
    render_content("t4", "bg-navy", "나만의 숫자 캐롤 만들기", 
        r"\text{My Number} \rightarrow \text{Music}", 
        "여러분의 생일이나 기념일을 입력해보세요. 1225(크리스마스)도 좋습니다. 여러분만의 숫자가 <b>세상에 하나뿐인 캐롤</b>로 변환됩니다.", 
        "12251225", "joyful", "purples")

st.markdown("<br><div style='text-align:center; color:#AAB7B8;'>Designed for Educational Purpose • 2025 Winter</div>", unsafe_allow_html=True)
