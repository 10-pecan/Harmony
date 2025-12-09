import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Symphony", page_icon="🎻", layout="wide")

# --- 2. [강력한 UI 수정] 글씨가 무조건 잘 보이게 설정 ---
st.markdown("""
<style>
    /* [핵심] 배경은 무조건 흰색, 글씨는 무조건 진한 남색으로 고정 */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* 모든 텍스트 강제 색상 지정 (다크모드 무시) */
    html, body, h1, h2, h3, h4, h5, h6, p, span, div, label, li {
        color: #1a237e !important; /* 진한 네이비 */
        font-family: 'Pretendard', sans-serif !important;
    }

    /* [탭/라디오 버튼 이슈 해결] */
    /* 선택되지 않은 탭 */
    button[data-baseweb="tab"] {
        background-color: #f5f5f5 !important;
        color: #666 !important;
        border: 1px solid #ddd !important;
    }
    /* 선택된 탭 (배경 진하게, 글씨 하얗게 -> 잘 보임) */
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #1a237e !important; /* 진한 네이비 */
        color: #FFD700 !important; /* 황금색 글씨 */
        border: none !important;
        font-weight: bold !important;
    }
    
    /* 라디오 버튼 선택 시 */
    div[role="radiogroup"] label > div:first-child {
        background-color: #fff !important;
    }
    
    /* 제목 스타일 (오케스트라 느낌) */
    .grand-title {
        font-family: 'Times New Roman', serif !important;
        font-size: 3.5rem;
        font-weight: bold;
        color: #1a237e !important;
        text-align: center;
        margin-bottom: 5px;
        text-shadow: 2px 2px 0px #FFD700; /* 황금 그림자 */
    }
    .sub-title {
        text-align: center;
        color: #555 !important;
        font-style: italic;
        margin-bottom: 40px;
    }

    /* 카드 디자인 (고급스러운 테두리) */
    .royal-card {
        background-color: #FAFAFA;
        border: 2px solid #1a237e;
        border-radius: 10px;
        padding: 25px;
        box-shadow: 5px 5px 0px rgba(26, 35, 126, 0.1);
        margin-bottom: 20px;
    }

    /* 버튼 스타일 (지휘자 느낌) */
    .stButton>button {
        background: linear-gradient(135deg, #1a237e, #283593) !important;
        color: #FFD700 !important; /* 황금색 글씨 */
        border: 2px solid #FFD700 !important;
        border-radius: 5px;
        height: 60px;
        font-size: 1.2rem;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(26, 35, 126, 0.4);
    }
    
    /* 입력창 테두리 */
    .stTextInput input {
        border: 2px solid #1a237e !important;
        border-radius: 5px !important;
        color: #1a237e !important;
        background-color: #fff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (Grand Orchestra Algorithm) ---
# 단순한 사인파가 아니라, 여러 파형을 합쳐서 '현악기 앙상블' 소리를 만듭니다.

def generate_orchestra_note(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 1. Main Melody (Violin Section): 톱니파(Sawtooth)를 부드럽게 가공
    # 톱니파는 현악기처럼 풍부한 배음을 가집니다.
    violin = 0.5 * (2 * (freq * t - np.floor(freq * t + 0.5))) # Sawtooth
    
    # 2. Harmony (Viola/Cello): 3도 위 화음 + 1옥타브 아래 베이스
    # 숫자가 하나 들어오면 자동으로 화음을 쌓습니다.
    harmony_freq = freq * 1.25 # 장3도 (Major 3rd)
    bass_freq = freq * 0.5     # 1옥타브 아래
    
    viola = 0.3 * np.sin(2 * np.pi * harmony_freq * t) # 부드러운 화음
    cello = 0.4 * np.sin(2 * np.pi * bass_freq * t)    # 묵직한 베이스
    
    # 3. 합치기 (Ensemble)
    wave = violin + viola + cello
    
    # 4. ADSR Envelope (부드러운 시작과 긴 여운)
    # 현악기는 소리가 서서히 커졌다가(Attack) 천천히 사라짐(Release)
    total_len = len(t)
    attack_len = int(total_len * 0.3) # 30% 동안 커짐
    sustain_len = int(total_len * 0.4)
    release_len = total_len - attack_len - sustain_len
    
    attack = np.linspace(0, 1, attack_len)
    sustain = np.linspace(1, 0.8, sustain_len)
    release = np.linspace(0.8, 0, release_len)
    
    envelope = np.concatenate([attack, sustain, release])
    
    # 길이 오차 보정
    if len(envelope) < total_len:
         envelope = np.pad(envelope, (0, total_len - len(envelope)), 'constant')
    elif len(envelope) > total_len:
         envelope = envelope[:total_len]

    return wave * envelope

def apply_reverb(audio_data, delay_ms=300, decay=0.5, sample_rate=44100):
    # [Reverb Effect] 공연장의 울림 효과 추가
    delay_samples = int(sample_rate * (delay_ms / 1000))
    reverb_signal = np.zeros(len(audio_data) + delay_samples)
    reverb_signal[:len(audio_data)] += audio_data
    # 원본 소리의 50% 크기로 뒤에 딜레이된 소리를 더함
    reverb_signal[delay_samples:] += audio_data * decay 
    return reverb_signal

def numbers_to_symphony(number_str, bpm):
    # C Major Scale (Grand) - 웅장함을 위해 음역대를 넓게 잡음
    scale = {
        '1': 261.63, '2': 293.66, '3': 329.63, '4': 349.23,
        '5': 392.00, '6': 440.00, '7': 493.88, '8': 523.25, 
        '9': 587.33, '0': 0
    }
    
    melody = []
    base_duration = 60.0 / bpm
    
    for char in number_str:
        if char in scale:
            freq = scale[char]
            
            # 리듬 변화: 0은 쉼표, 그 외에는 웅장하게
            if freq == 0:
                tone = np.zeros(int(44100 * base_duration))
            else:
                tone = generate_orchestra_note(freq, base_duration * 1.5) # 음을 조금 더 길게(Legato)
            
            melody.append(tone)
            
    if not melody: return None
    
    # 전체 연결 후 리버브(울림) 적용
    full_track = np.concatenate(melody)
    full_track_with_reverb = apply_reverb(full_track)
    
    # 볼륨 정규화 (소리 깨짐 방지)
    max_val = np.max(np.abs(full_track_with_reverb))
    if max_val > 0:
        full_track_with_reverb = full_track_with_reverb / max_val * 0.9
        
    return full_track_with_reverb

# --- 4. 메인 UI ---

st.markdown('<div class="grand-title">MATH SYMPHONY</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">수학적 연산으로 지휘하는 웅장한 오케스트라</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.4], gap="large")

with col1:
    st.markdown('<div class="royal-card">', unsafe_allow_html=True)
    st.markdown("### 🎼 악보 (Score)")
    
    # 탭 선택 시 이슈 해결된 버전
    tab_math, tab_custom = st.tabs(["✨ 위대한 상수", "🎻 나만의 주제곡"])
    
    with tab_math:
        choice = st.radio("연주할 테마를 선택하세요", 
                         ["Symphony No.3.14 (Pi)", "Concerto No.2.71 (Euler)", "Sonata No.1.61 (Golden Ratio)"])
        
        if "Pi" in choice: nums = "314159265358979323846264338327950288419716939937510"
        elif "Euler" in choice: nums = "271828182845904523536028747135266249775724709369995"
        else: nums = "161803398874989484820458683436563811772030917980576"
            
    with tab_custom:
        user_in = st.text_input("숫자를 입력하세요", placeholder="19950815")
        if user_in: nums = ''.join(filter(str.isdigit, user_in))
        elif 'nums' not in locals(): nums = "12345678"
    
    st.markdown("---")
    bpm = st.slider("지휘 속도 (Tempo)", 60, 140, 90) # 오케스트라는 좀 느려야 웅장함
    st.markdown('</div>', unsafe_allow_html=True)

    # 팁 박스
    st.info("""
    🎻 **오케스트라 사운드의 비밀**
    이 프로그램은 단순히 '삐-' 소리를 내지 않습니다. 
    하나의 숫자를 입력하면 **'바이올린(주선율) + 비올라(화음) + 첼로(베이스)'** 파형을 
    수학적으로 동시에 생성하여 합칩니다.
    """)

with col2:
    st.markdown('<div class="royal-card" style="border-color:#FFD700;">', unsafe_allow_html=True)
    st.markdown("### 🎹 시각화 (Visualization)")
    
    if nums:
        # Altair 차트 (골드 & 네이비 테마)
        digits = [int(d) for d in nums[:25] if d != '0']
        df = pd.DataFrame({'Time': range(len(digits)), 'Pitch': digits, 'Volume': [d*10+50 for d in digits]})

        chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X('Time', axis=None),
            y=alt.Y('Pitch', axis=None, scale=alt.Scale(domain=[0, 12])),
            color=alt.value("#1a237e"), # 네이비색 막대
            opacity=alt.value(0.8),
            tooltip=['Pitch']
        ).properties(height=250)
        
        # 선율 라인 추가 (금색 선)
        line = alt.Chart(df).mark_line(color='#FFD700', strokeWidth=3).encode(
            x='Time', y='Pitch'
        )

        st.altair_chart(chart + line, use_container_width=True)
        st.caption(f"🎶 Opus Sequence: {nums[:15]}...")
        
        st.write("")
        
        if st.button("🎵 오케스트라 연주 시작 (Maestro Start)", use_container_width=True):
            with st.spinner("단원들이 튜닝 중입니다... 🎻"):
                audio_data = numbers_to_symphony(nums, bpm)
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                st.audio(virtual_file, format='audio/wav')
                st.success("연주가 시작되었습니다.")
    else:
        st.warning("악보(숫자)를 준비해주세요.")
    st.markdown('</div>', unsafe_allow_html=True)
