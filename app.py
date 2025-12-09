import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Class", page_icon="🎄", layout="wide")

# --- 2. 🎨 Mobile-Friendly Christmas Design (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@400;700&family=Pretendard:wght@300;500;700&display=swap');
    
    /* [전체 배경: 따뜻한 겨울 오두막 느낌] */
    .stApp {
        background-color: #FDFBF7 !important;
        color: #2D3436 !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    /* [눈 효과: 모바일 성능 고려하여 가볍게] */
    .snowflake { position: fixed; top: -10px; z-index: 0; color: #D4AF37; opacity: 0.3; font-size: 1rem; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [헤더] */
    .header-box {
        text-align: center; padding: 30px 10px;
        background: linear-gradient(135deg, #165B33 0%, #0B3B24 100%);
        border-radius: 0 0 25px 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 30px; margin-top: -60px; /* 상단 여백 제거 */
    }
    .main-title {
        font-family: 'Gaegu', cursive; font-size: 3rem; font-weight: 700;
        color: #F1C40F; text-shadow: 2px 2px 0px #000; margin: 0;
    }
    .sub-title {
        color: #E8F5E9; font-size: 1rem; margin-top: 10px; font-weight: 400; letter-spacing: 1px;
    }

    /* [교육용 카드: 모바일에서도 잘 보이게] */
    .edu-card {
        background: #FFFFFF;
        border: 2px solid #EAEAEA;
        border-top: 6px solid #C0392B; /* 크리스마스 레드 포인트 */
        border-radius: 15px; padding: 25px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* [수학 개념 박스] */
    .math-concept {
        background-color: #E8F5E9;
        border-radius: 10px; padding: 15px;
        margin-top: 15px; border: 1px dashed #27AE60;
        font-size: 0.95rem; line-height: 1.6;
    }
    .concept-label { color: #1E8449; font-weight: 800; display: block; margin-bottom: 5px; font-size: 1rem; }

    /* [탭 디자인: 터치하기 편하게 큼직하게] */
    div[data-baseweb="tab-list"] { gap: 8px; flex-wrap: wrap; justify-content: center; }
    button[data-baseweb="tab"] {
        background-color: #EEE !important; border-radius: 20px !important;
        border: none !important; color: #555 !important; font-weight: bold; font-size: 0.95rem;
        padding: 8px 16px; margin-bottom: 5px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #C0392B !important; color: #FFF !important;
        box-shadow: 0 4px 10px rgba(192, 57, 43, 0.3);
    }

    /* [재생 버튼: 큼직하고 누르기 좋게] */
    .stButton>button {
        background: linear-gradient(to bottom, #27AE60, #1E8449) !important;
        color: white !important; border: none !important;
        border-radius: 15px; height: 60px; font-size: 1.2rem; font-weight: 800; width: 100%;
        box-shadow: 0 6px 0 #145A32; transition: all 0.1s; margin-top: 10px;
    }
    .stButton>button:hover { transform: translateY(2px); box-shadow: 0 4px 0 #145A32; }
    .stButton>button:active { transform: translateY(6px); box-shadow: none; }

    /* [반응형 폰트 조정 (모바일)] */
    @media (max-width: 600px) {
        .main-title { font-size: 2.2rem; }
        .sub-title { font-size: 0.9rem; }
        .edu-card { padding: 20px; }
        .stButton>button { font-size: 1.1rem; }
    }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(5, 15)}s; animation-delay:{np.random.uniform(0, 5)}s;">❄</div>' for _ in range(20)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (풍성한 오케스트라 레이어링) ---

def generate_wave(freq, duration, type="bell"):
    sr = 44100; num_samples = int(sr * duration); t = np.linspace(0, duration, num_samples, False)
    
    if type == "bell": # 영롱한 핸드벨
        return 0.5*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)*np.exp(-2*t) + 0.2*np.sin(2*np.pi*freq*4*t)*np.exp(-4*t)
    elif type == "strings": # 따뜻한 현악기 패드
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*0.5*t)
    elif type == "choir": # 코러스
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*0.998*t) + 0.2*np.sin(2*np.pi*freq*1.002*t)
    elif type == "sleigh": # 썰매 방울
        noise = np.random.uniform(-1, 1, len(t))
        return 0.1 * noise * np.sin(2*np.pi*3000*t) * np.exp(-15*t)
    return np.zeros(num_samples)

def match_len(wave, length):
    if len(wave) == length: return wave
    elif len(wave) > length: return wave[:length]
    else: return np.pad(wave, (0, length - len(wave)), 'constant')

def apply_envelope(wave, duration, type="short"):
    length = len(wave)
    if type == "short": env = np.exp(np.linspace(0, -5, length))
    else:
        att = int(length * 0.2); rel = int(length * 0.3); sus = length - att - rel
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
        
        # 멜로디 생성 (리듬감 부여)
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
        
        # 화음 & 베이스 & 효과음 추가
        pad = generate_wave(base_freq * 0.5, total_len/44100, "strings"); pad = match_len(pad, total_len)
        pad = apply_envelope(pad, total_len/44100, "long") * 0.35
        
        sleigh = generate_wave(0, total_len/44100, "sleigh"); sleigh = match_len(sleigh, total_len) * 0.3 if style == "joyful" else np.zeros(total_len)
        
        full_track.append(melody + pad + sleigh)
        
    if not full_track: return None
    full = np.concatenate(full_track); delay = int(44100 * 0.4); res = np.zeros(len(full) + delay); res[:len(full)] += full; res[delay:] += full * 0.4
    m = np.max(np.abs(res)); return res / m * 0.95 if m > 0 else res

# --- 4. UI 렌더링 (모바일 친화적 구조) ---

def render_tab_content(key_prefix, title, concept, math_desc, music_desc, default_nums, style, color_scheme):
    # 모바일에서는 컬럼이 자동으로 수직 정렬됩니다.
    c1, c2 = st.columns([1, 1], gap="medium")
    
    with c1:
        st.markdown(f"""
        <div class="edu-card">
            <h3 style="color:#C0392B; margin-top:0;">{title}</h3>
            <div style="color:#555; font-weight:bold; margin-bottom:15px; font-size:1.1rem;">{concept}</div>
            
            <div class="math-concept">
                <span class="concept-label">📐 수학적 원리 (Math Concept)</span>
                {math_desc}
            </div>
            
            <div class="math-concept" style="background-color:#FFF3E0; border-color:#FFB74D;">
                <span class="concept-label" style="color:#EF6C00;">🎼 음악적 해석 (Music Theory)</span>
                {music_desc}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        final_style = style
        
        # 4번째 탭 커스텀 입력
        if key_prefix == "t4":
            st.markdown('<div class="edu-card" style="padding:20px;">', unsafe_allow_html=True)
            st.markdown("**🔢 나만의 숫자 입력**")
            user_input = st.text_input("", value="", placeholder="예: 20250101", key=f"in_{key_prefix}", label_visibility="collapsed")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))
            
            st.markdown("**🎶 스타일 선택**")
            style_opt = st.radio("Style", ["Joyful (신나는 셔플)", "Waltz (우아한 왈츠)", "Holy (웅장한 합창)"], key=f"opt_{key_prefix}", label_visibility="collapsed")
            if "Joyful" in style_opt: final_style = "joyful"
            elif "Waltz" in style_opt: final_style = "waltz"
            else: final_style = "holy"
            st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="edu-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("### 🎄 Melody Tree")
        
        if final_nums:
            # [시각화] 트리 비주얼라이저
            digits = [int(d) for d in final_nums[:30] if d != '0']
            tree_data = []
            
            current_idx = 0; layer = 1; max_layers = 10 
            while current_idx < len(digits) and layer <= max_layers:
                nodes_in_layer = layer
                for i in range(nodes_in_layer):
                    if current_idx >= len(digits): break
                    note = digits[current_idx]
                    y_pos = 10 - layer 
                    width_spread = layer * 1.8
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
            top = alt.Chart(star).mark_point(shape='star', fill='#F4D03F', size=600, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=300).configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)
            st.caption("숫자의 높낮이(크기)에 따라 트리의 오너먼트가 배치됩니다.")

        st.write("")
        if st.button(f"🔔 음악 재생 (Play)", key=f"btn_{key_prefix}"):
            with st.spinner("캐롤 생성 중... 🎼"):
                bpm = 120 if final_style == "joyful" else 100 if final_style == "waltz" else 80
                audio = compose_music(final_nums, bpm, final_style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Layout ---
st.markdown("""
<div class="header-box">
    <div class="main-title">Merry Math Class</div>
    <div class="sub-title">🎄 중학교 수학으로 만드는 나만의 크리스마스 캐롤 🎄</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["중1: 원주율", "중2: 순환소수", "중3: 무리수", "자유 탐구"])

with t1:
    render_tab_content("t1", "원주율(π) 징글벨", "중1 도형 - 원의 성질", 
        """
        원은 완벽한 대칭을 가진 도형입니다. 하지만 원주율(π)은 3.14159... 처럼 숫자가 불규칙하게 영원히 이어지는 비순환 소수입니다.
        """,
        """
        이 불규칙한 숫자들이 <b>'경쾌한 셔플 리듬(Shuffle)'</b>과 만나면, 마치 울퉁불퉁한 눈길을 달리는 썰매 소리처럼 신나는 캐롤이 됩니다.
        """, "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_tab_content("t2", "순환소수 왈츠", "중2 유리수 - 순환소수", 
        """
        1/7 = 0.142857... 처럼 일정한 구간(순환마디)이 계속 반복되는 소수를 순환소수라고 합니다. 여기서는 '142857'이 반복됩니다.
        """,
        """
        이 규칙적인 반복 패턴은 춤추기 좋은 <b>'3박자 왈츠(Waltz)'</b> 리듬과 완벽하게 어울려, 우아하고 몽환적인 분위기를 만듭니다.
        """, "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_tab_content("t3", "루트2의 거룩한 밤", "중3 제곱근 - 무리수", 
        """
        제곱해서 2가 되는 수, 루트2(1.414...)는 인류가 처음 발견한 무리수입니다. 분수로 나타낼 수 없는 깊고 신비로운 수입니다.
        """,
        """
        끝을 알 수 없는 이 숫자의 깊이를 <b>'웅장한 합창(Choir)'</b> 사운드로 표현했습니다. 고요하고 성스러운 겨울밤을 느껴보세요.
        """, "141421356237309504880168872420969807856967187537694", "holy", "oranges")

with t4:
    render_tab_content("t4", "나만의 숫자 캐롤", "창의 융합 탐구 활동", 
        """
        수학은 어디에나 있습니다. 1225(크리스마스), 생일, 전화번호 등 나에게 의미 있는 숫자를 입력해보세요.
        """,
        """
        수학적 알고리즘이 여러분의 숫자를 분석하여 <b>세상에 하나뿐인 멜로디</b>로 변환해 줍니다. 어떤 스타일이 어울릴지 실험해보세요!
        """, "12251225", "joyful", "purples")

st.markdown("<br><hr style='border-top:1px dashed #aaa'><div style='text-align:center; color:#555; font-size:0.9rem;'>즐거운 수학 체험 활동 | Designed for Education</div>", unsafe_allow_html=True)
