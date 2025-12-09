import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Christmas Class", page_icon="🏫", layout="wide")

# --- 2. 🎨 Christmas Classroom Design (CSS) ---
st.markdown("""
<style>
    /* [폰트] 귀여운 손글씨(Gamja Flower) + 깔끔한 고딕(Noto Sans) */
    @import url('https://fonts.googleapis.com/css2?family=Gamja+Flower&family=Noto+Sans+KR:wght@400;700;900&display=swap');
    
    /* [전체 배경: 깊은 초록 칠판 + 눈송이] */
    .stApp {
        background-color: #1A3C34 !important; /* 칠판색 */
        background-image: 
            radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 3px),
            radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 2px),
            radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 3px);
        background-size: 550px 550px, 350px 350px, 250px 250px;
        background-position: 0 0, 40px 60px, 130px 270px;
        color: #333 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* [헤더 디자인] */
    .board-header {
        text-align: center; padding: 40px 0;
        border-bottom: 3px dashed #F1C40F; /* 노란색 분필 라인 */
        margin-bottom: 40px;
    }
    .main-title {
        font-family: 'Gamja Flower', cursive; font-size: 4.5rem; color: #FFFFFF;
        text-shadow: 3px 3px 0px #C0392B; margin: 0;
    }
    .sub-title {
        font-family: 'Noto Sans KR', sans-serif; font-size: 1.2rem; color: #E8F5E9; 
        background-color: rgba(255,255,255,0.1); display: inline-block; 
        padding: 8px 25px; border-radius: 50px; margin-top: 15px; border: 1px solid #FFF;
    }

    /* [카드 디자인: 넓고 시원하게] */
    .christmas-card {
        background-color: #FFFAFA; /* 눈처럼 하얀 배경 */
        border: 4px solid #C0392B; /* 크리스마스 레드 테두리 */
        border-radius: 20px;
        padding: 35px;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.2); /* 입체 그림자 */
        margin-bottom: 30px;
        position: relative;
    }
    /* 카드 장식 (상단) */
    .christmas-card::before {
        content: "🎄 Math & Music 🎄"; 
        position: absolute; top: -15px; left: 50%; transform: translateX(-50%);
        background-color: #1A3C34; color: #F1C40F; 
        padding: 5px 20px; border-radius: 20px; font-weight: bold; border: 2px solid #F1C40F;
    }

    /* [제목 뱃지: 큼직하고 잘 보이게] */
    .grade-badge {
        display: block; width: 100%; text-align: center;
        padding: 10px; border-radius: 10px;
        font-size: 1.1rem; font-weight: 800; color: #fff;
        margin-bottom: 15px; text-transform: uppercase;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .bg-red { background: linear-gradient(45deg, #FF512F, #DD2476); }
    .bg-green { background: linear-gradient(45deg, #11998e, #38ef7d); }
    .bg-gold { background: linear-gradient(45deg, #F2994A, #F2C94C); }
    .bg-purple { background: linear-gradient(45deg, #8E2DE2, #4A00E0); }

    /* [선생님 설명 박스: 칠판 지우개 느낌] */
    .teacher-box {
        background-color: #E8F5E9; /* 연한 초록 */
        border-left: 6px solid #2E7D32;
        padding: 20px; border-radius: 8px;
        margin-top: 20px; font-size: 1rem; line-height: 1.7; color: #2D3436;
    }
    .teacher-label { font-weight: 900; color: #2E7D32; font-size: 1.1rem; margin-bottom: 5px; display: block; }

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { gap: 15px; justify-content: center; }
    button[data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.1) !important; color: #AAA !important; 
        border: 2px solid #555 !important; border-radius: 12px !important; font-weight: bold;
        padding: 10px 20px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFF !important; color: #C0392B !important; 
        border: 2px solid #C0392B !important; box-shadow: 0 0 15px rgba(255,255,255,0.5);
    }

    /* [재생 버튼: 선물상자] */
    .play-btn {
        background: linear-gradient(to bottom, #C0392B, #922B21) !important;
        color: #FFF !important; border: 2px solid #F1C40F !important;
        height: 70px; border-radius: 15px; font-size: 1.3rem; font-weight: 800;
        width: 100%; box-shadow: 0 5px 0 #581814; transition: all 0.1s;
    }
    .play-btn:active { transform: translateY(5px); box-shadow: none; }
    .stButton>button { @extend .play-btn; } /* Streamlit 버튼에 적용 */

    /* [단계 표시] */
    .step-label {
        font-family: 'Gamja Flower', cursive; font-size: 1.5rem; color: #C0392B;
        border-bottom: 2px solid #EEE; padding-bottom: 5px; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 🎹 Audio Engine (에러 방지 & 캐롤 사운드) ---

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
    # Scale 확장 (에러 방지)
    if style == "joyful": scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    elif style == "waltz": scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    else: scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    
    beat_sec = 60.0 / bpm; full_track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit); base_freq = scale[idx % len(scale)]
        
        notes = []
        if style == "joyful": # 셔플
            if idx % 2 == 0: notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)]
            else: notes = [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        elif style == "waltz": # 3박자
            notes = [(base_freq, 1.0), (base_freq*1.25, 1.0), (base_freq*1.5, 1.0)]
        else: # 4박자
            notes = [(base_freq, 4.0)]
            
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

# --- 4. UI Rendering (카드형 + 가독성 최적화) ---

def render_tab_content(key_prefix, badge_cls, badge_text, title, desc, default_nums, style, color_scheme):
    
    # 1. 상단: 수학 개념 및 입력 (카드 디자인)
    st.markdown(f"""
    <div class="christmas-card">
        <div class="step-label">Step 1. 오늘의 수학 숫자</div>
        <span class="grade-badge {badge_cls}">{badge_text}</span>
        <h2 style="text-align:center; color:#2C3E50; margin-bottom:20px;">{title}</h2>
        
        <div class="teacher-box">
            <span class="teacher-label">🧑‍🏫 선생님의 한마디</span>
            {desc}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 숫자 데이터 준비
    final_nums = default_nums
    if key_prefix == "t4":
        c_in1, c_in2 = st.columns([1, 2])
        with c_in2:
            user_input = st.text_input("여기에 숫자를 입력하세요 (예: 1225)", value="", key=f"in_{key_prefix}")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))
        with c_in1:
            st.info("👈 나만의 숫자를 입력해볼까요?")

    # 2. 하단: 시각화 및 재생 (카드 디자인)
    st.markdown(f"""
    <div class="christmas-card">
        <div class="step-label">Step 2. 소리와 눈으로 확인하기</div>
    """, unsafe_allow_html=True)
    
    col_vis, col_play = st.columns([2, 1])
    
    with col_vis:
        if final_nums:
            # [Visual] 트리 비주얼라이저
            digits = [int(d) for d in final_nums[:40] if d != '0']
            tree_data = []
            
            # 트리 좌표 계산
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
            
            # 차트 그리기
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=1.5).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='#F1C40F', size=600, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=350, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)
            st.caption("▲ 숫자들이 모여 반짝이는 크리스마스 트리가 되었어요!")

    with col_play:
        st.write("")
        st.write("")
        st.markdown("##### 🎵 음악 만들기")
        if st.button(f"🔔 캐롤 재생 (Play)", key=f"btn_{key_prefix}"):
            with st.spinner("선물을 포장하는 중... 🎁"):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
    st.markdown("</div>", unsafe_allow_html=True) # End Card

# --- Main Layout ---
st.markdown("""
<div class="board-header">
    <h1 class="main-title">Merry Math Class</h1>
    <div class="sub-title">🎄 중학교 수학으로 만드는 나만의 크리스마스 캐롤 🎄</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["중1 (도형)", "중2 (수)", "중3 (무리수)", "자유 탐구"])

with t1:
    render_tab_content("t1", "bg-red", "중1 - 도형의 성질", "원주율(Pi) 징글벨", 
        """
        원은 어디서 봐도 똑같은 <b>'대칭'</b> 도형이야. 하지만 원주율(π)은 3.14159... 처럼 숫자가 불규칙하게 계속되지.<br>
        이 불규칙한 숫자들을 <b>경쾌한 셔플 리듬</b>으로 연주하면, 마치 <b>눈길을 달리는 썰매 소리</b>처럼 신나는 캐롤이 된단다!
        """, "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_tab_content("t2", "bg-green", "중2 - 유리수와 순환소수", "순환소수 왈츠", 
        """
        1 나누기 7을 해볼까? <b>0.142857...</b> 처럼 여섯 개의 숫자가 도돌이표처럼 계속 반복되지?<br>
        이런 '순환소수'의 규칙적인 리듬은 춤추기 좋은 <b>3박자 왈츠(Waltz)</b>와 정말 잘 어울려. 함께 춤을 추는 느낌을 상상해보렴.
        """, "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_tab_content("t3", "bg-gold", "중3 - 제곱근과 실수", "루트2의 거룩한 밤", 
        """
        제곱해서 2가 되는 수, <b>루트2(√2)</b>는 인류가 처음 발견한 '무리수'란다.<br>
        1.414... 끝을 알 수 없는 이 숫자의 깊은 울림을 <b>웅장한 합창(Choir)</b>으로 표현했어. 고요한 겨울밤에 어울리는 소리야.
        """, "141421356237309504880168872420969807856967187537694", "holy", "oranges")

with t4:
    render_tab_content("t4", "bg-purple", "자유 학기제 - 창의 탐구", "나만의 숫자 캐롤 만들기", 
        """
        수학은 어디에나 있어! <b>1225(크리스마스)</b>나 <b>너의 생일</b>을 입력해봐.<br>
        그 숫자들 속에 어떤 멜로디가 숨어있는지 확인해보는 거야. 너만의 특별한 캐롤을 친구들에게 들려주렴!
        """, "12251225", "joyful", "purples")

st.markdown("<br><div style='text-align:center; color:#CCC; font-size:0.8rem;'>Designed for Joyful Math Education • 2025 Winter</div>", unsafe_allow_html=True)
