import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol", page_icon="❄️", layout="wide")

# --- 2. 🎨 White Luxury Design ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700;900&family=Playfair+Display:ital,wght@1,700&display=swap');
    
    /* [전체 배경] */
    .stApp {
        background-color: #F8F9FA !important;
        background-image: linear-gradient(to bottom, #ffffff 0%, #eef2f3 100%);
        color: #2C3E50 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* [눈 내리는 효과] */
    .snowflake {
        position: fixed; top: -10px; z-index: 0;
        color: #BCCCDC; font-size: 1.2em; opacity: 0.7;
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { transform: translateY(-10vh); }
        100% { transform: translateY(110vh); }
    }

    /* [타이틀] */
    .holiday-title {
        font-family: 'Playfair Display', serif;
        font-size: 4.5rem; font-weight: 900; font-style: italic;
        text-align: center; color: #C92A2A; 
        margin-top: 20px; letter-spacing: -1px;
        text-shadow: 2px 2px 0px #FFF, 5px 5px 0px #E9ECEF;
    }
    .holiday-sub {
        text-align: center; color: #868E96; font-size: 1.0rem;
        letter-spacing: 3px; text-transform: uppercase; margin-bottom: 40px;
    }

    /* [컨텐츠 박스] */
    .content-box {
        background: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03);
        padding: 30px;
        border: 1px solid #F1F3F5;
        margin-bottom: 20px;
        height: 100%;
    }

    /* [수학 뱃지] */
    .badge {
        display: inline-block; padding: 5px 12px;
        border-radius: 20px; font-weight: 700; font-size: 0.8rem;
        margin-bottom: 15px;
    }
    .badge-1 { background: #FFC9C9; color: #C92A2A; } 
    .badge-2 { background: #B2F2BB; color: #2B8A3E; } 
    .badge-3 { background: #FFEC99; color: #E67700; } 
    .badge-c { background: #E5DBFF; color: #5F3DC4; } 

    /* [재생 버튼] */
    .stButton>button {
        background: linear-gradient(135deg, #C92A2A 0%, #A61E4D 100%) !important;
        color: #FFF !important; border: none; height: 60px; border-radius: 12px;
        font-family: 'Playfair Display', serif; font-size: 1.3rem; font-weight: 700;
        box-shadow: 0 8px 20px rgba(201, 42, 42, 0.2);
        width: 100%; transition: all 0.3s;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(201, 42, 42, 0.3); }

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { background: transparent !important; gap: 20px; justify-content: center; }
    button[data-baseweb="tab"] {
        background: #F8F9FA !important; border-radius: 10px !important; border: 1px solid #E9ECEF !important;
        color: #868E96 !important; font-size: 1rem !important; padding: 10px 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: #FFFFFF !important; color: #C92A2A !important;
        border: 1px solid #C92A2A !important; font-weight: bold !important;
        box-shadow: 0 5px 15px rgba(201, 42, 42, 0.1) !important;
    }
    
    /* [설명 텍스트] HTML 태그 적용을 위해 스타일 지정 */
    .desc-text {
        font-size: 1rem; line-height: 1.6; color: #495057;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 눈 내리는 효과 ---
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(10, 20)}s; animation-delay:{np.random.uniform(0, 10)}s;">❄</div>' for _ in range(30)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 4. 오디오 엔진 (길이 보정 기능 추가) ---

def generate_wave(freq, duration, type="bell"):
    sr = 44100
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if type == "bell": 
        return 0.6*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)*np.exp(-2*t) + 0.1*np.sin(2*np.pi*freq*4*t)
    elif type == "strings":
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*0.5*t)
    elif type == "sleigh":
        noise = np.random.uniform(-1, 1, len(t))
        return 0.1 * noise * np.sin(2*np.pi*2000*t) * np.exp(-10*t)
    return np.zeros(num_samples)

# [FIX] 길이 강제 맞춤 함수 (핵심 에러 해결)
def match_len(wave, length):
    if len(wave) == length: return wave
    elif len(wave) > length: return wave[:length]
    else: return np.pad(wave, (0, length - len(wave)), 'constant')

def apply_envelope(wave, duration, type="short"):
    length = len(wave)
    if type == "short": 
        env = np.exp(np.linspace(0, -5, length))
    else:
        att = int(length*0.2); rel = int(length*0.3); sus = length - att - rel
        if sus < 0: sus = 0
        env = np.concatenate([np.linspace(0,1,att), np.full(sus,1.0), np.linspace(1,0,rel)])
    
    # Envelope 길이도 Wave와 맞춤
    env = match_len(env, length)
    return wave * env

def create_carol_phrase(digit, bpm):
    scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    beat_sec = 60.0 / bpm
    idx = int(digit) if digit.isdigit() else 0
    base_freq = scale[idx % len(scale)]
    
    if idx % 2 == 0: 
        notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)]
    else: 
        notes = [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        
    melody_waves = []
    for f, d in notes:
        dur = d * beat_sec
        w = generate_wave(f, dur, "bell")
        w = apply_envelope(w, dur, "short")
        melody_waves.append(w)
    
    melody = np.concatenate(melody_waves)
    total_len = len(melody) # 이 길이를 기준으로 모든 반주를 맞춤
    
    # 반주 생성 (길이 강제 고정)
    pad_freq = base_freq * 0.5
    
    # 1. Pad Wave
    pad = generate_wave(pad_freq, total_len/44100, "strings")
    pad = match_len(pad, total_len) # 길이 맞춤
    pad += match_len(generate_wave(pad_freq * 1.5, total_len/44100, "strings"), total_len)
    pad = apply_envelope(pad, total_len/44100, "long") * 0.3
    
    # 2. Sleigh Bell
    sleigh = generate_wave(0, total_len/44100, "sleigh")
    sleigh = match_len(sleigh, total_len) # 길이 맞춤
    sleigh = sleigh * 0.4
    
    return melody + pad + sleigh

def compose_carol(nums, bpm):
    track = [create_carol_phrase(char, bpm) for char in nums if char.isdigit()]
    if not track: return None
    full = np.concatenate(track)
    
    delay = int(44100 * 0.3)
    res = np.zeros(len(full) + delay)
    res[:len(full)] += full
    res[delay:] += full * 0.4
    
    m = np.max(np.abs(res))
    return res / m * 0.95 if m > 0 else res

# --- 5. UI Logic ---

def render_tab_content(key_suffix, badge_class, badge_text, title, desc, default_nums, is_custom=False):
    c1, c2 = st.columns([1, 1], gap="large")
    
    with c1:
        st.markdown(f'<div class="content-box">', unsafe_allow_html=True)
        st.markdown(f'<span class="badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
        st.markdown(f"### {title}")
        
        # [FIX] HTML 태그가 그대로 보이는 문제 해결 (unsafe_allow_html=True)
        st.markdown(f'<div class="desc-text">{desc}</div>', unsafe_allow_html=True)
        
        if is_custom:
            user_in = st.text_input("숫자 입력", placeholder="20251225", key=f"input_{key_suffix}")
            current_nums = "".join(filter(str.isdigit, user_in)) if user_in else default_nums
        else:
            current_nums = default_nums
            
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="content-box">', unsafe_allow_html=True)
        
        if current_nums:
            digits = [int(d) for d in current_nums[:20] if d != '0']
            tree_data = []
            level, count = 1, 0
            for d in digits:
                tree_data.append({'Level': -level, 'Pos': count - (level-1)/2, 'Note': d})
                count += 1
                if count >= level: level += 1; count = 0
            
            df = pd.DataFrame(tree_data)
            color_scheme = 'reds' if '1' in key_suffix else 'greens' if '2' in key_suffix else 'oranges'
            if is_custom: color_scheme = 'purples'

            c = alt.Chart(df).mark_circle(size=400).encode(
                x=alt.X('Pos', axis=None), y=alt.Y('Level', axis=None),
                color=alt.Color('Note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['Note']
            ).properties(height=250).configure_view(strokeWidth=0)
            st.altair_chart(c, use_container_width=True)
            
            if st.button(f"🔔 연주하기 ({title})", key=f"btn_{key_suffix}"):
                with st.spinner("캐롤 생성 중..."):
                    audio = compose_carol(current_nums, bpm=110)
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- Main Page ---
st.markdown('<div class="holiday-title">White Math Carol</div>', unsafe_allow_html=True)
st.markdown('<div class="holiday-sub">중학교 수학 교육과정 × 크리스마스 멜로디</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["1학년 (도형)", "2학년 (수)", "3학년 (무리수)", "나만의 숫자"])

with tab1:
    render_tab_content(
        "t1", "badge-1", "중1 - 도형의 성질", 
        "원주율 (Pi, π)", 
        """
        <b>3.141592...</b><br>
        원은 완벽한 대칭을 가진 도형입니다. 원주율은 끝없이 이어지는 
        비순환 무한소수로, 예측 불가능한 멜로디를 만들어냅니다.
        """,
        "314159265358979323846264338327950288419716939937510"
    )

with tab2:
    render_tab_content(
        "t2", "badge-2", "중2 - 유리수와 순환소수", 
        "순환소수 (1/7)", 
        """
        <b>0.142857...</b><br>
        유리수 중에는 같은 숫자가 반복되는 순환소수가 있습니다.
        반복되는 리듬은 캐롤의 후렴구처럼 즐거운 패턴을 만듭니다.
        """,
        "142857142857142857142857142857142857142857"
    )

with tab3:
    render_tab_content(
        "t3", "badge-3", "중3 - 제곱근과 실수", 
        "루트 2 (√2)", 
        """
        <b>1.414213...</b><br>
        제곱해서 2가 되는 수, 무리수입니다.
        한 변이 1인 정사각형의 대각선 길이와 같습니다.
        무리수의 깊이 있는 울림을 감상해보세요.
        """,
        "141421356237309504880168872420969807856967187537694"
    )

with tab4:
    render_tab_content(
        "t4", "badge-c", "자유 학기제", 
        "나만의 숫자 캐롤", 
        """
        <b>Make Your Own Carol</b><br>
        여러분의 생일, 기념일, 혹은 좋아하는 숫자를 입력해보세요.
        수학적 규칙에 따라 세상에 하나뿐인 캐롤로 변환됩니다.
        """,
        "12251225",
        is_custom=True
    )

st.markdown("<br><br><div style='text-align:center; color:#ADB5BD; font-size:0.8rem;'>Designed for Math Education</div>", unsafe_allow_html=True)
