import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Factory", page_icon="🎄", layout="wide")

# --- 2. 🎨 Christmas Design (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@400;700&family=Pretendard:wght@300;500;700&display=swap');
    
    /* [전체 배경: 포근한 아이보리 & 눈송이] */
    .stApp {
        background-color: #FDFBF7 !important;
        background-image: 
            radial-gradient(#E0E0E0 1px, transparent 1px),
            radial-gradient(#E0E0E0 1px, transparent 1px);
        background-size: 20px 20px;
        background-position: 0 0, 10px 10px;
        color: #2D3436 !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    /* [헤더 디자인] */
    .header-box {
        text-align: center; 
        padding: 40px 20px;
        background: linear-gradient(135deg, #165B33, #0B3B24);
        border-radius: 0 0 30px 30px;
        color: white;
        margin-bottom: 40px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .main-title {
        font-family: 'Gaegu', cursive; font-size: 3.5rem; font-weight: 700;
        color: #F1C40F; text-shadow: 2px 2px 0px #000; margin: 0;
    }
    
    /* [카드 스타일 - 안전한 컨테이너] */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background-color: #FFFFFF;
        border: 2px solid #EAEAEA;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* [상단 뱃지 디자인] */
    .badge-box {
        display: inline-block; padding: 5px 15px; border-radius: 20px;
        font-size: 0.9rem; font-weight: 800; color: #fff; margin-bottom: 10px;
    }
    .b-red { background-color: #D32F2F; }
    .b-green { background-color: #388E3C; }
    .b-gold { background-color: #FBC02D; color: #333; }
    .b-purple { background-color: #7B1FA2; }

    /* [선생님 설명 박스] */
    .teacher-note {
        background-color: #E8F5E9; border-left: 5px solid #2E7D32;
        padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 15px;
        font-size: 0.95rem; line-height: 1.6; color: #1B5E20;
    }

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
    button[data-baseweb="tab"] {
        background-color: #EEE !important; border-radius: 15px !important;
        border: none !important; color: #555 !important; font-weight: bold;
        padding: 8px 16px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #C0392B !important; color: #FFF !important;
    }

    /* [버튼 디자인] */
    .stButton>button {
        background: linear-gradient(to bottom, #C0392B, #922B21) !important;
        color: white !important; border: 2px solid #F1C40F !important;
        border-radius: 12px; height: 55px; font-size: 1.2rem; font-weight: 800; width: 100%;
        box-shadow: 0 4px 0 #581814;
    }
    .stButton>button:hover { transform: translateY(2px); box-shadow: 0 2px 0 #581814; }
    .stButton>button:active { transform: translateY(4px); box-shadow: none; }

    /* [입력창] */
    .stTextInput input { text-align: center; border-radius: 10px; border: 2px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div style="position:fixed; top:-10px; left:{np.random.randint(0,100)}vw; z-index:99; color:#D4AF37; opacity:0.4; font-size:{np.random.uniform(0.5,1.5)}em; animation:fall {np.random.uniform(5,15)}s linear infinite;">❄</div>' for _ in range(30)])
    st.markdown(f"<style>@keyframes fall {{ 0% {{ transform: translateY(-10vh); }} 100% {{ transform: translateY(110vh); }} }}</style>{snow_html}", unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (Final) ---

def generate_wave(freq, duration, type="bell"):
    sr = 44100; num_samples = int(sr * duration); t = np.linspace(0, duration, num_samples, False)
    if type == "bell": return 0.6*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)*np.exp(-2*t) + 0.1*np.sin(2*np.pi*freq*4*t)
    elif type == "strings": return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*0.5*t)
    elif type == "choir": return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*0.998*t)
    elif type == "sleigh": noise = np.random.uniform(-1, 1, len(t)); return 0.1 * noise * np.sin(2*np.pi*3000*t) * np.exp(-15*t)
    return np.zeros(num_samples)

def match_len(wave, length):
    if len(wave) == length: return wave
    elif len(wave) > length: return wave[:length]
    else: return np.pad(wave, (0, length - len(wave)), 'constant')

def apply_envelope(wave, duration, type="short"):
    length = len(wave)
    if type == "short": env = np.exp(np.linspace(0, -5, length))
    else:
        att = int(length * 0.2); rel = int(length * 0.3); sus = length - att - rel; 
        if sus < 0: sus = 0
        env = np.concatenate([np.linspace(0, 1, att), np.full(sus, 1.0), np.linspace(1, 0, rel)])
    env = match_len(env, length); return wave * env

def compose_music(nums, bpm, style):
    # Scale Expansion (Error Prevention)
    if style == "joyful": scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    elif style == "waltz": scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    else: scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    
    beat_sec = 60.0 / bpm; full_track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit); base_freq = scale[idx % len(scale)]
        
        notes = []
        if style == "joyful": 
            if idx % 2 == 0: notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)]
            else: notes = [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        elif style == "waltz": notes = [(base_freq, 1.0), (base_freq*1.25, 1.0), (base_freq*1.5, 1.0)]
        else: notes = [(base_freq, 4.0)]
            
        melody_waves = []
        for f, d in notes:
            dur = d * beat_sec
            w = generate_wave(f, dur, "bell" if style != "holy" else "choir")
            w = apply_envelope(w, dur, "short" if style != "holy" else "long")
            melody_waves.append(w)
        melody = np.concatenate(melody_waves); total_len = len(melody)
        
        pad = generate_wave(base_freq * 0.5, total_len/44100, "strings"); pad = match_len(pad, total_len)
        pad = apply_envelope(pad, total_len/44100, "long") * 0.35
        
        sleigh = generate_wave(0, total_len/44100, "sleigh"); sleigh = match_len(sleigh, total_len) * 0.3 if style == "joyful" else np.zeros(total_len)
        full_track.append(melody + pad + sleigh)
        
    if not full_track: return None
    full = np.concatenate(full_track); delay = int(44100 * 0.4); res = np.zeros(len(full) + delay); res[:len(full)] += full; res[delay:] += full * 0.4
    m = np.max(np.abs(res)); return res / m * 0.95 if m > 0 else res

# --- 4. UI 렌더링 함수 ---

def render_card(key, badge_cls, badge_txt, title, subtitle, desc, default_nums, style, color_scheme):
    
    # 2열 구조: 왼쪽(설명) / 오른쪽(비주얼+버튼)
    c1, c2 = st.columns([1, 1], gap="medium")
    
    with c1:
        # [안전한 컨테이너 사용] HTML 깨짐 방지
        with st.container():
            st.markdown(f'<span class="badge-box {badge_cls}">{badge_txt}</span>', unsafe_allow_html=True)
            st.markdown(f"### {title}")
            st.markdown(f"**{subtitle}**")
            
            st.markdown(f"""
            <div class="teacher-note">
                <b>🧑‍🏫 선생님의 이야기:</b><br>
                {desc}
            </div>
            """, unsafe_allow_html=True)
            
            # 4번 탭 전용 입력창
            final_nums = default_nums
            final_style = style
            
            if key == "t4":
                st.markdown("---")
                user_input = st.text_input("숫자를 입력하세요 (예: 1225)", value="", key=f"in_{key}")
                if user_input: final_nums = "".join(filter(str.isdigit, user_input))
                
                s_opt = st.radio("스타일", ["Joyful (신남)", "Waltz (우아함)", "Holy (웅장함)"], key=f"s_{key}")
                if "Joyful" in s_opt: final_style = "joyful"; color_scheme = "reds"
                elif "Waltz" in s_opt: final_style = "waltz"; color_scheme = "greens"
                else: final_style = "holy"; color_scheme = "oranges"

    with c2:
        with st.container():
            st.markdown("##### 🎄 멜로디 트리")
            
            if final_nums:
                digits = [int(d) for d in final_nums[:30] if d != '0']
                tree_data = []
                idx = 0; layer = 1; max_layers = 10 
                while idx < len(digits) and layer <= max_layers:
                    nodes = layer
                    for i in range(nodes):
                        if idx >= len(digits): break
                        note = digits[idx]
                        y = 10 - layer 
                        width = layer * 1.8
                        x = np.linspace(-width/2, width/2, nodes)[i]
                        size = note * 50 + 100
                        tree_data.append({'x': x, 'y': y, 'note': note, 'size': size})
                        idx += 1
                    layer += 1
                
                df = pd.DataFrame(tree_data)
                star = pd.DataFrame({'x': [0], 'y': [10], 'note': [10], 'size': [600]})
                
                base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=1.5).encode(
                    x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                    size=alt.Size('size', legend=None),
                    color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                    tooltip=['note']
                )
                top = alt.Chart(star).mark_point(shape='star', fill='#F1C40F', size=600, stroke='none').encode(x='x', y='y')
                
                final_chart = (base + top).properties(height=300).configure_view(strokeWidth=0)
                st.altair_chart(final_chart, use_container_width=True)

            # 재생 버튼 (컨테이너 밖으로 빼서 안전하게 배치)
            st.write("")
            if st.button(f"🔔 재생하기 ({final_style.title()})", key=f"btn_{key}"):
                with st.spinner("음악 생성 중..."):
                    bpm = 120 if final_style == "joyful" else 100 if final_style == "waltz" else 80
                    audio = compose_music(final_nums, bpm, final_style)
                    if audio is not None:
                        virtual_file = io.BytesIO()
                        write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                        st.audio(virtual_file, format='audio/wav')

# --- Main Page ---
st.markdown("""
<div class="header-box">
    <h1 class="main-title">Merry Math Class</h1>
    <div class="sub-title">🎄 중학교 수학으로 만드는 나만의 크리스마스 캐롤 🎄</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["중1 (도형)", "중2 (수)", "중3 (무리수)", "자유 탐구"])

with t1:
    render_card("t1", "b-red", "중1 - 도형의 성질", "원주율(π) 징글벨", "3.141592...", 
        """
        원은 완벽한 대칭이지만, 그 비율인 파이(π)는 불규칙하게 끝없이 이어져요.
        이 숫자들을 <b>경쾌한 셔플 리듬</b>으로 연주하면, 
        마치 <b>눈길을 달리는 썰매 소리</b>처럼 신나는 캐롤이 된답니다!
        """, "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_card("t2", "b-green", "중2 - 유리수와 순환소수", "순환소수 왈츠", "0.142857...", 
        """
        1/7 = 0.142857... 처럼 같은 숫자가 계속 반복되는 수를 '순환소수'라고 해요.
        이 규칙적인 반복은 <b>우아한 3박자 왈츠(Waltz)</b> 리듬과 잘 어울려요.
        숫자들이 춤추는 모습을 상상해보세요.
        """, "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_card("t3", "b-gold", "중3 - 제곱근과 실수", "루트2의 거룩한 밤", "1.414213...", 
        """
        제곱해서 2가 되는 수, 루트2(√2)는 끝을 알 수 없는 신비로운 '무리수'입니다.
        이 숫자의 깊이를 <b>웅장한 합창(Choir)</b>으로 표현했어요.
        고요하고 성스러운 겨울밤 느낌이 나나요?
        """, "141421356237309504880168872420969807856967187537694", "holy", "oranges")

with t4:
    render_card("t4", "b-purple", "자유 학기제", "나만의 숫자 캐롤", "Make Your Own Carol", 
        """
        수학은 어디에나 있어요! 1225(크리스마스)나 여러분의 생일, 전화번호를 입력해보세요.
        아래에서 <b>음악 스타일</b>을 고르면, 세상에 하나뿐인 캐롤이 완성됩니다.
        """, "12251225", "joyful", "purples")

st.markdown("<br><div style='text-align:center; color:#999; font-size:0.8rem;'>Designed for Joyful Math Education • 2025 Winter</div>", unsafe_allow_html=True)
