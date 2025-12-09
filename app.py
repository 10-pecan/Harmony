import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Music", page_icon="🎵", layout="wide")

# --- 2. 스타일링 (완전히 현대적인 디자인) ---
st.markdown("""
<style>
    /* 1. 폰트 변경: 요즘 스타일의 깔끔한 고딕체(Pretendard/System font) 적용 */
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif !important;
        color: #171717 !important;
    }
    
    /* 2. 배경: 깨끗한 화이트 & 연한 그레이 */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* 3. 제목 스타일: 굵고 모던하게 */
    h1 {
        font-weight: 800;
        letter-spacing: -1px;
        color: #111 !important;
        margin-bottom: 10px;
    }
    
    /* 4. 카드 디자인 (박스) */
    .modern-card {
        background-color: #F8F9FA; /* 아주 연한 회색 */
        padding: 24px;
        border-radius: 16px; /* 둥근 모서리 */
        border: 1px solid #E9ECEF;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); /* 아주 은은한 그림자 */
    }
    
    /* 5. 팁 박스 (말풍선 느낌) */
    .tip-box {
        background-color: #E3F2FD; /* 산뜻한 파랑 */
        padding: 16px;
        border-radius: 12px;
        color: #0D47A1;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .tip-box b { color: #0056b3; }

    /* 6. 입력창 & 버튼 디자인 */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #fff;
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    .stButton>button {
        background-color: #111 !important; /* 검정 버튼 */
        color: #fff !important;
        border-radius: 10px;
        height: 50px;
        font-weight: 600;
        border: none;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #333 !important;
        transform: scale(1.01);
    }
    
    /* 7. 차트 색상 커스텀 */
    div[data-testid="stBarChart"] {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (소리 개선됨) ---
def generate_tone(freq, duration, wave_type):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # [소리 로직 변경]
    if wave_type == "💧 맑은 물방울 (Sine)":
        # 가장 깨끗한 소리
        wave = np.sin(2 * np.pi * freq * t)
        
    elif wave_type == "🎻 따뜻한 첼로 (Low Bass)":
        # [NEW] 단단한 소리 삭제 -> 부드러운 저음으로 변경
        bass_freq = freq * 0.5 # 옥타브 낮춤
        # 사인파 두 개를 섞어서 풍성하게 만듦 (배음 효과)
        wave = 0.7 * np.sin(2 * np.pi * bass_freq * t) + 0.3 * np.sin(2 * np.pi * bass_freq * 2 * t)
        
    else: # "✨ 반짝이는 소리 (Triangle)"
        # 뾰족하지만 거슬리지 않는 소리
        wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        
    # 소리가 뚝 끊기지 않게 끝을 흐림 (Fade out)
    decay = np.exp(-3 * t)
    return wave * decay

def numbers_to_melody(number_str, bpm, wave_type):
    # 도레미파솔라시도 주파수
    freqs = {
        '1': 261.63, '2': 293.66, '3': 329.63, '4': 349.23,
        '5': 392.00, '6': 440.00, '7': 493.88, '8': 523.25, 
        '9': 587.33, '0': 0
    }
    
    melody = []
    duration = 60.0 / bpm
    
    for char in number_str:
        if char in freqs:
            f = freqs[char]
            if f == 0:
                tone = np.zeros(int(44100 * duration))
            else:
                tone = generate_tone(f, duration, wave_type)
            melody.append(tone)
            
    if not melody: return None
    return np.concatenate(melody)

# --- 4. 메인 UI 구성 ---

st.title("Math Music Lab.")
st.markdown("##### 숫자가 들려주는 나만의 멜로디 🎧")
st.write("") # 여백

col1, col2 = st.columns([1, 1.2])

with col1:
    # 카드형 디자인 적용
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown("### 1. 숫자 고르기")
    
    tab_math, tab_custom = st.tabs(["유명한 수학 숫자", "내 숫자 입력"])
    
    with tab_math:
        math_choice = st.radio("어떤 수의 소리가 궁금한가요?", 
                              ["원주율 (3.14...)", "자연상수 (2.71...)", "황금비 (1.61...)"])
        
        if "원주율" in math_choice:
            nums = "314159265358979323846264338327950288419716939937510"
        elif "자연상수" in math_choice:
            nums = "271828182845904523536028747135266249775724709369995"
        else:
            nums = "161803398874989484820458683436563811772030917980576"

    with tab_custom:
        user_input = st.text_input("생일이나 기념일을 입력해보세요", placeholder="20241225")
        if user_input:
            nums = ''.join(filter(str.isdigit, user_input))
        elif 'nums' not in locals():
             nums = "12345678"
    st.markdown('</div>', unsafe_allow_html=True) # 카드 닫기

    
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown("### 2. 악기 설정")
    # [변경] 소리 이름 직관적으로 변경
    sound_type = st.selectbox("어떤 악기로 연주할까요?", 
                             ["🎻 따뜻한 첼로 (Low Bass)", "💧 맑은 물방울 (Sine)", "✨ 반짝이는 소리 (Triangle)"])
    bpm = st.slider("빠르기 (Tempo)", 60, 180, 110)
    st.markdown('</div>', unsafe_allow_html=True) # 카드 닫기

    # [변경] 중학생 눈높이 설명
    st.markdown("""
    <div class="tip-box">
        <b>💡 수학 선생님의 비밀 노트</b><br><br>
        <b>1. 소리는 떨림이야 (주파수)</b><br>
        숫자가 클수록 더 빨리 떨려서 '높은 소리'가 나고, 숫자가 작으면 천천히 떨려서 '낮은 소리'가 나.<br><br>
        <b>2. 악기마다 모양이 달라 (파형)</b><br>
        방금 고른 <b>'첼로 소리'</b>는 파도 모양 그래프(사인파) 두 개를 섞어서 만든 거야. 수학으로 악기 소리를 흉내 낼 수 있다니 신기하지?<br><br>
        <b>3. 소리가 작아지는 마법 (지수함수)</b><br>
        피아노 건반을 팅~ 치면 소리가 점점 작아지지? 그 모양을 수학 그래프로 그리면 미끄럼틀 모양(지수함수)이랑 똑같아!
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown("### 3. 연주 & 시각화")
    
    if nums:
        # 차트 그리기 (막대 그래프)
        digits = [int(d) for d in nums[:30] if d != '0']
        st.caption(f"🎼 연주할 숫자들: {nums[:20]}...")
        
        # 차트 색상을 모던한 블랙으로
        st.bar_chart(digits, height=220, color="#111111")
        
        st.write("") # 여백
        
        if st.button("▶️ 재생하기 (Play)", use_container_width=True):
            with st.spinner("수학 공식을 음악으로 바꾸는 중..."):
                audio_data = numbers_to_melody(nums, bpm, sound_type)
                virtual_file = io.BytesIO()
                write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
                
                st.audio(virtual_file, format='audio/wav')
                st.balloons() # 성공 축하 효과
    else:
        st.warning("숫자를 입력해주세요.")
    st.markdown('</div>', unsafe_allow_html=True)
