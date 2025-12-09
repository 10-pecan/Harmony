import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Winter Class", page_icon="🏫", layout="wide")

# --- 2. 🎨 Classroom Christmas Design (CSS) ---
st.markdown("""
<style>
    /* [폰트] 칠판 글씨체(Gamja Flower) + 본문 고딕(Noto Sans) */
    @import url('https://fonts.googleapis.com/css2?family=Gamja+Flower&family=Noto+Sans+KR:wght@400;700&display=swap');
    
    /* [전체 배경: 깊은 초록색 칠판] */
    .stApp {
        background-color: #1e3b28 !important;
        background-image: radial-gradient(circle at center, #254a33 0%, #172e1f 100%);
        color: #f1f2f6 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* [눈 효과: 분필 가루처럼 은은하게] */
    .snowflake { position: fixed; top: -10px; z-index: 99; color: rgba(255,255,255,0.6); font-size: 1em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [헤더: 칠판 상단 제목] */
    .board-header {
        text-align: center; margin-top: 20px; margin-bottom: 40px;
        border-bottom: 2px dashed #8FBC8F; padding-bottom: 20px;
    }
    .main-title {
        font-family: 'Gamja Flower', cursive; font-size: 4rem; color: #ffdd59; /* 분필 노랑 */
        text-shadow: 2px 2px 0px #2f3542; margin: 0;
    }
    .sub-title {
        font-family: 'Noto Sans KR', sans-serif; font-size: 1.2rem; color: #dcdcdc; 
        background-color: rgba(0,0,0,0.2); display: inline-block; padding: 5px 20px; border-radius: 20px; margin-top: 10px;
    }

    /* [카드 디자인: 칠판에 붙인 학습지] */
    .paper-card {
        background-color: #fffbf0; /* 미색 종이 */
        border-radius: 10px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3); /* 그림자 */
        padding: 30px; margin-bottom: 25px;
        color: #2d3436;
        position: relative;
    }
    /* 상단 테이프/압정 효과 */
    .paper-card::before {
        content: ""; position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
        width: 100px; height: 25px; background-color: rgba(255,255,255,0.4); box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        transform: translateX(-50%) rotate(-2deg);
    }

    /* [뱃지: 교과 단원 태그] */
    .subject-tag {
        display: inline-block; padding: 5px 12px; border-radius: 5px; 
        font-weight: 700; font-size: 0.9rem; color: #fff; margin-bottom: 15px;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.1);
    }
    .tag-1 { background-color: #e55039; } /* 중1 레드 */
    .tag-2 { background-color: #27ae60; } /* 중2 그린 */
    .tag-3 { background-color: #f39c12; } /* 중3 오렌지 */
    .tag-4 { background-color: #8e44ad; } /* 자유 보라 */

    /* [선생님 설명 박스] */
    .teacher-talk {
        background-color: #eafef1; /* 연한 초록색 노트 */
        border-left: 5px solid #27ae60;
        padding: 15px; margin-top: 15px; border-radius: 5px;
        font-size: 1rem; line-height: 1.6; color: #2d3436;
    }
    .teacher-talk b { color: #c0392b; }

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    button[data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.1) !important; color: #bbb !important; 
        border: 1px solid #555 !important; border-radius: 8px !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #fffbf0 !important; color: #2d3436 !important; 
        border: 2px solid #ffdd59 !important; font-weight: bold !important;
    }

    /* [버튼] */
    .stButton>button {
        background: linear-gradient(to bottom, #c0392b, #b3392b) !important;
        color: white !important; border: 2px solid #ecf0f1 !important; border-radius: 12px;
        height: 60px; font-size: 1.2rem; font-weight: bold; width: 100%;
        box-shadow: 0 4px 0 #802820; transition: all 0.1s;
    }
    .stButton>button:hover { transform: translateY(2px); box-shadow: 0 2px 0 #802820; }
    .stButton>button:active { transform: translateY(4px); box-shadow: none; }

    /* [입력창] */
    .stTextInput input {
        background-color: #fff; border: 2px solid #bdc3c7; border-radius: 8px; 
        text-align: center; color: #2d3436; font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# 눈 효과 JS
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(8, 20)}s; animation-delay:{np.random.uniform(0, 10)}s;">❄</div>' for _ in range(40)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (안정성 확보) ---

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
    else:
        att = int(length*0.2); rel = int(length*0.3); sus = length - att - rel
        if sus < 0: sus = 0
        env = np.concatenate([np.linspace(0, 1, att), np.full(sus, 1.0), np.linspace(1, 0, rel)])
    env = match_len(env, length); return wave * env

def compose_music(nums, bpm, style):
    # Scale: C Major / D Major / A Minor
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
        pad = apply_envelope(pad, total_len/44100, "long") * 0.3
        
        sleigh = generate_wave(0, total_len/44100, "sleigh"); sleigh = match_len(sleigh, total_len) * 0.3 if style == "joyful" else np.zeros(total_len)
        
        full_track.append(melody + pad + sleigh)
        
    if not full_track: return None
    full = np.concatenate(full_track); delay = int(44100 * 0.4); res = np.zeros(len(full) + delay); res[:len(full)] += full; res[delay:] += full * 0.4
    m = np.max(np.abs(res)); return res / m * 0.95 if m > 0 else res

# --- 4. UI 렌더링 함수 (안전한 HTML 처리) ---

def render_tab_content(key, badge_class, badge_text, title, desc, default_nums, style, color_scheme):
    c1, c2 = st.columns([1, 1.1], gap="large")
    
    with c1:
        # [HTML] 카드 UI (닫는 태그 오류 방지)
        st.markdown(f"""
        <div class="paper-card">
            <span class="subject-tag {badge_class}">{badge_text}</span>
            <h2 style="margin: 5px 0 15px 0; color:#2d3436; font-size:2rem; font-family:'Gamja Flower', cursive;">{title}</h2>
            <div class="teacher-talk">
                <b>🧑‍🏫 선생님의 한마디:</b><br>
                {desc}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        
        # 4번째 탭 커스텀 입력
        if key == "t4":
            st.markdown('<div class="paper-card" style="padding:20px;">', unsafe_allow_html=True)
            st.markdown("**🔢 나만의 숫자 입력**")
            user_input = st.text_input("", value="", placeholder="12251225", key=f"in_{key}", label_visibility="collapsed")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))
            st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="paper-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("### 🎄 Melody Tree")
        
        if final_nums:
            # [Visual] 트리 비주얼라이저
            digits = [int(d) for d in final_nums[:45] if d != '0']
            tree_data = []
            
            # 트리 좌표 알고리즘
            current_idx = 0; layer = 1; max_layers = 10 
            while current_idx < len(digits) and layer <= max_layers:
                nodes_in_layer = layer
                for i in range(nodes_in_layer):
                    if current_idx >= len(digits): break
                    note = digits[current_idx]
                    y_pos = 10 - layer 
                    width_spread = layer * 1.5
                    x_pos = np.linspace(-width_spread/2, width_spread/2, nodes_in_layer)[i]
                    size = note * 50 + 100
                    tree_data.append({'x': x_pos, 'y': y_pos, 'note': note, 'size': size})
                    current_idx += 1
                layer += 1
            
            df = pd.DataFrame(tree_data)
            star = pd.DataFrame({'x': [0], 'y': [10], 'note': [10], 'size': [600]})
            
            # 차트 그리기
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=1).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='#FFD700', size=600, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=350, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)
            st.caption("▲ 숫자가 쌓여 크리스마스 트리가 되었어요!")

        st.write("")
        if st.button(f"🔔 {title} 듣기", key=f"btn_{key}"):
            with st.spinner("음악을 만들고 있습니다..."):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Layout ---
st.markdown("""
<div class="board-header">
    <h1 class="main-title">Merry Math Class 🎄</h1>
    <div class="sub-title">중학교 수학과 함께하는 크리스마스 캐롤 탐구</div>
</div>
""", unsafe_allow_html=True)

# 탭 메뉴
t1, t2, t3, t4 = st.tabs(["중1 도형", "중2 유리수", "중3 제곱근", "자유 탐구"])

with t1:
    render_tab_content("t1", "tag-1", "도형의 성질 (중1)", "원주율(Pi) 징글벨", 
        """
        원은 완벽한 대칭을 가진 도형입니다. 원주율(3.14...)의 불규칙한 숫자들이 
        <b>경쾌한 셔플 리듬</b>과 만나 썰매를 타는 듯한 신나는 캐롤이 됩니다!
        """, "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_tab_content("t2", "tag-2", "유리수와 순환소수 (중2)", "순환소수 왈츠", 
        """
        1 나누기 7은 0.142857... 처럼 같은 숫자가 반복되는 순환소수입니다.
        이 규칙적인 패턴은 춤추기 좋은 <b>우아한 3박자 왈츠</b>와 완벽하게 어울립니다.
        """, "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_tab_content("t3", "tag-3", "제곱근과 실수 (중3)", "루트2의 거룩한 밤", 
        """
        제곱해서 2가 되는 수, 루트2(1.414...)는 인류가 처음 발견한 무리수입니다.
        끝없이 이어지는 이 신비로운 숫자는 <b>웅장한 합창(Choir)</b>으로 다시 태어납니다.
        """, "141421356237309504880168872420969807856967187537694", "holy", "oranges")

with t4:
    render_tab_content("t4", "tag-4", "자유 탐구 (전학년)", "나만의 숫자 캐롤", 
        """
        1225(크리스마스)나 여러분의 생일, 전화번호를 입력해보세요.
        수학적 규칙(알고리즘)이 여러분의 소중한 숫자를 <b>세상에 하나뿐인 캐롤</b>로 바꿔줄 거예요.
        """, "12251225", "joyful", "purples")

st.markdown("<br><hr style='border-top: 1px dashed #555;'><div style='text-align:center; color:#8FBC8F; font-size:0.9rem;'>수학 선생님과 함께하는 즐거운 크리스마스 🎁</div>", unsafe_allow_html=True)
