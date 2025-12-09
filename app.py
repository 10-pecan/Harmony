import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Class", page_icon="🎄", layout="wide")

# --- 2. 🎨 Cozy Textbook Design (따뜻한 교과서 스타일) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap');
    
    /* [전체 배경] */
    .stApp {
        background-color: #FDFBF7 !important;
        color: #4A4A4A !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* [눈 효과] */
    .snowflake { position: fixed; top: -10px; z-index: 99; color: #D4AF37; opacity: 0.4; font-size: 1.2em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [헤더] */
    .header-box {
        text-align: center; padding: 40px 0;
        background: url('https://www.transparenttextures.com/patterns/snow.png'), linear-gradient(to right, #C0392B, #D35400);
        border-radius: 0 0 30px 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 40px; color: white;
    }
    .main-title {
        font-family: 'Gaegu', cursive; font-size: 4.5rem; font-weight: 700;
        text-shadow: 2px 2px 0px #8E2800; margin: 0;
    }
    .sub-title { font-size: 1.2rem; margin-top: 10px; opacity: 0.9; font-weight: 400; }

    /* [카드] */
    .edu-card {
        background: #FFFFFF;
        border: 2px solid #EAEAEA;
        border-top: 5px solid #27AE60;
        border-radius: 15px; padding: 30px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.03);
        height: 100%;
    }

    /* [선생님 노트] */
    .teacher-note {
        background-color: #F1F8E9;
        border-left: 5px solid #7CB342;
        padding: 20px; border-radius: 10px;
        margin-top: 20px; font-size: 0.95rem; line-height: 1.7; color: #33691E;
    }
    .note-label { font-weight: 900; color: #558B2F; display: block; margin-bottom: 5px; }

    /* [탭] */
    div[data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    button[data-baseweb="tab"] {
        background-color: #EEE !important; border-radius: 10px 10px 0 0 !important;
        border: none !important; color: #777 !important; font-weight: bold; font-size: 1rem;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #C0392B !important; color: #FFF !important;
    }

    /* [버튼] */
    .stButton>button {
        background: linear-gradient(to bottom, #27AE60, #219150) !important;
        color: white !important; border: 2px solid #1E8449 !important;
        border-radius: 50px; height: 60px; font-size: 1.3rem; font-weight: 800; width: 100%;
        box-shadow: 0 5px 0 #145A32; transition: all 0.2s;
    }
    .stButton>button:hover { transform: translateY(2px); box-shadow: 0 2px 0 #145A32; }
    .stButton>button:active { transform: translateY(5px); box-shadow: none; }

    /* [입력창] */
    .stTextInput input {
        border: 2px solid #BDC3C7; border-radius: 10px; text-align: center; color: #2C3E50;
    }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(5, 15)}s; animation-delay:{np.random.uniform(0, 5)}s;">❄</div>' for _ in range(30)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine ---

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
        att = int(length * 0.2); rel = int(length * 0.3); sus = length - att - rel; 
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

# --- 4. UI 렌더링 ---

def render_class_tab(key_prefix, title, subtitle, math_note, default_nums, initial_style, initial_color):
    c1, c2 = st.columns([1, 1.2], gap="large")
    
    with c1:
        st.markdown(f"""
        <div class="edu-card">
            <h2 style="color:#C0392B; margin-bottom:5px;">{title}</h2>
            <div style="color:#7F8C8D; font-weight:bold; margin-bottom:20px;">{subtitle}</div>
            
            <div class="teacher-note">
                <span class="note-label">🧑‍🏫 수학 선생님의 Tip</span>
                {math_note}
            </div>
            <br>
        """, unsafe_allow_html=True)
        
        # [NEW] 4번째 탭(자유 탐구)일 경우 입력창 + 스타일 선택 옵션 추가
        final_nums = default_nums
        current_style = initial_style
        current_color = initial_color

        if key_prefix == "t4":
            st.markdown("##### 1️⃣ 숫자 입력")
            user_input = st.text_input("", value="", placeholder="12251225", key=f"in_{key_prefix}", label_visibility="collapsed")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))
            
            st.markdown("##### 2️⃣ 캐롤 스타일 선택")
            style_option = st.radio(
                "스타일을 골라보세요", 
                ["🔔 Joyful (경쾌한 셔플)", "💃 Waltz (우아한 3박자)", "👼 Holy (웅장한 합창)"],
                label_visibility="collapsed",
                key=f"style_{key_prefix}"
            )
            
            # 선택에 따라 스타일과 색상 변경
            if "Joyful" in style_option:
                current_style = "joyful"
                current_color = "reds"
            elif "Waltz" in style_option:
                current_style = "waltz"
                current_color = "greens"
            else:
                current_style = "holy"
                current_color = "oranges"

        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="edu-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("### 🎄 Melody Tree Visualization")
        
        if final_nums:
            digits = [int(d) for d in final_nums[:45] if d != '0']
            tree_data = []
            
            # 트리 구조 생성
            current_idx = 0
            layer = 1
            max_layers = 10 
            
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
            
            # 차트 그리기 (색상 동적 적용)
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=1.5).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=current_color), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='#F1C40F', size=600, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=400).configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)
            st.caption(f"▲ 숫자들이 {layer-1}층짜리 크리스마스 트리를 만들었어요!")

        st.write("")
        # 버튼에 현재 스타일 표시
        if st.button(f"🔔 연주 시작 ({current_style.title()} Ver.)", key=f"btn_{key_prefix}"):
            with st.spinner("캐롤 편곡 중..."):
                bpm = 120 if current_style == "joyful" else 100 if current_style == "waltz" else 80
                audio = compose_music(final_nums, bpm, current_style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
                    
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page ---
st.markdown("""
<div class="header-box">
    <div class="main-title">Math Christmas Carol</div>
    <div class="sub-title">중학교 수학으로 꾸미는 나만의 멜로디 트리</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["🔴 중1 (도형)", "🟢 중2 (수)", "🟡 중3 (무리수)", "🟣 자유 탐구"])

with t1:
    render_class_tab("t1", "원주율 (Pi) 징글벨", "중1-2 도형의 성질", 
        """
        <b>"원은 완벽한 대칭을 가진 도형이야."</b><br>
        원의 둘레를 지름으로 나눈 값인 <b>원주율(π)</b>은 3.141592... 처럼 숫자가 불규칙하게 영원히 이어져. 
        이 불규칙함이 <b>경쾌한 셔플 리듬(Joyful)</b>이 되면, 마치 눈 내리는 날 썰매를 타는 듯 신난단다!
        """, "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_class_tab("t2", "순환소수 왈츠", "중2-1 유리수와 순환소수", 
        """
        <b>"반복되는 것에도 규칙이 있단다."</b><br>
        1 나누기 7을 해볼까? <b>0.142857...</b> 처럼 여섯 개의 숫자가 도돌이표처럼 계속 반복되지?
        이런 규칙적인 숫자는 <b>우아한 3박자 왈츠(Waltz)</b> 춤곡과 정말 잘 어울려.
        """, "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_class_tab("t3", "루트2의 거룩한 밤", "중3-1 제곱근과 실수", 
        """
        <b>"세상의 비밀을 담은 숫자야."</b><br>
        제곱해서 2가 되는 수, <b>루트2(√2)</b>는 인류가 처음 발견한 무리수란다.
        끝없이 이어지는 깊고 신비로운 숫자의 배열을 <b>웅장한 합창(Holy)</b> 소리로 표현해봤어.
        """, "141421356237309504880168872420969807856967187537694", "holy", "oranges")

with t4:
    render_class_tab("t4", "나만의 숫자 캐롤", "자유 학기제 탐구 활동", 
        """
        <b>"어떤 음악이 나올지 실험해봐!"</b><br>
        숫자를 입력하고 아래에서 <b>음악 스타일(셔플/왈츠/합창)</b>을 직접 골라보렴.
        스타일을 바꿀 때마다 트리의 색깔과 분위기가 확 달라지는 걸 볼 수 있을 거야.
        """, "12251225", "joyful", "purples")

st.markdown("<br><hr><div style='text-align:center; color:#999;'>Designed for Joyful Math Education 🎁</div>", unsafe_allow_html=True)
