import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Magic Math Carol", page_icon="🧙‍♂️", layout="wide")

# --- 2. 🎨 Hogwarts Christmas Design (CSS) ---
st.markdown("""
<style>
    /* [폰트] 마법학교 느낌의 세리프 폰트 */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Nanum+Myeongjo:wght@400;700;800&display=swap');
    
    /* [전체 배경: 깊은 마법사의 밤하늘] */
    .stApp {
        background-color: #0c0c0c !important;
        background-image: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #000000 100%);
        color: #dcdcdc !important;
        font-family: 'Nanum Myeongjo', serif !important;
    }

    /* [눈 효과: 마법 가루] */
    .snowflake { 
        position: fixed; top: -10px; z-index: 99; 
        color: #ffd700; opacity: 0.6; font-size: 0.8em; 
        text-shadow: 0 0 5px #ffd700;
        animation: fall linear infinite; 
    }
    @keyframes fall { 
        0% { transform: translateY(-10vh) rotate(0deg); opacity: 0; } 
        20% { opacity: 0.8; }
        100% { transform: translateY(110vh) rotate(360deg); opacity: 0; } 
    }

    /* [헤더: 영화 타이틀 느낌] */
    .magic-header {
        text-align: center; padding: 40px 0;
        border-bottom: 2px solid #7f8c8d;
        margin-bottom: 40px;
        background: linear-gradient(to bottom, rgba(0,0,0,0), rgba(20,20,20,0.8));
    }
    .main-title {
        font-family: 'Cinzel', serif; font-size: 4.5rem; color: #d4af37; /* 앤틱 골드 */
        text-shadow: 0 0 10px #d4af37, 0 0 20px #000; margin: 0;
        letter-spacing: 5px;
    }
    .sub-title {
        font-size: 1.2rem; color: #bdc3c7; margin-top: 15px; 
        letter-spacing: 2px; font-style: italic;
    }

    /* [카드: 오래된 양피지 스타일] */
    .parchment-card {
        background-color: #f3e5ab; /* 양피지 색 */
        background-image: url("https://www.transparenttextures.com/patterns/aged-paper.png");
        border: 8px double #5a3a22; /* 갈색 테두리 */
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.8), inset 0 0 30px rgba(90, 58, 34, 0.2);
        color: #3e2723; /* 잉크색 */
        margin-bottom: 25px;
        position: relative;
    }
    /* 카드 모서리 장식 */
    .parchment-card::after {
        content: "✦"; position: absolute; top: 10px; right: 15px; font-size: 2rem; color: #8b0000;
    }

    /* [교수님 노트: 마법 주문서 느낌] */
    .professor-note {
        background-color: rgba(255, 255, 255, 0.5);
        border-left: 4px solid #740001; /* 그리핀도르 레드 */
        padding: 15px; margin-top: 20px;
        font-size: 1.05rem; line-height: 1.8;
        font-weight: 600; color: #2c0a0a;
    }
    .note-label { color: #740001; font-weight: 900; font-family: 'Cinzel', serif; display: block; margin-bottom: 5px; }

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { gap: 15px; justify-content: center; border-bottom: 1px solid #444; padding-bottom: 10px;}
    button[data-baseweb="tab"] {
        background-color: transparent !important; color: #888 !important; 
        font-family: 'Cinzel', serif !important; font-size: 1.1rem !important; border: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #d4af37 !important; border-bottom: 3px solid #d4af37 !important; font-weight: bold !important;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
    }

    /* [버튼: 마법 주문 버튼] */
    .stButton>button {
        background: linear-gradient(to bottom, #740001, #500000) !important;
        color: #d4af37 !important; border: 2px solid #d4af37 !important;
        border-radius: 5px; height: 65px; font-size: 1.4rem; font-family: 'Cinzel', serif; font-weight: 700; width: 100%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5); transition: all 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px #d4af37; text-shadow: 0 0 10px #fff; }

    /* [입력창] */
    .stTextInput input {
        background-color: rgba(255,255,255,0.1) !important; color: #fff !important; 
        border: 1px solid #d4af37 !important; text-align: center; font-size: 1.3rem; letter-spacing: 3px;
    }
    
    /* [뱃지] */
    .house-badge {
        display: inline-block; padding: 5px 12px; border-radius: 4px; font-size: 0.9rem; font-weight: bold; color: #fff; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;
    }
    .h-gry { background: #740001; border: 1px solid #d3a625; }
    .h-sly { background: #1a472a; border: 1px solid #aaaaaa; }
    .h-rav { background: #0e1a40; border: 1px solid #946b2d; }
    .h-huf { background: #ecb939; color: #000; border: 1px solid #000; }
</style>
""", unsafe_allow_html=True)

# 마법 가루(눈) 효과
def create_magic_dust():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(5, 12)}s; animation-delay:{np.random.uniform(0, 5)}s;">✨</div>' for _ in range(30)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_magic_dust()

# --- 3. 🎹 Magical Audio Engine ---

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
        att = int(length*0.2); rel = int(length*0.3); sus = length - att - rel; 
        if sus < 0: sus = 0
        env = np.concatenate([np.linspace(0, 1, att), np.full(sus, 1.0), np.linspace(1, 0, rel)])
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

# --- 4. UI 렌더링 함수 (HTML 버그 수정됨) ---

def render_magic_tab(key_prefix, badge_cls, badge_text, title, subtitle, math_note, default_nums, style, color_scheme):
    c1, c2 = st.columns([1, 1.1], gap="large")
    
    with c1:
        # [HTML] 양피지 카드 컨테이너 (div 태그 노출 오류 해결)
        html_content = f"""
        <div class="parchment-card">
            <span class="house-badge {badge_cls}">{badge_text}</span>
            <h2 style="font-family:'Cinzel',serif; color:#740001; margin-top:0;">{title}</h2>
            <div style="font-weight:bold; color:#5a3a22; margin-bottom:15px;">{subtitle}</div>
            
            <div class="professor-note">
                <span class="note-label">📜 Professor's Note</span>
                {math_note}
            </div>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
        
        final_nums = default_nums
        if key_prefix == "t4":
            st.write("")
            user_input = st.text_input("당신의 숫자를 입력하세요", value="", placeholder="12251225", key=f"in_{key_prefix}")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))

    with c2:
        # [Visualizer] 떠있는 마법 트리
        st.markdown('<div class="parchment-card" style="text-align:center; padding-bottom:10px;">', unsafe_allow_html=True)
        
        if final_nums:
            digits = [int(d) for d in final_nums[:45] if d != '0']
            tree_data = []
            
            current_idx = 0; layer = 1; max_layers = 10 
            while current_idx < len(digits) and layer <= max_layers:
                nodes_in_layer = layer
                for i in range(nodes_in_layer):
                    if current_idx >= len(digits): break
                    note = digits[current_idx]
                    y_pos = 10 - layer 
                    width_spread = layer * 1.5
                    x_pos = np.linspace(-width_spread/2, width_spread/2, nodes_in_layer)[i]
                    size = note * 50 + 100
                    tree_data.append({'x': x_pos, 'y': y_pos, 'note': note, 'size': size})
                    current_idx += 1
                layer += 1
                
            df = pd.DataFrame(tree_data)
            star = pd.DataFrame({'x': [0], 'y': [10], 'note': [10], 'size': [600]})
            
            # 차트: 앤틱한 색감
            base = alt.Chart(df).mark_circle(opacity=0.8, stroke='#2c0a0a', strokeWidth=1).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='#d4af37', size=600, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=350, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)
            st.caption("▲ 숫자들이 마법처럼 쌓여 트리를 만듭니다")

        st.write("")
        if st.button(f"🪄 Cast Spell (Play Music)", key=f"btn_{key_prefix}"):
            with st.spinner("마법을 거는 중... ✨"):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
                    
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page ---
st.markdown("""
<div class="magic-header">
    <h1 class="main-title">Magic Math Carol</h1>
    <div class="sub-title">The Secret Melody of Hogwarts Numbers</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["Gryffindor (1학년)", "Slytherin (2학년)", "Ravenclaw (3학년)", "Hufflepuff (자유)"])

with t1:
    render_magic_tab("t1", "h-gry", "Year 1 • Shape Magic", "원주율(π)의 징글벨", "3.141592...", 
        """
        "원은 완벽한 대칭을 가진 마법진과 같단다."<br>
        원주율(π)은 끝없이 이어지는 불규칙한 주문이야. 
        이 숫자들이 <b>경쾌한 셔플 리듬</b>과 만나면 빗자루를 타고 나는 듯한 신나는 캐롤이 되지!
        """, "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_magic_tab("t2", "h-sly", "Year 2 • Number Potion", "순환소수 왈츠", "0.142857...", 
        """
        "규칙적인 반복은 강력한 마법의 기초지."<br>
        1/7처럼 같은 숫자가 도돌이표처럼 반복되는 수를 '순환소수'라고 한단다.
        이 규칙은 <b>우아한 3박자 왈츠</b>와 어우러져 최면에 걸린 듯한 춤곡을 만들어내지.
        """, "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_magic_tab("t3", "h-rav", "Year 3 • Root Mystery", "루트2의 거룩한 밤", "1.414213...", 
        """
        "보이지 않는 진실을 꿰뚫어 보렴."<br>
        정사각형의 대각선, 루트2(√2)는 끝을 알 수 없는 신비로운 수란다.
        이 깊이 있는 숫자는 <b>웅장한 합창(Choir)</b>이 되어 성스러운 겨울밤을 노래하지.
        """, "141421356237309504880168872420969807856967187537694", "holy", "blues")

with t4:
    render_magic_tab("t4", "h-huf", "Free Magic", "나만의 숫자 주문", "Make Your Own Spell", 
        """
        "너만의 특별한 숫자를 찾아보렴."<br>
        생일이나 소중한 날짜를 입력해봐. 
        수학적 마법이 너의 숫자를 세상에 하나뿐인 아름다운 멜로디로 바꿔줄 거야.
        """, "12251225", "joyful", "goldorange")

st.markdown("<br><br><div style='text-align:center; color:#555; font-family:Cinzel, serif;'>Designed for Magical Math Education 🪄</div>", unsafe_allow_html=True)
