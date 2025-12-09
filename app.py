import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Christmas Music Box", page_icon="🎁", layout="wide")

# --- 2. 🎨 Christmas Music Box Design (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@700&family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;700&display=swap');
    
    /* [전체 배경: 크리스마스 레드 & 눈송이 패턴] */
    .stApp {
        background-color: #4a0e0e !important; /* 깊은 버건디 */
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(255,215,0, 0.1) 0%, transparent 20%),
            radial-gradient(circle at 90% 80%, rgba(0,255,0, 0.05) 0%, transparent 20%);
        color: #fdfbf7 !important;
        font-family: 'Gowun Dodum', sans-serif !important;
    }

    /* [눈 효과] */
    .snowflake { position: fixed; top: -10px; z-index: 0; color: rgba(255,255,255,0.3); font-size: 1em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [헤더] */
    .party-header {
        text-align: center; padding: 40px 0;
        border-bottom: 3px double #d4af37; /* 골드 라인 */
        margin-bottom: 40px;
        background: rgba(0,0,0,0.2);
        border-radius: 0 0 30px 30px;
    }
    .main-title {
        font-family: 'Mountains of Christmas', cursive; font-size: 5rem; 
        color: #d4af37; text-shadow: 2px 2px 4px #000; margin: 0; letter-spacing: 2px;
    }
    .sub-title { font-family: 'Noto Sans KR', sans-serif; font-size: 1.2rem; color: #f1c40f; margin-top: 10px; opacity: 0.9; }

    /* [왼쪽: 교육용 카드 (선물상자 컨셉)] */
    .gift-card {
        background-color: #fffaf0; /* 크림색 종이 */
        border: 4px solid #165b33; /* 크리스마스 그린 테두리 */
        border-radius: 15px; padding: 30px;
        color: #2d3436;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.3);
        position: relative; height: 100%;
    }
    .gift-card::before { /* 리본 장식 */
        content: "🎀 Math Gift"; position: absolute; top: -15px; left: 20px;
        background: #c0392b; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }

    /* [오른쪽: 뮤직 플레이어 UI (핵심!)] */
    .music-player {
        background: linear-gradient(145deg, #2c3e50, #000000);
        border: 2px solid #555;
        border-radius: 30px;
        padding: 20px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5), inset 0 0 20px rgba(255,255,255,0.1);
        color: white; text-align: center;
    }
    .screen-display {
        background-color: #111; border-radius: 20px;
        border: 2px solid #333; padding: 10px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        margin-bottom: 20px; min-height: 300px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .track-info { color: #f1c40f; font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 10px; }

    /* [재생 버튼: 금색 플레이 버튼] */
    .stButton>button {
        background: linear-gradient(to bottom, #f1c40f, #f39c12) !important;
        color: #2c3e50 !important; border: 2px solid #fff !important;
        border-radius: 50px; height: 60px; width: 100%;
        font-size: 1.3rem; font-weight: 900;
        box-shadow: 0 5px 15px rgba(243, 156, 18, 0.4); transition: 0.2s;
    }
    .stButton>button:hover { transform: scale(1.02); background: #f39c12 !important; box-shadow: 0 0 20px #f1c40f; }

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { gap: 10px; justify-content: center; margin-bottom: 30px; }
    button[data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.1) !important; color: #aaa !important; border: none !important;
        font-family: 'Mountains of Christmas', cursive; font-size: 1.2rem; font-weight: bold;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #c0392b !important; color: #fff !important; 
        border: 2px solid #d4af37 !important; border-radius: 20px !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
    }

    /* [설명 텍스트] */
    .edu-text { font-size: 1.05rem; line-height: 1.8; }
    .edu-text b { color: #c0392b; background-color: #ffeaa7; padding: 2px 5px; border-radius: 4px; }
    
    /* [입력창] */
    .stTextInput input { text-align: center; border-radius: 10px; background: #fff; color: #333; }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(10, 25)}s; animation-delay:{np.random.uniform(0, 10)}s;">❄</div>' for _ in range(50)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (안정화됨) ---
# (오디오 엔진 코드는 이전과 동일합니다. 길이 보정 함수 포함)
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

# --- 4. UI Rendering (뮤직박스 스타일) ---

def render_music_box(key, title, subtitle, desc, default_nums, style):
    c1, c2 = st.columns([1, 1], gap="large")
    
    # [Left: Educational Content (선물상자)]
    with c1:
        st.markdown(f"""
        <div class="gift-card">
            <h2 style="color:#165b33; font-family:'Mountains of Christmas'; margin:0; font-size:2.5rem;">{title}</h2>
            <div style="color:#7f8c8d; font-weight:bold; margin-bottom:15px;">{subtitle}</div>
            <div class="edu-text">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        final_style = style
        
        if key == "t4":
            st.markdown("")
            st.markdown('<div class="gift-card" style="padding:20px; height:auto; margin-top:20px;">', unsafe_allow_html=True)
            user_input = st.text_input("숫자 입력 (Number Input)", value="", placeholder="12251225", key=f"in_{key}")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))
            
            st.markdown("---")
            sel = st.radio("음악 스타일 (Music Style)", ["Joyful (셔플)", "Waltz (왈츠)", "Holy (합창)"], key=f"sel_{key}")
            if "Joyful" in sel: final_style = "joyful"
            elif "Waltz" in sel: final_style = "waltz"
            else: final_style = "holy"
            st.markdown("</div>", unsafe_allow_html=True)

    # [Right: Music Player (블랙 & 골드 UI)]
    with c2:
        st.markdown(f"""
        <div class="music-player">
            <div style="margin-bottom:15px; font-weight:bold; color:#f1c40f;">Now Playing: {title}</div>
            <div class="screen-display">
        """, unsafe_allow_html=True)
        
        if final_nums:
            # 트랙 정보 표시
            st.markdown(f'<div class="track-info">TRACK DATA: {final_nums[:12]}...</div>', unsafe_allow_html=True)
            
            # [Visual] 오디오 비주얼라이저 (트리)
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
            
            color_scheme = {'joyful': 'reds', 'waltz': 'greens', 'holy': 'oranges'}[final_style]
            
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=1).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='#fff', size=600).encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=250, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True) # End Screen
        
        # 재생 버튼
        if st.button(f"▶ PLAY MUSIC", key=f"btn_{key}"):
            with st.spinner("Loading Track..."):
                bpm = 120 if final_style == "joyful" else 100 if final_style == "waltz" else 80
                audio = compose_music(final_nums, bpm, final_style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
        st.markdown('</div>', unsafe_allow_html=True) # End Player

# --- Main Page ---
st.markdown("""
<div class="party-header">
    <div class="main-title">Merry Math Christmas</div>
    <div class="sub-title">🎄 The Magic Music Box of Numbers 🎄</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["🔴 중1 (도형)", "🟢 중2 (수)", "🟡 중3 (무리수)", "🟣 자유 탐구"])

with t1:
    render_music_box("t1", "Pi Jingle Bell", "중1 - 도형의 성질", 
        """
        <b>"원주율(π)의 마법"</b><br>
        3.141592... 끝없이 이어지는 불규칙한 숫자들이
        <b>신나는 징글벨(Joyful)</b> 리듬으로 변신합니다!
        트리의 붉은 장식볼이 춤추는 모습을 감상해보세요.
        """, "314159265358979323846264338327950288419716939937510", "joyful")

with t2:
    render_music_box("t2", "Decimal Waltz", "중2 - 유리수와 순환소수", 
        """
        <b>"순환소수의 춤"</b><br>
        1/7 = 0.142857... 규칙적으로 반복되는 숫자의 패턴이
        <b>우아한 왈츠(Waltz)</b> 곡이 되었습니다.
        초록빛 트리가 빙글빙글 도는 무도회장을 상상해보세요.
        """, "142857142857142857142857142857142857142857", "waltz")

with t3:
    render_music_box("t3", "Root 2 Harmony", "중3 - 제곱근과 실수", 
        """
        <b>"무리수의 울림"</b><br>
        깊고 신비로운 루트2(1.414...)는 <b>웅장한 합창(Holy)</b>과 만났습니다.
        황금빛으로 빛나는 트리가 성스러운 크리스마스 밤을 밝혀줍니다.
        """, "141421356237309504880168872420969807856967187537694", "holy")

with t4:
    render_music_box("t4", "My Custom Carol", "자유 학기제 탐구", 
        """
        <b>"나만의 오르골 만들기"</b><br>
        여러분의 소중한 숫자를 입력하고, 원하는 스타일을 골라보세요.
        이 뮤직박스가 세상에 하나뿐인 캐롤을 연주해 드립니다.
        """, "12251225", "joyful")

st.markdown("<br><br><div style='text-align:center; color:#f1c40f; font-size:0.9rem;'>Designed by Math Santa 🎅</div>", unsafe_allow_html=True)
