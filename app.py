import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Village", page_icon="🎄", layout="wide")

# --- 2. 🎨 Warm Winter Design (CSS) ---
st.markdown("""
<style>
    /* [폰트] 제목: 감성적인 명조 / 본문: 깔끔한 고딕 */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Pretendard:wght@300;500;700&display=swap');
    
    /* [전체 배경: 따뜻한 겨울밤의 마을] */
    .stApp {
        background-color: #1a2e35 !important; /* 딥 그린 블루 */
        background-image: radial-gradient(circle at 50% 10%, #2c5364 0%, #0f2027 100%);
        color: #f1f2f6 !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    /* [눈 효과: 금빛 눈송이] */
    .snowflake { position: fixed; top: -10px; z-index: 0; color: rgba(255,215,0,0.3); font-size: 0.8em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [헤더] */
    .village-header {
        text-align: center; padding: 50px 0 30px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 40px;
    }
    .main-title {
        font-family: 'Gowun Batang', serif; font-size: 3.5rem; font-weight: 700;
        color: #f1c40f; text-shadow: 0 4px 15px rgba(0,0,0,0.3); letter-spacing: -1px; margin-bottom: 10px;
    }
    .sub-title {
        color: #bdc3c7; font-size: 1.1rem; letter-spacing: 1px; font-weight: 300;
    }

    /* [컨텐츠 카드: 따뜻한 편지지 느낌] */
    .letter-card {
        background-color: #fffaf0; /* 아이보리 */
        border-top: 5px solid #c0392b; /* 크리스마스 레드 */
        border-radius: 12px;
        padding: 30px;
        color: #2d3436;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 25px;
        position: relative;
    }
    .letter-card::before { /* 우표 장식 효과 */
        content: "🎅 Math"; position: absolute; top: -15px; right: 20px;
        background: #27ae60; color: white; padding: 5px 15px;
        border-radius: 5px; font-weight: bold; font-size: 0.8rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    /* [선생님 말씀 박스] */
    .teacher-note {
        background-color: #e8f5e9; /* 연한 초록 배경 */
        border: 1px dashed #27ae60;
        border-radius: 10px; padding: 20px;
        margin-top: 20px; font-size: 1rem; line-height: 1.7; color: #1e4d2b;
    }
    .teacher-badge {
        background-color: #27ae60; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px;
    }

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { gap: 15px; justify-content: center; }
    button[data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.1) !important; color: #aaa !important; border: none !important;
        font-family: 'Gowun Batang', serif; font-weight: bold; font-size: 1.1rem;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #c0392b !important; color: #fff !important;
        border-radius: 8px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* [재생 버튼] */
    .stButton>button {
        background: linear-gradient(135deg, #c0392b 0%, #a93226 100%) !important;
        color: #fff !important; border: 2px solid #e74c3c !important;
        border-radius: 50px; height: 65px; font-size: 1.3rem; font-weight: 700; width: 100%;
        box-shadow: 0 5px 15px rgba(192, 57, 43, 0.4); transition: all 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(192, 57, 43, 0.5); }

    /* [입력창] */
    .stTextInput input {
        background-color: #fff; border: 2px solid #dcdcdc; border-radius: 8px;
        text-align: center; color: #333; font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(10, 25)}s; animation-delay:{np.random.uniform(0, 10)}s;">❄</div>' for _ in range(40)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Advanced Audio Engine (풍성한 캐롤 사운드) ---

# 기본 파형 생성기 (악기별 특징 구현)
def get_instrument_wave(freq, duration, instrument):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), False)
    
    if instrument == "bell": # 영롱한 벨소리 (Joyful)
        # 기본음 + 비정수 배음(금속성) + 빠른 감쇠
        wave = 0.5*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2.05*t)*np.exp(-2*t) + 0.2*np.sin(2*np.pi*freq*3.98*t)*np.exp(-4*t)
        envelope = np.exp(-3 * t)
        return wave * envelope
        
    elif instrument == "piano": # 따뜻한 피아노 (Waltz)
        # 배음이 풍부한 사인파 조합
        wave = 0.6*np.sin(2*np.pi*freq*t) + 0.2*np.sin(2*np.pi*freq*2*t) + 0.1*np.sin(2*np.pi*freq*3*t)
        envelope = np.exp(-1.5 * t)
        return wave * envelope
        
    elif instrument == "strings": # 배경에 깔리는 현악기 (Pad)
        # 여러 주파수를 섞어 두꺼운 소리
        wave = 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*2*t)
        # 부드럽게 시작했다가 끝남 (ASDR)
        total = len(t)
        att, rel = int(total*0.3), int(total*0.3)
        sus = total - att - rel
        if sus < 0: sus = 0
        env = np.concatenate([np.linspace(0,1,att), np.full(sus,1.0), np.linspace(1,0,rel)])
        # 길이 보정
        if len(env) != total: env = np.resize(env, total)
        return wave * env
        
    elif instrument == "sleigh": # 썰매 방울 소리 (Noise)
        noise = np.random.uniform(-1, 1, len(t))
        wave = 0.1 * noise * np.sin(2*np.pi*3000*t) * np.exp(-15*t)
        return wave

    return np.zeros_like(t)

# 길이 맞춤 (필수)
def match_len(wave, target_len):
    if len(wave) == target_len: return wave
    elif len(wave) > target_len: return wave[:target_len]
    else: return np.pad(wave, (0, target_len - len(wave)), 'constant')

# 작곡 로직 (화음 + 리듬 + 베이스)
def compose_rich_music(nums, bpm, style):
    # 스케일 설정 (겨울 느낌의 D Major / Holy는 B Minor)
    if style == "joyful": 
        scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99] # D Major
    elif style == "waltz":
        scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25] # C Major
    else: # Holy
        scale = [246.94, 277.18, 293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33] # B Minor

    beat_sec = 60.0 / bpm
    full_track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit)
        base_freq = scale[idx % len(scale)]
        
        # --- 1. 멜로디 파트 (Rhythm Variation) ---
        melody_waves = []
        if style == "joyful": # 셔플 리듬 (징글벨)
            # 패턴: 딴.따.단 (점8분 - 16분 - 4분)
            durations = [0.75, 0.25, 1.0]
            freqs = [base_freq, base_freq, base_freq * 1.25] # 마지막 음 도약
            inst = "bell"
        elif style == "waltz": # 3/4 박자
            # 패턴: 쿵-짝-짝
            durations = [1.0, 1.0, 1.0]
            freqs = [base_freq, base_freq * 1.25, base_freq * 1.5] # 아르페지오
            inst = "piano"
        else: # Holy (느린 4박자)
            durations = [4.0]
            freqs = [base_freq]
            inst = "strings" # 합창 느낌

        for f, d in zip(freqs, durations):
            w = get_instrument_wave(f, d * beat_sec, inst)
            melody_waves.append(w)
            
        melody = np.concatenate(melody_waves)
        total_len = len(melody)
        
        # --- 2. 반주 파트 (Harmony & Bass) ---
        # 화음 (3도 위)
        chord_freq = scale[(idx + 2) % len(scale)]
        pad = get_instrument_wave(chord_freq * 0.5, total_len/44100, "strings")
        pad = match_len(pad, total_len) * 0.4 # 볼륨 낮춤
        
        # 베이스 (근음 1옥타브 아래)
        bass = get_instrument_wave(base_freq * 0.5, total_len/44100, "strings") # 첼로 느낌
        bass = match_len(bass, total_len) * 0.5
        
        # 썰매 방울 (Joyful일 때만)
        sleigh = np.zeros(total_len)
        if style == "joyful":
            sleigh = get_instrument_wave(0, total_len/44100, "sleigh")
            sleigh = match_len(sleigh, total_len) * 0.4
            
        # 믹싱
        mix = melody + pad + bass + sleigh
        full_track.append(mix)
        
    if not full_track: return None
    
    # 전체 연결 및 리버브(공간감) 추가
    full_audio = np.concatenate(full_track)
    
    # Simple Reverb (Echo)
    delay = int(44100 * 0.4)
    res = np.zeros(len(full_audio) + delay)
    res[:len(full_audio)] += full_audio
    res[delay:] += full_audio * 0.3 # 에코 추가
    
    # 노멀라이즈 (소리 깨짐 방지)
    m = np.max(np.abs(res))
    return res / m * 0.9 if m > 0 else res

# --- 4. UI 렌더링 ---

def render_tab(key, title, subtitle, desc, default_nums, style, color_scheme):
    c1, c2 = st.columns([1, 1.2], gap="large")
    
    with c1:
        st.markdown(f"""
        <div class="letter-card">
            <h2 style="margin-top:0; color:#c0392b; font-family:'Gowun Batang';">{title}</h2>
            <div style="color:#7f8c8d; font-weight:bold; margin-bottom:20px;">{subtitle}</div>
            
            <div class="teacher-note">
                <span class="teacher-badge">Math & Music</span>
                {desc}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        final_style = style
        
        if key == "t4":
            st.markdown("##### 🎹 나만의 캐롤 만들기")
            user_input = st.text_input("숫자를 입력하세요 (예: 1225)", value="", key=f"in_{key}")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))
            
            style_opt = st.radio("분위기 선택", ["Joyful (신나는 썰매)", "Waltz (우아한 파티)", "Holy (거룩한 밤)"], key=f"st_{key}")
            if "Joyful" in style_opt: final_style = "joyful"
            elif "Waltz" in style_opt: final_style = "waltz"
            else: final_style = "holy"

    with c2:
        st.markdown('<div class="letter-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("### 🎄 Christmas Melody Tree")
        
        if final_nums:
            # [Visual] 트리 모양 비주얼라이저
            digits = [int(d) for d in final_nums[:30] if d != '0']
            tree_data = []
            
            layer = 1; idx = 0; max_layers = 8
            while idx < len(digits) and layer <= max_layers:
                for i in range(layer):
                    if idx >= len(digits): break
                    note = digits[idx]
                    y = 10 - layer 
                    width = layer * 1.5
                    x = np.linspace(-width/2, width/2, layer)[i]
                    size = note * 50 + 150
                    tree_data.append({'x': x, 'y': y, 'note': note, 'size': size})
                    idx += 1
                layer += 1
                
            df = pd.DataFrame(tree_data)
            star = pd.DataFrame({'x': [0], 'y': [10], 'note': [10], 'size': [800]})
            
            # 차트
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=2).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='#f1c40f', size=800, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=350, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)

        st.write("")
        if st.button(f"🔔 캐롤 재생 (Play)", key=f"btn_{key}"):
            with st.spinner("산타가 악보를 연주합니다... 🎼"):
                bpm = 120 if final_style == "joyful" else 100 if final_style == "waltz" else 80
                audio = compose_rich_music(final_nums, bpm, final_style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page ---
st.markdown("""
<div class="village-header">
    <div class="main-title">Winter Math Village</div>
    <div class="sub-title">중학교 수학 교과서 속 숫자들이 들려주는 크리스마스 이야기</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["중1 도형", "중2 유리수", "중3 무리수", "자유 탐구"])

with t1:
    render_tab("t1", "원주율(π) 징글벨", "중1 - 도형의 성질", 
        """
        <b>"원은 완벽한 대칭이지만, 그 속엔 끝없는 숫자가 숨어있단다."</b><br><br>
        원주율(3.14...)은 규칙 없이 영원히 이어지는 비순환 소수예요. 
        이 불규칙한 숫자들을 <b>경쾌한 셔플 리듬</b>으로 연주하면, 
        마치 <b>울퉁불퉁한 눈길을 달리는 썰매 소리</b>처럼 신나는 캐롤이 된답니다! 🛷
        """, "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_tab("t2", "순환소수 왈츠", "중2 - 유리수와 순환소수", 
        """
        <b>"규칙적으로 반복되는 숫자의 춤을 들어볼까?"</b><br><br>
        1/7 = 0.142857... 처럼 같은 숫자가 도돌이표처럼 반복되는 수를 '순환소수'라고 해요.
        이 규칙적인 패턴은 춤추기 좋은 <b>우아한 3박자 왈츠(Waltz)</b>와 완벽하게 어울립니다.
        함께 춤을 추는 느낌을 상상해보세요. 💃
        """, "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_tab("t3", "루트2의 거룩한 밤", "중3 - 제곱근과 실수", 
        """
        <b>"세상의 비밀을 담은 깊고 신비로운 수야."</b><br><br>
        제곱해서 2가 되는 수, 루트2(1.414...)는 인류가 처음 발견한 '무리수'입니다.
        끝을 알 수 없는 이 숫자의 깊은 울림을 <b>웅장한 합창(Choir)</b>으로 표현했어요.
        고요하고 성스러운 겨울밤에 어울리는 소리입니다. 🕯️
        """, "141421356237309504880168872420969807856967187537694", "holy", "oranges")

with t4:
    render_tab("t4", "나만의 숫자 캐롤", "자유 학기제 - 창의 탐구", 
        """
        <b>"여러분의 숫자도 아름다운 음악이 될 수 있어요!"</b><br><br>
        1225(크리스마스)나 여러분의 생일, 전화번호를 입력해보세요.
        수학적 규칙(알고리즘)이 여러분의 소중한 숫자를 
        <b>세상에 하나뿐인 캐롤</b>로 바꿔줄 거예요.
        """, "12251225", "joyful", "purples")

st.markdown("<br><hr><div style='text-align:center; color:#7f8c8d; font-size:0.9rem;'>Designed for Joyful Math Education • 2025 Winter</div>", unsafe_allow_html=True)
