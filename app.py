import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Ultimate Fixed", page_icon="🎄", layout="wide")

# --- 2. 🎨 White Luxury Design & Fixed Tab UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700;900&family=Cinzel:wght@700&display=swap');
    
    /* [전체 배경] */
    .stApp {
        background-color: #FFFFFF !important;
        background-image: radial-gradient(#ffffff 0%, #f8f9fa 100%);
        color: #2d3436 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* [눈 효과] */
    .snowflake { position: fixed; top: -10px; z-index: 99; color: #dfe6e9; font-size: 1.2em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [타이틀] */
    .main-title {
        font-family: 'Cinzel', serif; font-size: 4rem; color: #c0392b; text-align: center;
        text-shadow: 2px 2px 0px #badc58; margin-top: 20px;
    }
    .sub-title { text-align: center; color: #636e72; margin-bottom: 40px; letter-spacing: 1px; }

    /* [카드 스타일] */
    .music-card {
        background: rgba(255, 255, 255, 1.0);
        border: 1px solid #eee; border-radius: 20px;
        padding: 35px; box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        margin-bottom: 25px; height: 100%;
    }

    /* [탭 스타일 개선 - 가독성 확보] */
    div[data-baseweb="tab-list"] { gap: 20px; margin-bottom: 20px; }
    button[data-baseweb="tab"] {
        font-weight: bold; font-size: 1.1rem; color: #636e72 !important; /* 기본: 진한 회색 */
        border: none !important; background: transparent !important;
    }
    /* 선택된 탭 강조 */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #c0392b !important; /* 선택: 빨간색 */
        border-bottom: 4px solid #c0392b !important;
    }

    /* [버튼 스타일] */
    .stButton>button {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%) !important;
        color: white !important; border-radius: 15px; height: 65px; font-size: 1.3rem; font-weight: 800; border: none;
        box-shadow: 0 8px 20px rgba(192, 57, 43, 0.3); transition: 0.3s; width: 100%;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 12px 25px rgba(192, 57, 43, 0.4); }

    /* [교육용 뱃지 & 텍스트] */
    .badge { padding: 6px 14px; border-radius: 20px; font-size: 0.9rem; font-weight: bold; color: white; display: inline-block; margin-bottom: 15px; }
    .b-1 { background-color: #e74c3c; } /* Red */
    .b-2 { background-color: #27ae60; } /* Green */
    .b-3 { background-color: #f1c40f; color: #333; } /* Gold */
    .desc-box { font-size: 1.05rem; line-height: 1.7; color: #555; background: #f9f9f9; padding: 20px; border-radius: 15px; border-left: 5px solid #c0392b; }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(8, 15)}s; animation-delay:{np.random.uniform(0, 5)}s;">❄</div>' for _ in range(40)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (버그 수정됨) ---

def get_sine(freq, duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    return np.sin(2 * np.pi * freq * t)

def apply_envelope(wave, duration, type="plucked"):
    length = len(wave)
    if type == "plucked":
        env = np.exp(np.linspace(0, -4, length))
    elif type == "pad":
        att = int(length*0.2); rel = int(length*0.4)
        env = np.concatenate([np.linspace(0,1,att), np.full(length-att-rel,1.0), np.linspace(1,0,rel)])
    if len(env) != length: env = np.resize(env, length)
    return wave * env

# 악기 신디사이저
def synth_bell(freq, duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    mod = np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-3*t)
    car = np.sin(2 * np.pi * freq * t + 2.0 * mod) 
    return apply_envelope(car, duration, "plucked")

def synth_choir(freq, duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    w = 0.4*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*(freq*1.01)*t) + 0.3*np.sin(2*np.pi*(freq*0.99)*t)
    return apply_envelope(w, duration, "pad")

def synth_strings(freq, duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    w = 0.5*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t) + 0.2*np.sin(2*np.pi*freq*3*t)
    return apply_envelope(w, duration, "pad")

def synth_sleigh(duration):
    t = np.linspace(0, duration, int(44100 * duration), False)
    noise = np.random.uniform(-1, 1, len(t))
    return noise * np.sin(2*np.pi*3000*t) * np.exp(-15*t) * 0.3

# --- 스타일별 작곡 엔진 (스케일 확장 및 안전장치 추가) ---

def compose_joyful(nums, bpm):
    """중1: 경쾌한 셔플 (C Major Scale - 10음으로 확장)"""
    scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    beat = 60/bpm
    track = []
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        freq = scale[idx % len(scale)] # 안전한 인덱싱
        
        dur = [beat*0.75, beat*0.25, beat] 
        melody = np.concatenate([synth_bell(freq, dur[0]), synth_bell(freq, dur[1]), synth_bell(freq*1.25, dur[2])])
        bass_len = len(melody)
        bass = synth_strings(freq*0.5, bass_len/44100) * 0.5
        sleigh = synth_sleigh(bass_len/44100)
        track.append(melody + bass + sleigh)
    return np.concatenate(track) if track else None

def compose_waltz(nums, bpm):
    """중2: 우아한 왈츠 (D Major Scale - 10음으로 확장)"""
    # [FIX] 스케일을 10개로 늘려 IndexError 방지
    scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    beat = 60/bpm
    track = []
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        base = scale[idx % len(scale)]
        
        part1 = synth_strings(base*0.5, beat)
        chord_note = scale[(idx+2) % len(scale)] # 안전한 인덱싱
        part2 = synth_bell(chord_note, beat) * 0.6
        part3 = synth_bell(chord_note, beat) * 0.6
        measure = np.concatenate([part1, part2, part3])
        melody_layer = synth_choir(base * 2, 3*beat) * 0.4
        # 길이 맞추기
        min_len = min(len(measure), len(melody_layer))
        track.append(measure[:min_len] + melody_layer[:min_len])
    return np.concatenate(track) if track else None

def compose_holy(nums, bpm):
    """중3: 웅장한 코러스 (A Minor Scale - 10음으로 확장)"""
    # [FIX] 스케일을 10개로 늘려 IndexError 방지
    scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    beat = 60/(bpm*0.7)
    track = []
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        freq = scale[idx % len(scale)]
        
        duration = 4 * beat
        choir = synth_choir(freq, duration)
        arp1 = synth_bell(freq * 2, duration) * 0.3
        arp2 = synth_bell(freq * 3, duration) * 0.2
        bass = synth_strings(freq * 0.25, duration) * 0.6
        track.append(choir + arp1 + arp2 + bass)
    return np.concatenate(track) if track else None

def apply_reverb(audio):
    delay = int(44100 * 0.4)
    res = np.zeros(len(audio) + delay)
    res[:len(audio)] += audio
    res[delay:] += audio * 0.4
    return res

# --- 4. UI 렌더링 함수 (트리 비주얼 적용) ---

def render_content(key, style, title, badge, desc, default_nums):
    c1, c2 = st.columns([1, 1], gap="large")
    
    with c1:
        st.markdown(f'<div class="music-card">', unsafe_allow_html=True)
        st.markdown(f'{badge}', unsafe_allow_html=True)
        st.markdown(f"## {title}")
        st.markdown(f'<div class="desc-box">{desc}</div>', unsafe_allow_html=True)
        
        user_in = st.text_input("숫자 입력 (자유롭게 바꿔보세요!)", value=default_nums, key=f"in_{key}")
        nums = "".join(filter(str.isdigit, user_in))
        
        style_desc = ""
        if style == "joyful": style_desc = "🔔 <b>Joyful:</b> 징글벨처럼 신나는 셔플 리듬"
        elif style == "waltz": style_desc = "💃 <b>Waltz:</b> 우아하고 몽환적인 3박자 춤곡"
        elif style == "holy": style_desc = "👼 <b>Holy:</b> 웅장하고 성스러운 대성당의 합창"
        st.caption(style_desc, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="music-card">', unsafe_allow_html=True)
        
        # [VISUAL FIX] 요청하신 트리(피라미드) 구조 비주얼라이저 복구
        colors = {'joyful': 'reds', 'waltz': 'greens', 'holy': 'oranges'}
        if nums:
            digits = [int(d) for d in nums[:20] if d != '0']
            tree_data = []
            level, count = 1, 0
            for d in digits:
                # 피라미드 형태로 좌표 계산
                tree_data.append({'Level': -level, 'Pos': count - (level-1)/2, 'Note': d})
                count += 1
                if count >= level: level += 1; count = 0
            
            df = pd.DataFrame(tree_data)
            
            chart = alt.Chart(df).mark_circle(size=400, opacity=0.8).encode(
                x=alt.X('Pos', axis=None),
                y=alt.Y('Level', axis=None),
                color=alt.Color('Note', scale=alt.Scale(scheme=colors[style]), legend=None),
                tooltip=['Note']
            ).properties(height=250).configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)
            st.caption("▲ 숫자들이 모여 크리스마스 트리를 만들었어요!")
        
        if st.button(f"🎼 Play {title}", key=f"btn_{key}"):
            with st.spinner("캐롤 편곡 중..."):
                try:
                    if style == "joyful": audio = compose_joyful(nums, 120)
                    elif style == "waltz": audio = compose_waltz(nums, 100)
                    elif style == "holy": audio = compose_holy(nums, 90)
                    
                    if audio is not None and len(audio) > 0:
                        final = apply_reverb(audio)
                        m = np.max(np.abs(final))
                        if m > 0: final = final / m * 0.9
                        virtual_file = io.BytesIO()
                        write(virtual_file, 44100, (final * 32767).astype(np.int16))
                        st.audio(virtual_file, format='audio/wav')
                    else:
                        st.warning("연주할 숫자가 충분하지 않습니다.")
                except Exception as e:
                    st.error(f"연주 중 오류가 발생했습니다: {e}")
                    
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main UI ---

st.markdown('<div class="main-title">CHRISTMAS MATH CAROL</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">중학교 수학으로 연주하는 3가지 색깔의 캐롤</div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🔴 1학년 (Joyful)", "🟢 2학년 (Waltz)", "🟡 3학년 (Holy)"])

with t1:
    render_content(
        "t1", "joyful", "원주율 (Pi) 징글벨", 
        '<span class="badge b-1">중1 도형</span>',
        """
        <b>3.141592...</b> 원주율은 끝없이 이어지는 비순환 소수입니다.
        규칙 없는 숫자들이 만드는 예측 불가능한 멜로디가
        마치 썰매를 타고 달리는 듯한 신나는 캐롤이 됩니다! 🛷
        """,
        "314159265358979323846264338327950288419716939937510"
    )

with t2:
    render_content(
        "t2", "waltz", "순환소수 왈츠", 
        '<span class="badge b-2">중2 유리수</span>',
        """
        <b>0.142857...</b> 순환소수는 일정한 마디가 반복되는 수입니다.
        이 규칙적인 반복은 우아한 3박자 왈츠 리듬(쿵-짝-짝)과 만나
        몽환적인 춤곡으로 다시 태어납니다. 💃
        """,
        "142857142857142857142857142857142857142857"
    )

with t3:
    render_content(
        "t3", "holy", "루트2 판타지", 
        '<span class="badge b-3">중3 무리수</span>',
        """
        <b>1.414213...</b> 정사각형의 대각선 길이, 무리수 루트2.
        깊고 비밀스러운 이 숫자는 웅장한 합창(Choir) 사운드와 어우러져
        성스럽고 신비로운 겨울밤의 분위기를 연출합니다. 🕯️
        """,
        "141421356237309504880168872420969807856967187537694"
    )

st.markdown("<br><hr><div style='text-align:center; color:#b2bec3;'>Designed for Joyful Math Education 🎁</div>", unsafe_allow_html=True)
