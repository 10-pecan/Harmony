import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Masterpiece", page_icon="🎄", layout="wide")

# --- 2. 디자인 (Royal Winter Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Noto+Serif+KR:wght@300;500;700&display=swap');
    
    /* [배경] 깊은 겨울 밤하늘 */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #0F2027, #203A43, #2C5364) !important;
        color: #fdfdfd !important;
        font-family: 'Noto Serif KR', serif !important;
    }

    /* [눈 내리는 효과] */
    .snowflake {
        position: fixed; top: -10px; z-index: 0;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2em; text-shadow: 0 0 5px #FFF;
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { transform: translateY(-10vh) rotate(0deg); opacity: 0; }
        20% { opacity: 1; }
        100% { transform: translateY(110vh) rotate(360deg); opacity: 0.3; }
    }

    /* [타이포그래피] */
    .royal-title {
        font-family: 'Cinzel', serif;
        font-size: 4rem; font-weight: 700; text-align: center;
        background: linear-gradient(to bottom, #FFD700, #FDB931);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
        margin-top: 20px; letter-spacing: 3px;
    }
    .royal-sub {
        text-align: center; color: #cbd5e1; font-size: 1.1rem; letter-spacing: 1px;
        margin-bottom: 40px; font-weight: 300;
    }

    /* [컨테이너 박스] */
    .glass-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 15px; padding: 30px; margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }

    /* [교육용 텍스트 박스] */
    .edu-box {
        background-color: rgba(0, 20, 40, 0.6);
        border-left: 4px solid #FFD700;
        padding: 20px; border-radius: 0 10px 10px 0;
        line-height: 1.8; margin-top: 20px;
    }
    .edu-box h4 { color: #FFD700 !important; margin-bottom: 10px; }
    .edu-box b { color: #81D4FA; }

    /* [탭 스타일] */
    div[data-baseweb="tab-list"] { background: transparent !important; }
    button[data-baseweb="tab"] { color: #aaa !important; font-family: 'Cinzel', serif !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFD700 !important; border-bottom: 2px solid #FFD700 !important; font-weight: bold !important;
    }

    /* [재생 버튼] */
    .stButton>button {
        background: linear-gradient(135deg, #FFD700, #FFA500) !important;
        color: #000 !important; border: none; width: 100%; height: 65px;
        font-family: 'Cinzel', serif; font-size: 1.3rem; font-weight: 700;
        border-radius: 10px; box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 눈 효과 JS ---
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(8, 15)}s; animation-delay:{np.random.uniform(0, 8)}s;">❄</div>' for _ in range(30)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 4. 🎻 Grand Audio Engine (멜로디+리듬+화음) ---

def generate_wave(freq, duration, type="sine"):
    sr = 44100
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if type == "bell": # 영롱한 종소리
        return 0.5*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t) + 0.2*np.sin(2*np.pi*freq*5*t)*np.exp(-2*t)
    elif type == "strings": # 풍성한 현악기
        return 0.4*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*2*t)
    elif type == "choir": # 천상의 코러스
        return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*0.998*t)
    return np.zeros(num_samples)

def match_len(wave, length):
    if len(wave) == length: return wave
    elif len(wave) > length: return wave[:length]
    return np.pad(wave, (0, length - len(wave)), 'constant')

def apply_envelope(wave, duration, type="bell"):
    length = len(wave)
    if type == "bell": # 종소리: 띵~ (빠른 어택, 긴 여운)
        env = np.exp(np.linspace(0, -4, length))
    else: # 스트링/코러스: 웅~장 (천천히 커졌다 작아짐)
        att = int(length*0.2)
        rel = int(length*0.3)
        sus = length - att - rel
        if sus<0: sus=0
        env = np.concatenate([np.linspace(0,1,att), np.full(sus,1.0), np.linspace(1,0,rel)])
    return wave * match_len(env, length)

def apply_reverb(audio, decay=0.6, delay_ms=400):
    delay_samples = int(44100 * (delay_ms/1000))
    res = np.zeros(len(audio) + delay_samples)
    res[:len(audio)] += audio
    res[delay_samples:] += audio * decay
    return res

def compose_masterpiece(nums, bpm):
    # D Major Scale (겨울 느낌)
    scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    
    quarter_note = 60.0 / bpm
    
    full_track = []
    
    # [핵심] 숫자별 '음악적 프레이즈(Phrase)' 정의
    # 리듬감과 멜로디성을 부여하기 위해 숫자 하나가 여러 음을 연주함
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        base_freq = scale[idx % len(scale)]
        
        # 1. 리듬 & 멜로디 패턴 선택
        melody_seq = [] # (주파수 배율, 길이 비율)
        
        if idx % 4 == 0:   # 왈츠 패턴 (쿵-짝-짝)
            melody_seq = [(1.0, 1.0), (1.25, 0.5), (1.5, 0.5)] 
        elif idx % 4 == 1: # 아르페지오 (빠르게 상승)
            melody_seq = [(1.0, 0.5), (1.25, 0.5), (1.5, 0.5), (2.0, 0.5)]
        elif idx % 4 == 2: # 롱 노트 (우아하게)
            melody_seq = [(1.0, 1.5), (0.8, 0.5)]
        else:              # 스타카토 (통통 튀게)
            melody_seq = [(1.5, 0.25), (1.25, 0.25), (1.0, 0.5), (1.0, 1.0)]

        # 2. 사운드 합성 (멜로디 + 화음)
        phrase_waves = []
        for freq_mult, dur_mult in melody_seq:
            dur_sec = quarter_note * dur_mult
            
            # Lead Melody (Bell)
            f = base_freq * freq_mult
            bell = generate_wave(f, dur_sec, "bell")
            bell = apply_envelope(bell, dur_sec, "bell")
            
            # Harmony (Strings) - 1옥타브 아래
            # 길이 맞추기
            str_wave = generate_wave(base_freq * 0.5, dur_sec, "strings")
            str_wave = apply_envelope(str_wave, dur_sec, "strings") * 0.4
            
            # Choir (High) - 숫자가 클 때만 등장
            choir_wave = np.zeros_like(bell)
            if idx > 5:
                choir_wave = generate_wave(base_freq * 2, dur_sec, "choir")
                choir_wave = apply_envelope(choir_wave, dur_sec, "strings") * 0.25
                
            mix = bell + str_wave + choir_wave
            phrase_waves.append(mix)
            
        full_track.append(np.concatenate(phrase_waves))
        
    if not full_track: return None
    
    # 전체 연결 및 리버브
    raw = np.concatenate(full_track)
    final = apply_reverb(raw, decay=0.6, delay_ms=500)
    
    # 노멀라이즈
    m = np.max(np.abs(final))
    return final / m * 0.95 if m > 0 else final

# --- 5. UI Layout ---

st.markdown('<div class="royal-title">MATH SYMPHONY</div>', unsafe_allow_html=True)
st.markdown('<div class="royal-sub">수학과 음악이 만나는 가장 아름다운 순간</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown("### 🎼 연주할 수학 테마")
    
    tab1, tab2, tab3 = st.tabs(["⭕ 원주율 (Pi)", "✨ 황금비 (Phi)", "📐 루트2 (Sqrt2)"])
    
    with tab1:
        nums = "314159265358979323846264338327950288419716939937510"
        title = "원주율 (Pi, 3.14...)"
        desc = """
        <h4>⭕ 원주율: 영원히 끝나지 않는 노래</h4>
        우리가 원을 그릴 때마다 사용하는 <b>3.141592...</b>는 규칙 없이 무한히 이어지는 신비로운 숫자입니다.
        <br><br>
        이 숫자를 음악으로 바꾸면, <b>'예측할 수 없는 멜로디'</b>가 탄생합니다.
        마치 눈 내리는 겨울밤처럼, 불규칙 속에서 피어나는 수학적 아름다움을 감상해보세요.
        """
    with tab2:
        nums = "161803398874989484820458683436563811772030917980576"
        title = "황금비 (Golden Ratio, 1.618...)"
        desc = """
        <h4>✨ 황금비: 신이 설계한 비율</h4>
        <b>1 : 1.618</b>은 자연계에서 가장 완벽하고 아름답다고 여겨지는 비율입니다.
        파르테논 신전, 해바라기 씨앗, 그리고 우리의 DNA 속에도 이 비율이 숨어있죠.
        <br><br>
        이 비율을 음악으로 연주하면, 가장 <b>안정적이고 편안한 화음</b>의 흐름을 느낄 수 있습니다.
        """
    with tab3:
        nums = "141421356237309504880168872420969807856967187537694"
        title = "루트 2 (Root 2, 1.414...)"
        desc = """
        <h4>📐 루트 2: 최초의 무리수</h4>
        가로세로 1cm인 정사각형의 대각선 길이는 얼마일까요? 바로 <b>1.414...</b>입니다.
        <br><br>
        고대 피타고라스 학파는 이 숫자의 비밀을 풀기 위해 평생을 바쳤다고 합니다.
        단단한 도형 속에 숨겨진 <b>깊고 웅장한 소리</b>를 들어보세요.
        """

    # [수학 도슨트 섹션]
    st.markdown(f"<div class='edu-box'>{desc}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 템포 조절
    bpm = st.slider("지휘 속도 (Tempo)", 70, 140, 90)

with col2:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown("### 🎹 멜로디 시각화 (Aurora Score)")
    
    if nums:
        # Altair 시각화 (오로라 스타일)
        digits = [int(d) for d in nums[:25] if d != '0']
        df = pd.DataFrame({'Note': digits, 'Time': range(len(digits))})
        
        c = alt.Chart(df).mark_area(
            interpolate='monotone', # 부드러운 곡선
            line={'color':'#FFD700'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#FFD700', offset=0),
                       alt.GradientStop(color='rgba(255, 215, 0, 0)', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x=alt.X('Time', axis=None),
            y=alt.Y('Note', axis=None, scale=alt.Scale(domain=[-1, 11]))
        ).properties(height=200).configure_view(strokeWidth=0)
        
        st.altair_chart(c, use_container_width=True)
        
        # 교육용 팁 (소리의 원리)
        st.info("""
        💡 **소리의 수학적 비밀**
        이 음악은 녹음된 것이 아닙니다. **삼각함수(Sine Wave)**를 이용하여 실시간으로 합성된 소리입니다.
        소리가 서서히 사라지는 효과는 **지수함수(Exponential Decay)**를 곱해서 만들었답니다!
        """)
        
        st.write("")
        
        # 재생 버튼
        if st.button("🎻 웅장한 캐롤 연주 시작 (Play)"):
            with st.spinner("오케스트라 단원들이 악보를 넘기는 중... 🎼"):
                audio = compose_masterpiece(nums, bpm)
                
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                st.audio(virtual_file, format='audio/wav')
                st.success(f"Now Playing: {title}")

    st.markdown('</div>', unsafe_allow_html=True)
