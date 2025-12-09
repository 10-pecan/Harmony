import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io

# --- 1. 페이지 설정 (와이드 모드) ---
st.set_page_config(page_title="Harmonia: Midnight", page_icon="🎹", layout="wide")

# --- 2. 고급 스타일링 (CSS 주입) ---
# 구글 폰트(Cinzel: 고전적 느낌) 불러오기 및 전체 테마 적용
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lato:wght@300;400&display=swap');

    /* 전체 배경 그라데이션 (Midnight Theme) */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0e0;
    }
    
    /* 타이틀 폰트 스타일 */
    h1 {
        font-family: 'Cinzel', serif;
        font-size: 3.5rem !important;
        background: -webkit-linear-gradient(#eee, #999);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* 서브 타이틀 */
    .subtitle {
        font-family: 'Lato', sans-serif;
        text-align: center;
        font-size: 1.2rem;
        color: #a8a8b3;
        margin-bottom: 50px;
    }

    /* 버튼 스타일 (Glassmorphism) */
    .stButton>button {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        height: 60px;
        font-size: 18px;
        font-family: 'Cinzel', serif;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: #fff;
        transform: scale(1.02);
    }
    
    /* 입력창 및 슬라이더 스타일 */
    .stTextInput>div>div>input {
        background-color: rgba(0, 0, 0, 0.3);
        color: white;
        border: 1px solid #444;
        text-align: center;
    }
    
    /* 풋터 숨김 */
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (사운드 업그레이드) ---
def generate_rich_tone(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # [사운드 디자인] 기본음 + 배음(Harmonics)을 섞어 풍성하게 만듦
    # Fundamental (기본음)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    # 2nd Harmonic (한 옥타브 위) - 은은하게
    tone += 0.2 * np.sin(2 * np.pi * (frequency * 2) * t)
    # 3rd Harmonic (완전 5도 위) - 약간의 색채
    tone += 0.1 * np.sin(2 * np.pi * (frequency * 3) * t)
    
    # Envelope (ADSR 중 Release 구현) - 소리가 뚝 끊기지 않고 부드럽게 사라짐
    decay = np.exp(-3 * t) # 감쇠 곡선
    tone = tone * decay
    
    return tone

def numbers_to_melody(number_str, speed, octave):
    # 피타고라스 음계 기반 주파수 매핑
    base_freqs = {
        '1': 261.63, '2': 293.66, '3': 329.63, '4': 349.23,
        '5': 392.00, '6': 440.00, '7': 493.88, '8': 523.25, 
        '9': 587.33, '0': 0
    }
    
    melody = []
    duration = 1.0 / speed 
    
    for char in number_str:
        if char in base_freqs:
            freq = base_freqs[char]
            if freq > 0:
                # 옥타브 적용
                freq = freq * (2 ** (octave - 4))
                tone = generate_rich_tone(freq, duration)
            else:
                # 쉼표 (0일 때)
                tone = np.zeros(int(44100 * duration))
            
            melody.append(tone)
            
    if not melody: return None
    return np.concatenate(melody)

# --- 4. 메인 UI 구성 ---

# 헤더 영역
st.markdown("<h1>HARMONIA</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Where Mathematics Meets Melody</div>", unsafe_allow_html=True)

# 레이아웃 분할 (3단 구성으로 중앙 집중)
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    # 탭 메뉴
    tab1, tab2 = st.tabs(["✨ PRESETS", "🎹 CUSTOM"])
    
    num_input = ""
    
    with tab1:
        preset = st.selectbox("수학적 상수 선택", 
                             ["Circle Constant (π)", "Euler's Number (e)", "Golden Ratio (φ)"],
                             label_visibility="collapsed")
        
        if "π" in preset:
            num_input = "314159265358979323846264338327950288419716939937510"
            desc = "원주율(Pi): 원의 둘레와 지름의 비율. 무한하고 반복되지 않는 신비로운 수."
        elif "e" in preset:
            num_input = "271828182845904523536028747135266249775724709369995"
            desc = "자연상수(e): 성장의 한계와 연속 복리를 설명하는 아름다운 수."
        else:
            num_input = "161803398874989484820458683436563811772030917980576"
            desc = "황금비(Phi): 자연계와 예술에서 발견되는 가장 완벽한 비율."
            
        st.caption(f"📜 {desc}")

    with tab2:
        user_input = st.text_input("숫자를 입력하세요 (예: 생년월일, 기념일)", placeholder="Numbers only...")
        if user_input:
            num_input = ''.join(filter(str.isdigit, user_input))

    st.markdown("---")

    # 컨트롤러 (속도, 옥타브)
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        bpm = st.slider("Tempo", 1, 10, 5)
    with col_ctrl2:
        octave = st.select_slider("Octave", options=[3, 4, 5], value=4)

    # 생성 버튼
    generate_btn = st.button("Generate Harmony")

# --- 5. 결과물 출력 (하단) ---
if num_input and generate_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 오디오 생성
    with st.spinner("Calculating Frequencies..."):
        audio_data = numbers_to_melody(num_input, bpm, octave)
        
        # 1. 시각화 (Area Chart로 파동 느낌 연출)
        chart_data = [int(d) for d in num_input if d != '0'][:50] # 50개만 샘플링
        st.area_chart(chart_data, height=120, color="#8B5FBF")
        
        # 2. 오디오 플레이어
        virtual_file = io.BytesIO()
        write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
        st.audio(virtual_file, format='audio/wav')
        
        # 3. 다운로드 버튼 (중앙 정렬)
        c_d1, c_d2, c_d3 = st.columns([1, 1, 1])
        with c_d2:
            st.download_button(
                label="📥 MP3 다운로드 (소장용)",
                data=virtual_file,
                file_name="harmonia_result.wav",
                mime="audio/wav",
                use_container_width=True
            )

# 하단 여백
st.markdown("<br><br><br>", unsafe_allow_html=True)
