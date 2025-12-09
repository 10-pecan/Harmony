import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Masterpiece", page_icon="❄️", layout="wide")

# --- 2. 🎨 Pure CSS Design (이미지 없이 코드로만 구현) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;500;700;900&family=Cinzel:wght@700&display=swap');
    
    /* [전체 배경: 움직이는 그라데이션 오로라] */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Pretendard', sans-serif !important;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* [배경을 덮는 화이트 글래스 레이어] */
    .stApp::before {
        content: "";
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(255, 255, 255, 0.85); /* 흰색 반투명 */
        z-index: -1;
    }

    /* [눈 내리는 효과] */
    .snowflake { position: fixed; top: -10px; z-index: 99; color: #fff; font-size: 1.2em; text-shadow: 0 0 5px rgba(0,0,0,0.1); animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [타이틀 디자인] */
    .main-title {
        font-family: 'Cinzel', serif; font-size: 4.5rem; font-weight: 800;
        text-align: center; color: #c0392b; margin-top: 30px;
        text-shadow: 0 10px 30px rgba(192, 57, 43, 0.2); letter-spacing: -1px;
    }
    .sub-title {
        text-align: center; color: #555; font-size: 1.1rem; letter-spacing: 2px;
        text-transform: uppercase; margin-bottom: 50px; font-weight: 600;
    }

    /* [카드 디자인: 애플 스타일 프로스트 글래스] */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 24px; padding: 40px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px; transition: transform 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-5px); }

    /* [탭 스타일] */
    div[data-baseweb="tab-list"] { gap: 15px; margin-bottom: 30px; justify-content: center; }
    button[data-baseweb="tab"] {
        background: rgba(255,255,255,0.5) !important; border: 1px solid #ddd !important; border-radius: 30px !important;
        padding: 10px 25px !important; color: #777 !important; font-weight: 600 !important; font-size: 1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: #c0392b !important; color: #fff !important; border-color: #c0392b !important;
        box-shadow: 0 5px 15px rgba(192, 57, 43, 0.3) !important;
    }

    /* [재생 버튼] */
    .play-btn { width: 100%; }
    .stButton>button {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%) !important;
        color: #fff !important; border: none; height: 65px; border-radius: 16px;
        font-size: 1.4rem; font-weight: 700; width: 100%;
        box-shadow: 0 10px 25px rgba(192, 57, 43, 0.3); transition: all 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 15px 35px rgba(192, 57, 43, 0.4); }

    /* [교육용 뱃지] */
    .badge {
        display: inline-block; padding: 6px 14px; border-radius: 20px;
        font-size: 0.9rem; font-weight: 700; color: #fff; margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .b-red { background: #e74c3c; }
    .b-green { background: #27ae60; }
    .b-gold { background: #f1c40f; color: #333; }
    .b-purple { background: #8e44ad; }

    /* [설명 텍스트] */
    .desc-text { color: #444; line-height: 1.7; font-size: 1.05rem; }
    .desc-text b { color: #c0392b; }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(8, 20)}s; animation-delay:{np.random.uniform(0, 10)}s;">❄</div>' for _ in range(40)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (안정화된 합성 로직) ---

def generate_wave(freq, duration, type="bell"):
    sr = 44100
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if type == "bell": # 밝은 벨소리
        return 0.6*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)*np.exp(-2*t) + 0.1*np.sin(2*np.pi*freq*4*t)
    elif type == "strings": # 풍성한 스트링
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*0.5*t)
    elif type == "choir": # 웅장한 코러스
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*0.998*t) + 0.3*np.sin(2*np.pi*freq*1.002*t)
    elif type == "sleigh": # 썰매 벨
        noise = np.random.uniform(-1, 1, len(t))
        return 0.1 * noise * np.sin(2*np.pi*3000*t) * np.exp(-15*t)
    return np.zeros(num_samples)

# [핵심 Fix] 길이 강제 맞춤 (에러 방지)
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

# 작곡 엔진 (스타일별)
def compose_music(nums, bpm, style):
    # 안전한 스케일 (인덱스 에러 방지용으로 길게)
    if style == "joyful": # C Major
        scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    elif style == "waltz": # D Major
        scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    else: # A Minor (Holy)
        scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

    beat_sec = 60.0 / bpm
    full_track = []

    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        base_freq = scale[idx % len(scale)]
        
        # 스타일별 프레이즈 생성
        melody_waves = []
        notes = [] # (freq, duration_multiplier)

        if style == "joyful": # 셔플 리듬
            if idx % 2 == 0: notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)]
            else: notes = [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        elif style == "waltz": # 3/4박자
            notes = [(base_freq, 1.0), (base_freq*1.25, 1.0), (base_freq*1.5, 1.0)]
        else: # 4박자 롱노트
            notes = [(base_freq, 4.0)]

        # 멜로디 합성
        for f, d in notes:
            dur = d * beat_sec
            w = generate_wave(f, dur, "bell" if style != "holy" else "choir")
            w = apply_envelope(w, dur, "short" if style != "holy" else "long")
            melody_waves.append(w)
        
        melody = np.concatenate(melody_waves)
        total_len = len(melody)

        # 반주 추가 (길이 강제 보정)
        pad_freq = base_freq * 0.5
        pad = generate_wave(pad_freq, total_len/44100, "strings")
        pad = match_len(pad, total_len) # [Safe Fix]
        pad = apply_envelope(pad, total_len/44100, "long") * 0.3
        
        sleigh = generate_wave(0, total_len/44100, "sleigh")
        sleigh = match_len(sleigh, total_len) * 0.3 if style == "joyful" else np.zeros(total_len)

        full_track.append(melody + pad + sleigh)

    if not full_track: return None
    
    # 전체 합치기 & 리버브
    full = np.concatenate(full_track)
    delay = int(44100 * 0.4)
    res = np.zeros(len(full) + delay)
    res[:len(full)] += full
    res[delay:] += full * 0.4
    
    m = np.max(np.abs(res))
    return res / m * 0.95 if m > 0 else res

# --- 4. Main UI ---

st.markdown('<div class="main-title">WHITE WINTER CAROL</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Mathematics × Christmas Symphony</div>', unsafe_allow_html=True)

# 탭 구성 (독립적인 작동을 위해 로직 분리 확인)
tab1, tab2, tab3, tab4 = st.tabs(["1학년 (도형)", "2학년 (수)", "3학년 (무리수)", "나만의 숫자"])

def render_tab(key_prefix, badge_cls, badge_text, title, desc, default_nums, style):
    c1, c2 = st.columns([1, 1], gap="large")
    
    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <span class="badge {badge_cls}">{badge_text}</span>
            <h2 style="color:#2c3e50; margin:10px 0;">{title}</h2>
            <div class="desc-text">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 커스텀 입력창 (4번째 탭용)
        final_nums = default_nums
        if key_prefix == "t4":
            user_input = st.text_input("숫자를 입력하세요 (예: 1225)", value="", key=f"in_{key_prefix}")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))

    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        # 트리 비주얼라이저 (음계에 따라 배치)
        if final_nums:
            digits = [int(d) for d in final_nums[:30] if d != '0']
            tree_data = []
            max_width = 10
            height_scale = 1.5
            
            for i, d in enumerate(digits):
                level = d * height_scale
                spread = (10 - d) * max_width / 10 
                pos = spread * (1 if i % 2 == 0 else -1) * np.random.uniform(0.3, 1.0)
                tree_data.append({'Level': level, 'Pos': pos, 'Note': d})
            
            df = pd.DataFrame(tree_data)
            
            # 탭별 색상 테마
            color_map = {'t1': 'reds', 't2': 'greens', 't3': 'oranges', 't4': 'purples'}
            
            c = alt.Chart(df).mark_circle(size=350, opacity=0.9).encode(
                x=alt.X('Pos', axis=None), y=alt.Y('Level', axis=None),
                color=alt.Color('Note', scale=alt.Scale(scheme=color_map[key_prefix]), legend=None),
                tooltip=['Note']
            ).properties(height=300).configure_view(strokeWidth=0)
            
            st.altair_chart(c, use_container_width=True)
            st.caption("▲ 음계의 높낮이로 장식된 크리스마스 트리")

        # 재생 버튼
        if st.button(f"🔔 캐롤 재생 (Play)", key=f"btn_{key_prefix}"):
            with st.spinner("캐롤 편곡 중..."):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
                else:
                    st.error("연주할 숫자가 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)

# 탭 내용 렌더링
with tab1:
    render_tab("t1", "b-red", "중1 - 도형의 성질", "원주율 (Pi) 징글벨", 
               "<b>3.141592...</b><br>원은 완벽한 대칭을 가진 도형입니다. 원주율의 불규칙한 숫자들이 <b>경쾌한 셔플 리듬</b>과 만나 썰매를 타는 듯한 신나는 곡이 됩니다.", 
               "314159265358979323846264338327950288419716939937510", "joyful")

with tab2:
    render_tab("t2", "b-green", "중2 - 순환소수", "순환소수 왈츠", 
               "<b>0.142857...</b><br>같은 구간이 반복되는 순환소수(1/7)입니다. 이 규칙적인 패턴은 <b>우아한 3박자 왈츠</b>와 어우러져 무도회장 같은 분위기를 만듭니다.", 
               "142857142857142857142857142857142857142857", "waltz")

with tab3:
    render_tab("t3", "b-gold", "중3 - 무리수", "루트2 홀리 나이트", 
               "<b>1.414213...</b><br>정사각형의 대각선 길이인 무리수입니다. 깊고 신비로운 숫자의 배열이 <b>웅장한 합창(Choir)</b>과 만나 성스러운 겨울밤을 연출합니다.", 
               "141421356237309504880168872420969807856967187537694", "holy")

with tab4:
    render_tab("t4", "b-purple", "자유학기제", "나만의 숫자 캐롤", 
               "<b>Make Your Own Music</b><br>생일, 기념일, 전화번호 등 당신의 소중한 숫자를 입력해보세요. 세상에 하나뿐인 캐롤로 변환해 드립니다.", 
               "12251225", "joyful")

st.markdown("<br><div style='text-align:center; color:#bbb;'>Designed for Joyful Math Education 🎁</div>", unsafe_allow_html=True)
