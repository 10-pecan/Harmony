import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Music: Serendipity", page_icon="🌸", layout="wide")

# --- 2. 아름다운 디자인 (CSS) ---
st.markdown("""
<style>
    /* [폰트 설정] */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Montserrat:wght@400;600&display=swap');

    :root {
        --bg-color: #FFF9F9; /* 아주 연한 핑크빛 화이트 */
        --primary-color: #FFB7B2; /* 파스텔 코랄 */
        --secondary-color: #E2F0CB; /* 파스텔 그린 */
        --accent-color: #C7CEEA; /* 파스텔 퍼플 */
        --text-dark: #4A4A4A; /* 부드러운 차콜 */
    }

    /* 전체 배경 및 폰트 */
    .stApp {
        background-color: var(--bg-color) !important;
        color: var(--text-dark) !important;
        font-family: 'Gowun Dodum', sans-serif !important;
    }

    /* [ISSUE FIX] 탭/라디오 버튼 선택 시 글씨 안 보이는 문제 해결 */
    /* 탭(Tab) 스타일 커스텀 */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 20px !important;
        color: #888 !important;
        font-weight: normal !important;
        border: 1px solid transparent !important;
    }
    /* 선택된 탭: 진한 배경 대신 연한 파스텔톤 배경 + 진한 글씨 */
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFF0F5 !important; /* 연한 분홍 */
        color: #FF6B6B !important; /* 진한 핑크 글씨 */
        border: 1px solid #FFB7B2 !important;
        font-weight: bold !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* 라디오 버튼 커스텀 */
    div[role="radiogroup"] label {
        background-color: #FFFFFF !important;
        border: 1px solid #EEE !important;
        padding: 10px 15px !important;
        border-radius: 12px !important;
        margin-bottom: 5px !important;
        color: #555 !important;
        transition: 0.2s;
    }
    /* 선택된 라디오 버튼 텍스트 색상 강제 지정 */
    div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
        background-color: #FFB7B2 !important; /* 체크박스 색 */
    }

    /* [타이틀 디자인] */
    .title-area {
        text-align: center;
        margin-bottom: 40px;
        padding: 20px;
    }
    .main-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 3rem;
        font-weight: 600;
        background: linear-gradient(90deg, #FF9A9E, #FECFEF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
    }
    .sub-title {
        color: #888;
        font-size: 1rem;
        margin-top: 10px;
    }

    /* [카드 UI: 마카롱 스타일] */
    .macaron-card {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 30px;
        box-shadow: 0 10px 30px rgba(255, 183, 178, 0.15); /* 부드러운 핑크 그림자 */
        border: 1px solid #FFF0F0;
        margin-bottom: 25px;
    }
    
    /* 섹션 헤더 */
    .section-header {
        font-size: 1.2rem;
        color: #6D6D6D;
        margin-bottom: 20px;
        border-left: 4px solid #FFB7B2;
        padding-left: 15px;
        font-weight: bold;
    }

    /* [말풍선 팁] */
    .soft-tip {
        background-color: #F3F8FF;
        border-radius: 20px;
        padding: 20px;
        color: #5B7BB2;
        font-size: 0.95rem;
        line-height: 1.7;
        border: 1px dashed #C7CEEA;
    }

    /* [입력창 예쁘게] */
    .stTextInput input {
        border-radius: 15px !important;
        border: 2px solid #F0F0F0 !important;
        padding: 12px !important;
        color: #555 !important;
    }
    .stTextInput input:focus {
        border-color: #FFB7B2 !important;
        box-shadow: none !important;
    }

    /* [재생 버튼] */
    .play-btn-area button {
        background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%) !important;
        color: #fff !important;
        font-weight: bold;
        border-radius: 50px;
        height: 60px;
        font-size: 1.1rem;
        border: none;
        box-shadow: 0 5px 15px rgba(161, 196, 253, 0.4);
        transition: transform 0.2s;
    }
    .play-btn-area button:hover {
        transform: translateY(-3px);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (Melodical Upgrade) ---
# 기존의 단순한 1:1 매칭이 아니라, 리듬과 화음을 추가하여 '진짜 음악'처럼 만듭니다.

def generate_piano_note(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # [Piano Synthesis] 피아노처럼 풍성한 소리 만들기
    # 기본음 + 배음(Overtones)을 섞고, 타격음(Attack)을 시뮬레이션
    tone = 0.6 * np.sin(2 * np.pi * freq * t)
    tone += 0.3 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-3 * t) # 2배음
    tone += 0.1 * np.sin(2 * np.pi * freq * 3 * t) * np.exp(-5 * t) # 3배음
    
    # ADSR Envelope (부드러운 감쇠)
    envelope = np.exp(-2.5 * t) 
    
    return tone * envelope

def numbers_to_beautiful_music(number_str, bpm):
    # [음악 이론] 펜타토닉 스케일 (어떤 순서로 연주해도 아름다운 음계)
    # C Major Pentatonic: C(도), D(레), E(미), G(솔), A(라) + 높은음
    scale = {
        '1': 261.63, # C4
        '2': 293.66, # D4
        '3': 329.63, # E4
        '4': 392.00, # G4
        '5': 440.00, # A4
        '6': 523.25, # C5
        '7': 587.33, # D5
        '8': 659.25, # E5
        '9': 783.99, # G5
        '0': 0       # 쉼표
    }
    
    melody = []
    base_duration = 60.0 / bpm
    
    for i, char in enumerate(number_str):
        if char in scale:
            freq = scale[char]
            
            # [Melody Logic] 숫자에 따라 리듬(길이)을 다르게 줌 (리듬감 형성)
            # 짝수는 짧고 경쾌하게(0.5박), 홀수는 길고 우아하게(1박)
            digit = int(char)
            if digit == 0:
                duration = base_duration
                tone = np.zeros(int(44100 * duration))
            elif digit % 2 == 0: 
                duration = base_duration * 0.5 # 8분음표
            else: 
                duration = base_duration # 4분음표

            if freq > 0:
                tone = generate_piano_note(freq, duration)
                
                # [Harmony Logic] 3의 배수일 때 화음(3도 위) 추가 -> 풍성함 UP
                if digit % 3 == 0:
                    harmony_freq = freq * 1.25 # 장3도 위
                    harmony_tone = generate_piano_note(harmony_freq, duration)
                    tone = tone + (harmony_tone * 0.6) # 화음 섞기
            else:
                tone = np.zeros(int(44100 * duration))
                
            melody.append(tone)
            
    if not melody: return None
    return np.concatenate(melody)

# --- 4. 메인 UI 구성 ---

st.markdown('<div class="title-area"><div class="main-title">Serendipity</div><div class="sub-title">수학이 그리는 우연한 아름다움</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown('<div class="macaron-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Numbers (숫자)</div>', unsafe_allow_html=True)
    
    # 탭 디자인 개선
    tab_math, tab_custom = st.tabs(["✨ 신비로운 상수", "💌 나의 숫자"])
    
    with tab_math:
        # 라디오 버튼 선택 시 배경 문제 해결됨
        math_choice = st.radio("영감을 줄 숫자를 선택하세요", 
                              ["Pi (원주율) - 영원한 흐름", "Golden Ratio (황금비) - 완벽한 균형", "Euler (자연상수) - 성장의 미학"],
                              label_visibility="collapsed")
        
        if "Pi" in math_choice: nums = "314159265358979323846264338327950288419716939937510"
        elif "Golden" in math_choice: nums = "161803398874989484820458683436563811772030917980576"
        else: nums = "271828182845904523536028747135266249775724709369995"
            
    with tab_custom:
        user_input = st.text_input("당신의 특별한 날짜를 입력하세요", placeholder="예: 20241225")
        if user_input: nums = ''.join(filter(str.isdigit, user_input))
        elif 'nums' not in locals(): nums = "12345678"
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 감성적인 설명
    st.markdown("""
    <div class="soft-tip">
        <b>🌿 힐링 포인트</b><br>
        이 음악은 <b>'펜타토닉 스케일'</b>로 만들어졌어요. 
        마치 풍경(Wind chime) 소리처럼, 어떤 숫자가 와도 서로 어울리며 
        아름다운 화음을 만들어냅니다. 눈을 감고 들어보세요.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="macaron-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Visualizer (시각화)</div>', unsafe_allow_html=True)
    
    if nums:
        # [Visual Upgrade] 몽환적인 버블 차트
        digits = [int(d) for d in nums[:20] if d != '0']
        
        # 데이터프레임
        df = pd.DataFrame({
            'x': range(len(digits)),
            'y': digits,
            'size': [d * 15 + 100 for d in digits], # 크기 변화
            'color': digits # 색상 변화 기준
        })

        # Altair로 파스텔톤 차트 그리기
        chart = alt.Chart(df).mark_circle().encode(
            x=alt.X('x', axis=None),
            y=alt.Y('y', axis=None, scale=alt.Scale(domain=[-1, 11])),
            size=alt.Size('size', legend=None),
            color=alt.Color('color', scale=alt.Scale(scheme='pastel1'), legend=None), # 파스텔 색상
            tooltip=['y']
        ).properties(
            height=300
        ).configure_view(strokeWidth=0) # 테두리 제거

        st.altair_chart(chart, use_container_width=True)
        st.caption(f"🎶 Melody Sequence: {nums[:15]}...")

        st.write("")
        
        # 재생 버튼 스타일 적용
        with st.container():
            st.markdown('<div class="play-btn-area">', unsafe_allow_html=True)
            if st.button("🎹 Play Beautiful Melody", use_container_width=True):
                with st.spinner("아름다운 선율을 조율 중입니다..."):
                    # BPM을 약간 느리게(Andante) 설정하여 감성적으로
                    audio_data = numbers_to_beautiful_music(nums, bpm=90)
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.info("숫자를 선택해주세요.")
        
    st.markdown('</div>', unsafe_allow_html=True)
