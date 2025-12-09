import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Ultimate", page_icon="🎄", layout="wide")

# --- 2. 🎨 White Luxury Design ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700;900&family=Cinzel:wght@700&display=swap');
    
    .stApp {
        background-color: #FFFFFF !important;
        background-image: radial-gradient(#ffffff 0%, #f1f2f6 100%);
        color: #2d3436 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    .snowflake { position: fixed; top: -10px; z-index: 99; color: #dfe6e9; font-size: 1.2em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    .main-title {
        font-family: 'Cinzel', serif; font-size: 4rem; color: #c0392b; text-align: center;
        text-shadow: 2px 2px 0px #badc58; margin-top: 20px;
    }
    .sub-title { text-align: center; color: #636e72; margin-bottom: 40px; letter-spacing: 1px; }

    /* 카드 스타일 */
    .music-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #dfe6e9; border-radius: 20px;
        padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* 탭 스타일 */
    button[data-baseweb="tab"] { font-weight: bold; font-size: 1.1rem; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #c0392b !important; border-bottom: 3px solid #c0392b !important; }

    /* 버튼 스타일 */
    .stButton>button {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%) !important;
        color: white !important; border-radius: 15px; height: 60px; font-size: 1.2rem; font-weight: 800; border: none;
        box-shadow: 0 5px 15px rgba(192, 57, 43, 0.3); transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); }

    /* 교육용 뱃지 */
    .badge { padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; color: white; display: inline-block; margin-bottom: 10px; }
    .b-1 { background-color: #e74c3c; } /* Red */
    .b-2 { background-color: #27ae60; } /* Green */
    .b-3 { background-color: #f1c40f; color: #333; } /* Gold */
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(5, 15)}s; animation-delay:{np.random.uniform(0, 5)}s;">❄</div>' for _ in range(30)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Advanced Audio Engine (3가지 스타일) ---

def get_sine(freq, duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    return np.sin(2 * np.pi * freq * t)

def apply_envelope(wave, duration, type="plucked"):
    length = len(wave)
    if type == "plucked": # 띵~ (벨소리)
        env = np.exp(np.linspace(0, -4, length))
    elif type == "pad": # 웅~ (코러스/현악기)
        att = int(length*0.2); rel = int(length*0.4)
        env = np.concatenate([np.linspace(0,1,att), np.full(length-att-rel,1.0), np.linspace(1,0,rel)])
    
    if len(env) != length: env = np.resize(env, length)
    return wave * env

# [악기 1] FM Bell (영롱한 종소리)
def synth_bell(freq, duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    # FM Synthesis: Modulator가 Carrier의 주파수를 흔듦
    modulator = np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-3*t)
    carrier = np.sin(2 * np.pi * freq * t + 2.0 * modulator) 
    return apply_envelope(carrier, duration, "plucked")

# [악기 2] Choir (천상의 코러스)
def synth_choir(freq, duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    # 여러 주파수를 미세하게 겹침 (Detune)
    w = 0.4*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*(freq*1.01)*t) + 0.3*np.sin(2*np.pi*(freq*0.99)*t)
    return apply_envelope(w, duration, "pad")

# [악기 3] Strings (따뜻한 현악기)
def synth_strings(freq, duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    # 톱니파 비슷하게 배음 추가
    w = 0.5*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t) + 0.2*np.sin(2*np.pi*freq*3*t)
    return apply_envelope(w, duration, "pad")

# [악기 4] Sleigh Bells (썰매 방울)
def synth_sleigh(duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    noise = np.random.uniform(-1, 1, len(t))
    return noise * np.sin(2*np.pi*3000*t) * np.exp(-15*t) * 0.3

# --- 스타일별 작곡 엔진 ---

def compose_joyful(nums, bpm):
    """중1 원주율: 경쾌한 4/4박자 셔플 (징글벨 스타일)"""
    scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25] # C Major
    beat = 60/bpm
    track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        freq = scale[idx % 8]
        
        # 리듬: 딴.따.단 (Shuffle)
        durations = [beat*0.75, beat*0.25, beat] 
        
        # 1. Melody (Bell)
        melody = np.concatenate([
            synth_bell(freq, durations[0]),
            synth_bell(freq, durations[1]),
            synth_bell(freq*1.25, durations[2]) # 마지막 음은 살짝 높게
        ])
        
        # 2. Bass (Tuba 느낌)
        bass_len = len(melody)
        bass = synth_strings(freq*0.5, bass_len/44100) * 0.5
        
        # 3. Sleigh Bell (계속 흔듬)
        sleigh = synth_sleigh(bass_len/44100)
        
        track.append(melody + bass + sleigh)
        
    return np.concatenate(track) if track else None

def compose_waltz(nums, bpm):
    """중2 순환소수: 우아한 3/4박자 왈츠 (실버벨 스타일)"""
    scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33] # D Major
    beat = 60/bpm
    track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        base = scale[idx % 8]
        
        # 왈츠 리듬: 쿵-짝-짝 (1박 + 1박 + 1박)
        
        # 1. Bass (쿵) - Piano Left Hand
        part1 = synth_strings(base*0.5, beat) # 베이스 음
        
        # 2. Chord (짝) - Piano Right Hand
        chord_note = scale[(idx+2)%8] # 3도 위 화음
        part2 = synth_bell(chord_note, beat) * 0.6
        part3 = synth_bell(chord_note, beat) * 0.6
        
        # 합치기 (순차적으로)
        measure = np.concatenate([part1, part2, part3])
        
        # 3. Melody (위에 얹기) - 3박자 동안 길게 끄는 코러스
        melody_layer = synth_choir(base * 2, 3*beat) * 0.4
        
        track.append(measure + melody_layer)
        
    return np.concatenate(track) if track else None

def compose_holy(nums, bpm):
    """중3 무리수: 웅장하고 느린 4/4박자 (고요한 밤 스타일)"""
    scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00] # A Minor (신비로움)
    beat = 60/(bpm*0.7) # 느리게
    track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        freq = scale[idx % 8]
        
        # 1. Choir (합창) - 길게 4박자
        duration = 4 * beat
        choir = synth_choir(freq, duration)
        
        # 2. Arpeggio (하프 소리) - 띠리링~
        arp1 = synth_bell(freq * 2, duration) * 0.3
        arp2 = synth_bell(freq * 3, duration) * 0.2
        
        # 3. Low Strings (웅장한 베이스)
        bass = synth_strings(freq * 0.25, duration) * 0.6
        
        track.append(choir + arp1 + bass)
        
    return np.concatenate(track) if track else None

def apply_reverb(audio):
    delay = int(44100 * 0.4)
    res = np.zeros(len(audio) + delay)
    res[:len(audio)] += audio
    res[delay:] += audio * 0.4 # Echo
    return res

# --- 4. 탭별 렌더링 함수 ---

def render_content(key, style, title, badge, desc, default_nums):
    c1, c2 = st.columns([1.2, 1], gap="large")
    
    with c1:
        st.markdown(f'<div class="music-card">', unsafe_allow_html=True)
        st.markdown(f'{badge}', unsafe_allow_html=True)
        st.markdown(f"## {title}")
        st.markdown(desc, unsafe_allow_html=True)
        
        user_in = st.text_input("숫자 입력 (자유롭게 바꿔보세요!)", value=default_nums, key=f"in_{key}")
        nums = "".join(filter(str.isdigit, user_in))
        
        # 스타일별 설명
        style_desc = ""
        if style == "joyful": style_desc = "🔔 <b>Joyful Style:</b> 징글벨처럼 경쾌한 4/4박자 셔플 리듬"
        elif style == "waltz": style_desc = "💃 <b>Waltz Style:</b> 춤추는 듯한 3/4박자 (쿵-짝-짝)"
        elif style == "holy": style_desc = "👼 <b>Holy Style:</b> 대성당의 합창처럼 웅장하고 느린 선율"
        
        st.caption(style_desc, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="music-card">', unsafe_allow_html=True)
        
        # 시각화 (스타일별 색상)
        colors = {'joyful': 'reds', 'waltz': 'greens', 'holy': 'oranges'}
        if nums:
            digits = [int(d) for d in nums[:15] if d != '0']
            df = pd.DataFrame({'idx': range(len(digits)), 'val': digits})
            
            # 파형 차트
            chart = alt.Chart(df).mark_bar(cornerRadius=5).encode(
                x=alt.X('idx', axis=None),
                y=alt.Y('val', axis=None, scale=alt.Scale(domain=[0, 10])),
                color=alt.Color('val', scale=alt.Scale(scheme=colors[style]), legend=None)
            ).properties(height=200).configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)
        
        # 재생 버튼
        if st.button(f"🎼 Play {title}", key=f"btn_{key}"):
            with st.spinner("캐롤 편곡 중..."):
                if style == "joyful": audio = compose_joyful(nums, 120)
                elif style == "waltz": audio = compose_waltz(nums, 100)
                elif style == "holy": audio = compose_holy(nums, 90)
                
                if audio is not None:
                    final = apply_reverb(audio)
                    # Normalize
                    m = np.max(np.abs(final))
                    if m > 0: final = final / m * 0.9
                    
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (final * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
                else:
                    st.error("숫자가 유효하지 않습니다.")
                    
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main UI ---

st.markdown('<div class="main-title">CHRISTMAS MATH CAROL</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">중학교 수학으로 연주하는 3가지 스타일의 캐롤</div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🔴 1학년 (Joyful)", "🟢 2학년 (Waltz)", "🟡 3학년 (Holy)"])

with t1:
    render_content(
        "t1", "joyful", "원주율 (Pi) 징글벨", 
        '<span class="badge b-1">중1 도형</span>',
        """
        <b>3.141592...</b><br>
        원주율은 규칙 없이 영원히 이어지는 숫자입니다.<br>
        이 불규칙함이 <b>경쾌한 셔플 리듬</b>을 만나면<br>
        마치 썰매를 타고 달리는 듯한 신나는 캐롤이 됩니다! 🛷
        """,
        "314159265358979323846264338327950288419716939937510"
    )

with t2:
    render_content(
        "t2", "waltz", "순환소수 왈츠", 
        '<span class="badge b-2">중2 유리수</span>',
        """
        <b>0.142857 142857...</b><br>
        순환소수는 일정한 마디가 계속 반복되는 수입니다.<br>
        이 반복성은 <b>3박자 왈츠 리듬(쿵-짝-짝)</b>과 완벽하게 어울려<br>
        우아하고 몽환적인 춤곡을 만들어냅니다. 💃
        """,
        "142857142857142857142857142857142857142857"
    )

with t3:
    render_content(
        "t3", "holy", "무리수 루트2 판타지", 
        '<span class="badge b-3">중3 제곱근</span>',
        """
        <b>1.414213...</b><br>
        인류가 처음 발견한 무리수, 루트2.<br>
        이 깊고 신비로운 숫자는 <b>웅장한 합창(Choir)</b>과 만나<br>
        고요한 겨울밤의 성스러운 분위기를 연출합니다. 🕯️
        """,
        "141421356237309504880168872420969807856967187537694"
    )

st.markdown("<br><hr><div style='text-align:center; color:#b2bec3;'>Designed for Joyful Math Education 🎁</div>", unsafe_allow_html=True)
