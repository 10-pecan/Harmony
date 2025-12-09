import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol: White Winter", page_icon="❄️", layout="wide")

# --- 2. 🎨 White Luxury Design (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700;900&family=Playfair+Display:ital,wght@1,700&display=swap');
    
    /* [전체 배경] 깨끗한 스노우 화이트 */
    .stApp {
        background-color: #F8F9FA !important;
        background-image: radial-gradient(#ffffff 0%, #e6e9f0 100%);
        color: #2C3E50 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* [눈 내리는 효과 - 회색 눈송이로 은은하게] */
    .snowflake {
        position: fixed; top: -10px; z-index: 0;
        color: #D1D5DB; font-size: 1.2em; opacity: 0.6;
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { transform: translateY(-10vh); }
        100% { transform: translateY(110vh); }
    }

    /* [타이틀] 잡지 표지 같은 스타일 */
    .holiday-title {
        font-family: 'Playfair Display', serif;
        font-size: 5rem; font-weight: 900; font-style: italic;
        text-align: center; color: #D6336C; /* 루비 레드 */
        margin-top: 30px; letter-spacing: -2px;
        text-shadow: 2px 2px 0px #FFF, 4px 4px 0px #E9ECEF;
    }
    .holiday-sub {
        text-align: center; color: #868E96; font-size: 1.1rem;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 50px;
    }

    /* [카드 디자인] 애플 스타일의 깔끔한 박스 */
    .snow-card {
        background: #FFFFFF;
        border-radius: 24px;
        border: 1px solid #FFFFFF;
        box-shadow: 0 10px 40px rgba(0,0,0,0.05); /* 아주 부드러운 그림자 */
        padding: 40px; margin-bottom: 25px;
        transition: transform 0.3s ease;
    }
    .snow-card:hover { transform: translateY(-5px); }

    /* [수학 교육 뱃지] */
    .grade-badge {
        display: inline-block; padding: 6px 14px;
        border-radius: 30px; font-weight: 700; font-size: 0.85rem;
        margin-bottom: 15px;
    }
    .badge-red { background: #FFE3E3; color: #C92A2A; } /* 중1 */
    .badge-green { background: #D3F9D8; color: #2B8A3E; } /* 중2 */
    .badge-gold { background: #FFF3BF; color: #F08C00; } /* 중3 */

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { background: transparent !important; border-bottom: 2px solid #E9ECEF; }
    button[data-baseweb="tab"] {
        background: transparent !important; border: none !important;
        color: #ADB5BD !important; font-size: 1.1rem !important; font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #D6336C !important; /* 선택된 탭 레드 */
        border-bottom: 3px solid #D6336C !important;
    }

    /* [재생 버튼] */
    .stButton>button {
        background: linear-gradient(135deg, #D6336C 0%, #A61E4D 100%) !important;
        color: #FFF !important; border: none; height: 70px; border-radius: 16px;
        font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700;
        box-shadow: 0 10px 30px rgba(214, 51, 108, 0.3);
        width: 100%; transition: all 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 15px 40px rgba(214, 51, 108, 0.4); }

    /* [입력창] */
    .stTextInput input {
        background: #F1F3F5 !important; border: none !important; color: #343A40 !important;
        text-align: center; font-size: 1.2rem;
    }
    
    /* [설명 텍스트] */
    h3 { color: #343A40 !important; font-family: 'Noto Sans KR', sans-serif; font-weight: 700; }
    p { color: #495057; line-height: 1.7; font-size: 1rem; }
    b { color: #D6336C; }
</style>
""", unsafe_allow_html=True)

# --- 3. ❄️ 눈 내리는 JS ---
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(10, 20)}s; animation-delay:{np.random.uniform(0, 10)}s;">❄</div>' for _ in range(30)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 4. 🔔 Rich Carol Engine (Rhythm & Sleigh Bells) ---

def generate_wave(freq, duration, type="bell"):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), False)
    
    if type == "bell": # 밝은 벨소리
        return 0.6*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)*np.exp(-2*t) + 0.1*np.sin(2*np.pi*freq*4*t)
    elif type == "strings": # 풍성한 배경음
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*0.5*t)
    elif type == "sleigh": # 썰매 방울 (고음역 노이즈)
        noise = np.random.uniform(-1, 1, len(t))
        return 0.1 * noise * np.sin(2*np.pi*2000*t) * np.exp(-10*t) # 짤랑!
    return np.zeros_like(t)

def apply_envelope(wave, duration, type="short"):
    length = len(wave)
    if type == "short": # 통통 튀는 느낌
        env = np.exp(np.linspace(0, -5, length))
    else: # 길게 깔리는 느낌
        att = int(length*0.2); rel = int(length*0.3)
        env = np.concatenate([np.linspace(0,1,att), np.full(length-att-rel,1.0), np.linspace(1,0,rel)])
    
    if len(env) != length: env = np.resize(env, length)
    return wave * env

def create_carol_phrase(digit, bpm):
    # C Major Scale (Happy Christmas)
    scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    
    # 셔플 리듬 (Swing Feel) - 딴.따.단
    beat_sec = 60.0 / bpm
    idx = int(digit) if digit.isdigit() else 0
    base_freq = scale[idx % len(scale)]
    
    # 1. Melody Pattern (리드미컬하게)
    if idx % 2 == 0: # 짝수: "징-글-벨" 리듬 (점4분, 8분, 2분)
        notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)]
    else: # 홀수: "달-려-가-자" 리듬 (4분음표 4개)
        notes = [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        
    melody_waves = []
    for f, d in notes:
        dur = d * beat_sec
        w = generate_wave(f, dur, "bell")
        w = apply_envelope(w, dur, "short")
        melody_waves.append(w)
    
    melody = np.concatenate(melody_waves)
    total_len = len(melody)
    
    # 2. Harmony (Strings) - 꽉 찬 화음
    pad_freq = base_freq * 0.5 # 1옥타브 아래
    pad = generate_wave(pad_freq, total_len/44100, "strings")
    pad += generate_wave(pad_freq * 1.5, total_len/44100, "strings") # 5도 화음
    pad = apply_envelope(pad, total_len/44100, "long") * 0.3
    
    # 3. Sleigh Bells (썰매 방울) - 박자마다 짤랑!
    sleigh = generate_wave(0, total_len/44100, "sleigh") * 0.4
    
    # 믹싱
    return melody + pad + sleigh

def compose_carol(nums, bpm):
    track = [create_carol_phrase(char, bpm) for char in nums if char.isdigit()]
    if not track: return None
    
    full = np.concatenate(track)
    # 리버브 (겨울 느낌)
    delay = int(44100 * 0.3)
    res = np.zeros(len(full) + delay)
    res[:len(full)] += full
    res[delay:] += full * 0.4
    
    m = np.max(np.abs(res))
    return res / m * 0.95 if m > 0 else res

# --- 5. Main UI ---

st.markdown('<div class="holiday-title">Math & Carol</div>', unsafe_allow_html=True)
st.markdown('<div class="holiday-sub">The Sound of Middle School Mathematics</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.markdown('<div class="snow-card">', unsafe_allow_html=True)
    st.markdown("### 📚 교과서 속 수학 테마")
    
    # 탭 메뉴
    tab1, tab2, tab3, tab4 = st.tabs(["🔴 1학년", "🟢 2학년", "🟡 3학년", "🖊️ 자유입력"])
    
    badge = ""
    title = ""
    desc = ""
    
    with tab1:
        # 중1: 원주율
        badge = '<span class="grade-badge badge-red">중1-2 도형의 성질</span>'
        title = "원주율 (Pi, 3.14)"
        desc = """
        초등학교 때는 3.14로 계산했지만, 중학교부턴 <b>π(파이)</b>라는 기호를 써요.
        이 숫자는 순환하지 않는 무한소수라서 끝이 없답니다.
        <b>🎶 감상 포인트:</b> 끝없이 이어지는 불규칙한 멜로디가 마치 눈송이 같아요.
        """
        nums = "314159265358979323846264338327950288419716939937510"
        
    with tab2:
        # 중2: 순환소수
        badge = '<span class="grade-badge badge-green">중2-1 유리수와 순환소수</span>'
        title = "순환소수 (1/7)"
        desc = """
        분수 1/7을 소수로 바꾸면 <b>0.142857...</b> 이 여섯 숫자가 계속 반복돼요.
        이걸 '순환마디'라고 부르죠.
        <b>🎶 감상 포인트:</b> 도돌이표처럼 반복되는 리듬이 캐롤의 후렴구처럼 신나요!
        """
        nums = "142857142857142857142857142857142857142857142857"

    with tab3:
        # 중3: 무리수
        badge = '<span class="grade-badge badge-gold">중3-1 제곱근과 실수</span>'
        title = "무리수 루트2 (√2)"
        desc = """
        제곱해서 2가 되는 수는 없을까요? 중3이 되면 <b>√ (루트)</b>를 씌워 표현합니다.
        가로세로 1cm인 정사각형의 대각선 길이가 바로 √2 랍니다.
        <b>🎶 감상 포인트:</b> 무리수의 깊고 단단한 느낌이 웅장한 현악기 소리로 표현돼요.
        """
        nums = "141421356237309504880168872420969807856967187537694"

    with tab4:
        user_in = st.text_input("나만의 기념일 입력 (예: 20250101)", placeholder="20250101")
        if user_in:
            nums = "".join(filter(str.isdigit, user_in))
            badge = '<span class="grade-badge badge-red">나만의 수학</span>'
            title = "마이 넘버 캐롤"
            desc = "여러분의 소중한 숫자가 세상에 하나뿐인 캐롤이 됩니다."
        elif 'nums' not in locals(): # 탭1 기본값 유지
            pass 

    # 선택된 내용 표시
    st.markdown(f"{badge} <h3>{title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p>{desc}</p>", unsafe_allow_html=True)
    
    st.write("")
    bpm = st.slider("🛷 썰매 속도 (BPM)", 80, 160, 110)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="snow-card">', unsafe_allow_html=True)
    st.markdown("### 🎄 멜로디 트리 (Melody Tree)")
    
    if nums:
        # [Visualizer] 크리스마스 트리 모양 차트 (삼각형 배치)
        digits = [int(d) for d in nums[:20] if d != '0']
        
        # 트리 모양 데이터 생성 (피라미드 쌓기)
        # 1층 1개, 2층 2개, 3층 3개...
        tree_data = []
        level = 1
        count = 0
        for d in digits:
            tree_data.append({'Level': -level, 'Pos': count - (level-1)/2, 'Note': d})
            count += 1
            if count >= level:
                level += 1
                count = 0
        
        df = pd.DataFrame(tree_data)
        
        c = alt.Chart(df).mark_circle(size=300).encode(
            x=alt.X('Pos', axis=None),
            y=alt.Y('Level', axis=None),
            color=alt.Color('Note', scale=alt.Scale(scheme='redyellowgreen'), legend=None),
            tooltip=['Note']
        ).properties(height=300, background='transparent').configure_view(strokeWidth=0)
        
        st.altair_chart(c, use_container_width=True)
        st.caption("▲ 숫자들이 모여 크리스마스 트리를 만들었어요!")
        
        st.write("")
        
        if st.button("🔔 캐롤 연주 시작 (Play)"):
            with st.spinner("산타가 악보를 배달 중입니다... 🎅"):
                audio_data = compose_carol(nums, bpm)
                
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                
                st.audio(virtual_file, format='audio/wav')
                st.balloons() # 눈과 함께 풍선 파티!

    else:
        st.info("왼쪽에서 테마를 선택해주세요.")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; color:#ADB5BD; font-size:0.8rem; margin-top:50px;">
    Mathematics Winter Festival • Designed for Middle School Students
</div>
""", unsafe_allow_html=True)
