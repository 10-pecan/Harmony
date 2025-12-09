import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import time

# --- 1. 페이지 설정 (모바일 앱 느낌을 위해 Centered 추천) ---
st.set_page_config(page_title="Mathgram", page_icon="🎵", layout="centered")

# --- 2. 힙한 SNS 스타일링 (CSS) ---
st.markdown("""
<style>
    /* 전체 폰트 및 배경 (다크 모드 베이스) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* 인스타 프로필 느낌의 헤더 */
    .profile-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .profile-img {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
        padding: 2px;
        margin-right: 15px;
    }
    .profile-img-inner {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background-color: black;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
    }
    .profile-name {
        font-weight: 700;
        font-size: 18px;
    }
    .profile-loc {
        font-size: 12px;
        color: #888;
    }

    /* 그라데이션 버튼 (좋아요/재생) */
    .stButton>button {
        background: transparent;
        border: 1px solid #333;
        color: white;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #e1306c;
        color: #e1306c;
    }
    
    /* 입력창 둥글게 */
    .stTextInput>div>div>input {
        border-radius: 20px;
        background-color: #121212;
        color: white;
        border: 1px solid #333;
    }
    
    /* 앨범 커버 같은 차트 영역 */
    .cover-art {
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 15px;
        border: 1px solid #222;
        box-shadow: 0 4px 15px rgba(220, 39, 67, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (감성 사운드) ---
def generate_rich_tone(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # 몽환적인 일렉트릭 피아노 톤
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    tone += 0.3 * np.sin(2 * np.pi * (frequency * 2) * t) * np.exp(-2 * t) # 반짝이는 느낌
    tone += 0.1 * np.sin(2 * np.pi * (frequency * 0.5) * t) # 베이스
    
    decay = np.exp(-4 * t) 
    return tone * decay

def numbers_to_melody(number_str, speed, octave):
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
                freq = freq * (2 ** (octave - 4))
                tone = generate_rich_tone(freq, duration)
            else:
                tone = np.zeros(int(44100 * duration))
            melody.append(tone)
            
    if not melody: return None
    return np.concatenate(melody)

# --- 4. 메인 UI (SNS 피드 스타일) ---

# [상단 프로필]
st.markdown("""
<div class="profile-header">
    <div class="profile-img">
        <div class="profile-img-inner">🎹</div>
    </div>
    <div>
        <div class="profile-name">Math_DJ_Official</div>
        <div class="profile-loc">Pythagoras Studio • Seoul</div>
    </div>
</div>
""", unsafe_allow_html=True)

# [입력 및 설정]
tab_feed, tab_new = st.tabs(["🔥 핫한 숫자들", "➕ 나만의 곡 만들기"])

target_nums = ""
hashtags = ""

with tab_feed:
    st.caption("지금 인기 있는 수학적 선율")
    feed_pick = st.selectbox("재생 목록 선택", 
                            ["π (파이) - 영원히 반복되지 않는 노래", 
                             "φ (황금비) - 가장 완벽한 비율의 소리", 
                             "e (자연상수) - 성장의 멜로디"],
                            label_visibility="collapsed")
    
    if "π" in feed_pick:
        target_nums = "314159265358979323846264338327950288419716939937510"
        hashtags = "#원주율 #끝이없는 #미스테리 #3.14"
    elif "φ" in feed_pick:
        target_nums = "161803398874989484820458683436563811772030917980576"
        hashtags = "#황금비 #피보나치 #자연의소리 #Perfect"
    else:
        target_nums = "271828182845904523536028747135266249775724709369995"
        hashtags = "#자연상수 #성장 #미적분 #감성"

with tab_new:
    st.caption("숫자를 입력하면 음악이 됩니다.")
    user_val = st.text_input("숫자 입력 (예: 생일, 기념일)", placeholder="예: 19951225")
    if user_val:
        target_nums = ''.join(filter(str.isdigit, user_val))
        hashtags = "#나만의노래 #CustomTrack #수학갬성"

# [메인 비주얼 영역]
st.markdown("---")

if target_nums:
    # 앨범 커버 (차트)
    with st.container():
        st.caption("Now Playing 🎧")
        
        # 차트 데이터 생성 (비주얼라이저 느낌)
        vis_data = [int(d) for d in target_nums[:30] if d != '0']
        
        # 앨범 커버 스타일로 차트 표시
        st.area_chart(vis_data, height=200, color="#E1306C")

    # 액션 버튼 (좋아요, 공유 등)
    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        # 좋아요 기능 (세션 스테이트 사용)
        if "likes" not in st.session_state:
            st.session_state.likes = 0
            
        if st.button("❤️"):
            st.session_state.likes += 1
            
    with c2:
        st.button("💬") # 댓글 척하기
    
    with c3:
        # 재생 버튼을 크게
        play_triggered = st.button("▶️ Play Music", use_container_width=True)

    # 좋아요 수 및 캡션
    st.markdown(f"**좋아요 {st.session_state.likes}개**")
    
    # 캡션 (감성 글귀)
    st.markdown(f"""
    <span style='font-weight:bold;'>Math_DJ_Official</span> 
    숫자 뒤에 숨겨진 멜로디를 들어보세요. 당신의 숫자는 어떤 소리를 내나요? 🌌
    <br><br>
    <span style='color:#3897f0;'>{hashtags}</span>
    """, unsafe_allow_html=True)
    
    # [음악 재생 로직]
    if play_triggered:
        with st.spinner("비트 찍는 중... 💿"):
            # 기본 설정값
            bpm = 5
            octave = 4
            
            audio_data = numbers_to_melody(target_nums, bpm, octave)
            
            # 파일 변환
            virtual_file = io.BytesIO()
            write(virtual_file, 44100, (audio_data * 32767).astype(np.int16))
            
            # 오디오 플레이어 (화면 하단에 뜨게 됨)
            st.audio(virtual_file, format='audio/wav')
            
            # 다운로드 링크 제공
            st.download_button(
                label="💾 이 트랙 다운로드",
                data=virtual_file,
                file_name="Mathgram_Track.wav",
                mime="audio/wav",
                use_container_width=True
            )

else:
    st.info("👆 위에서 재생할 목록을 선택하거나 숫자를 입력해주세요.")

# [네비게이션 바 흉내]
st.markdown("<br><br>", unsafe_allow_html=True)
c_nav1, c_nav2, c_nav3, c_nav4, c_nav5 = st.columns(5)
with c_nav1: st.markdown("<div style='text-align:center;'>🏠</div>", unsafe_allow_html=True)
with c_nav2: st.markdown("<div style='text-align:center;'>🔍</div>", unsafe_allow_html=True)
with c_nav3: st.markdown("<div style='text-align:center;'>➕</div>", unsafe_allow_html=True)
with c_nav4: st.markdown("<div style='text-align:center;'>❤️</div>", unsafe_allow_html=True)
with c_nav5: st.markdown("<div style='text-align:center;'>👤</div>", unsafe_allow_html=True)
