import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Magic", page_icon="🎄", layout="wide")

# --- 2. 🎨 Christmas Magic Design (CSS) ---
st.markdown("""
<style>
    /* [폰트 불러오기] 눈 쌓인 느낌의 폰트 추가 */
    @import url('https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@700&family=Noto+Sans+KR:wght@300;500;700&display=swap');
    
    /* [전체 배경: 오로라 + 화이트 글래스] */
    .stApp {
        background: linear-gradient(-45deg, #c0392b, #f39c12, #27ae60, #2980b9);
        background-size: 400% 400%; animation: gradient 20s ease infinite;
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    @keyframes gradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(255, 255, 255, 0.9); /* 더 밝은 화이트 레이어 */
        z-index: -1;
    }

    /* [눈 내리는 효과] */
    .snowflake { position: fixed; top: -10px; z-index: 99; color: #fff; text-shadow: 0 0 5px rgba(0,0,0,0.2); animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [타이틀 디자인 - 크리스마스 분위기 UP!] */
    .main-title {
        font-family: 'Mountains of Christmas', cursive; /* 크리스마스 폰트 */
        font-size: 5rem; font-weight: 700;
        text-align: center; color: #d35400; /* 따뜻한 오렌지 레드 */
        margin-top: 20px;
        /* 눈 쌓인 듯한 텍스트 그림자 효과 */
        text-shadow: 
            3px 3px 0 #fff,
            5px 5px 0 #c0392b,
            7px 7px 5px rgba(0,0,0,0.3);
        letter-spacing: 2px;
    }
    .sub-title {
        text-align: center; color: #555; font-size: 1.2rem; letter-spacing: 2px;
        text-transform: uppercase; margin-bottom: 40px; font-weight: 600;
    }

    /* [유리 카드 디자인] */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border: 2px solid rgba(255, 255, 255, 0.8); /* 테두리 강조 */
        border-radius: 24px; padding: 40px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px; transition: transform 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-5px); border-color: #fff; box-shadow: 0 25px 50px rgba(0,0,0,0.1); }

    /* [탭 스타일] */
    div[data-baseweb="tab-list"] { gap: 15px; margin-bottom: 30px; justify-content: center; }
    button[data-baseweb="tab"] {
        background: rgba(255,255,255,0.5) !important; border: 1px solid #ddd !important; border-radius: 30px !important;
        padding: 10px 25px !important; color: #777 !important; font-weight: 600 !important; font-size: 1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: #c0392b !important; color: #fff !important; border-color: #c0392b !important;
        box-shadow: 0 5px 15px rgba(192, 57, 43, 0.3) !important;
    }

    /* [재생 버튼 - 선물 상자 느낌] */
    .stButton>button {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%) !important;
        color: #fff !important; border: 3px solid #f1c40f !important; /* 금테 두름 */
        height: 70px; border-radius: 20px;
        font-size: 1.5rem; font-weight: 800; width: 100%;
        box-shadow: 0 10px 25px rgba(192, 57, 43, 0.3); transition: all 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 15px 35px rgba(192, 57, 43, 0.4); background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important; }

    /* [교육용 뱃지] */
    .badge {
        display: inline-block; padding: 8px 16px; border-radius: 25px;
        font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .b-red { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    .b-green { background: linear-gradient(135deg, #2ecc71, #27ae60); }
    .b-gold { background: linear-gradient(135deg, #f1c40f, #f39c12); color: #2d3436; }
    .b-purple { background: linear-gradient(135deg, #9b59b6, #8e44ad); }

    /* [설명 텍스트] */
    .desc-text { color: #555; line-height: 1.8; font-size: 1.1rem; }
    .desc-text b { color: #c0392b; background: rgba(192, 57, 43, 0.1); padding: 2px 5px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(10, 25)}s; animation-delay:{np.random.uniform(0, 15)}s; font-size:{np.random.uniform(0.8, 1.5)}em;">❄</div>' for _ in range(50)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (동일하게 유지) ---
# (오디오 엔진 코드는 이전과 동일하여 생략합니다. 실제 실행 시에는 포함되어야 합니다.)
def generate_wave(freq, duration, type="bell"):
    sr = 44100; num_samples = int(sr * duration); t = np.linspace(0, duration, num_samples, False)
    if type == "bell": return 0.6*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*2*t)*np.exp(-2*t) + 0.1*np.sin(2*np.pi*freq*4*t)
    elif type == "strings": return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*1.01*t) + 0.2*np.sin(2*np.pi*freq*0.5*t)
    elif type == "choir": return 0.3*np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*freq*0.998*t) + 0.3*np.sin(2*np.pi*freq*1.002*t)
    elif type == "sleigh": noise = np.random.uniform(-1, 1, len(t)); return 0.1 * noise * np.sin(2*np.pi*3000*t) * np.exp(-15*t)
    return np.zeros(num_samples)
def match_len(wave, length):
    if len(wave) == length: return wave
    elif len(wave) > length: return wave[:length]
    else: return np.pad(wave, (0, length - len(wave)), 'constant')
def apply_envelope(wave, duration, type="short"):
    length = len(wave)
    if type == "short": env = np.exp(np.linspace(0, -5, length))
    else: att = int(length*0.2); rel = int(length*0.3); sus = length - att - rel; if sus < 0: sus = 0; env = np.concatenate([np.linspace(0,1,att), np.full(sus,1.0), np.linspace(1,0,rel)])
    env = match_len(env, length); return wave * env
def compose_music(nums, bpm, style):
    if style == "joyful": scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    elif style == "waltz": scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    else: scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    beat_sec = 60.0 / bpm; full_track = []
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit); base_freq = scale[idx % len(scale)]
        if style == "joyful": notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)] if idx % 2 == 0 else [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        elif style == "waltz": notes = [(base_freq, 1.0), (base_freq*1.25, 1.0), (base_freq*1.5, 1.0)]
        else: notes = [(base_freq, 4.0)]
        melody_waves = []
        for f, d in notes: dur = d * beat_sec; w = generate_wave(f, dur, "bell" if style != "holy" else "choir"); w = apply_envelope(w, dur, "short" if style != "holy" else "long"); melody_waves.append(w)
        melody = np.concatenate(melody_waves); total_len = len(melody)
        pad_freq = base_freq * 0.5; pad = generate_wave(pad_freq, total_len/44100, "strings"); pad = match_len(pad, total_len); pad = apply_envelope(pad, total_len/44100, "long") * 0.3
        sleigh = generate_wave(0, total_len/44100, "sleigh"); sleigh = match_len(sleigh, total_len) * 0.3 if style == "joyful" else np.zeros(total_len)
        full_track.append(melody + pad + sleigh)
    if not full_track: return None
    full = np.concatenate(full_track); delay = int(44100 * 0.4); res = np.zeros(len(full) + delay); res[:len(full)] += full; res[delay:] += full * 0.4
    m = np.max(np.abs(res)); return res / m * 0.95 if m > 0 else res

# --- 4. UI Logic ---

def render_tab(key_prefix, badge_cls, badge_text, title, desc, default_nums, style):
    c1, c2 = st.columns([1, 1.1], gap="large") # 오른쪽 컬럼을 약간 더 넓게
    
    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <span class="badge {badge_cls}">{badge_text}</span>
            <h2 style="color:#c0392b; margin:15px 0; font-family:'Mountains of Christmas', cursive; font-size:2.5rem;">{title}</h2>
            <div class="desc-text">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        if key_prefix == "t4":
            user_input = st.text_input("숫자를 입력하세요 (예: 20251225)", value="", key=f"in_{key_prefix}")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))

    with c2:
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        
        # [VISUAL UPGRADE] 입체적인 장식볼 트리
        if final_nums:
            digits = [int(d) for d in final_nums[:35] if d != '0']
            tree_data = []
            max_width = 12
            height_scale = 1.8
            
            for i, d in enumerate(digits):
                level = d * height_scale # 높은 음 = 위쪽
                spread = (10 - d) * max_width / 10 # 낮은 음 = 넓게 퍼짐
                pos = spread * (1 if i % 2 == 0 else -1) * np.random.uniform(0.4, 1.0)
                # [NEW] 크기(Size)를 음계(Note)에 비례하게 설정
                size = d * 80 + 200 # 최소 200, 최대 1000 정도
                tree_data.append({'Level': level, 'Pos': pos, 'Note': d, 'Size': size})
            
            df = pd.DataFrame(tree_data)
            
            color_map = {'t1': 'reds', 't2': 'greens', 't3': 'oranges', 't4': 'purples'}
            
            # [레이어링을 통한 입체 효과]
            # 1. 기본 원 (불투명)
            base = alt.Chart(df).mark_circle(opacity=0.8).encode(
                x=alt.X('Pos', axis=None), y=alt.Y('Level', axis=None, scale=alt.Scale(domain=[0, 13*height_scale])),
                size=alt.Size('Size', legend=None), # 크기 적용
                color=alt.Color('Note', scale=alt.Scale(scheme=color_map[key_prefix]), legend=None),
                tooltip=['Note']
            )
            
            # 2. 빛 번짐 효과 (더 크고 반투명한 원)
            glow = alt.Chart(df).mark_circle(opacity=0.3).encode(
                x=alt.X('Pos', axis=None), y=alt.Y('Level', axis=None),
                size=alt.Size('Size', legend=None, scale=alt.Scale(range=[400, 1500])), # 더 크게
                color=alt.Color('Note', scale=alt.Scale(scheme=color_map[key_prefix]), legend=None)
            )
            
            # 3. 하이라이트 (중심부 밝은 빛)
            highlight = alt.Chart(df).mark_circle(opacity=0.6, color='white').encode(
                x=alt.X('Pos', axis=None), y=alt.Y('Level', axis=None),
                size=alt.Size('Size', legend=None, scale=alt.Scale(range=[50, 300])) # 작게
            )
            
            # 레이어 결합
            chart = alt.layer(glow, base, highlight).properties(height=350).configure_view(strokeWidth=0)
            
            st.altair_chart(chart, use_container_width=True)
            st.caption("▲ 음계의 높낮이에 따라 빛나는 크리스마스 장식볼 트리")

        # 재생 버튼
        if st.button(f"🔔 캐롤 재생 (Play)", key=f"btn_{key_prefix}"):
            with st.spinner("캐롤 편곡 중..."):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page ---
st.markdown('<div class="main-title">CHRISTMAS MATH CAROL</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🎄 수학으로 장식하는 나만의 멜로디 트리 🎄</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🔴 1학년 (도형)", "🟢 2학년 (수)", "🟡 3학년 (무리수)", "🟣 나만의 숫자"])

with tab1:
    render_tab("t1", "b-red", "중1 - 도형의 성질", "원주율 (Pi) 징글벨", 
               "<b>3.141592...</b><br>원주율의 불규칙한 숫자들이 <b>경쾌한 셔플 리듬</b>과 만나 썰매를 타는 듯한 신나는 캐롤이 됩니다! 높은 숫자는 트리의 빛나는 별이 됩니다.", 
               "314159265358979323846264338327950288419716939937510", "joyful")

with tab2:
    render_tab("t2", "b-green", "중2 - 순환소수", "순환소수 왈츠", 
               "<b>0.142857...</b><br>순환소수의 규칙적인 반복은 <b>우아한 3박자 왈츠</b>와 어우러져 몽환적인 춤곡을 만듭니다. 반복되는 숫자는 트리의 같은 위치에서 반짝입니다.", 
               "142857142857142857142857142857142857142857", "waltz")

with tab3:
    render_tab("t3", "b-gold", "중3 - 무리수", "루트2 홀리 나이트", 
               "<b>1.414213...</b><br>무리수의 깊고 신비로운 배열이 <b>웅장한 합창(Choir)</b>과 만나 성스러운 겨울밤을 연출합니다. 트리의 아래쪽을 든든하게 받쳐주는 숫자들입니다.", 
               "141421356237309504880168872420969807856967187537694", "holy")

with tab4:
    render_tab("t4", "b-purple", "자유학기제", "나만의 숫자 캐롤", 
               "<b>Make Your Own Music</b><br>소중한 숫자를 입력해보세요. 세상에 하나뿐인 캐롤로 변환됩니다. 당신의 숫자가 트리의 가장 빛나는 장식이 될 거예요.", 
               "12251225", "joyful")

st.markdown("<br><div style='text-align:center; color:#bbb; font-weight:600;'>🎁 Designed for Joyful Math Education 🎁</div>", unsafe_allow_html=True)
