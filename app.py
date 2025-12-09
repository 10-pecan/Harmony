import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol School", page_icon="🎄", layout="wide")

# --- 2. 🎨 Premium Winter School Design (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@300;500;700;900&family=Cinzel:wght@700&display=swap');
    
    /* [전체 배경: 깊은 로열 그린 (칠판 + 크리스마스 느낌)] */
    .stApp {
        background-color: #1A472A !important;
        background-image: radial-gradient(#2E5E40 1px, transparent 1px);
        background-size: 30px 30px;
        color: #f1f2f6 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* [눈 효과] */
    .snowflake { position: fixed; top: -10px; z-index: 0; color: rgba(255,255,255,0.4); font-size: 1em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [헤더 디자인] */
    .header-container {
        text-align: center; padding: 50px 0 30px 0;
        border-bottom: 2px solid #D4AF37; /* 골드 라인 */
        margin-bottom: 40px;
    }
    .main-title {
        font-family: 'Cinzel', serif; font-size: 4.5rem; color: #F4D03F; /* 샴페인 골드 */
        text-shadow: 0 4px 10px rgba(0,0,0,0.5); margin: 0;
    }
    .sub-title {
        font-family: 'Gowun Dodum', sans-serif; font-size: 1.3rem; color: #A9DFBF; 
        margin-top: 15px; letter-spacing: 1px;
    }

    /* [카드 디자인: 여백을 넓혀서 시원하게] */
    .premium-card {
        background: #FFFFFF;
        border: 4px solid #D4AF37; /* 금테 */
        border-radius: 20px;
        padding: 40px; /* 내부 여백 대폭 확대 */
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        margin-bottom: 30px;
        height: 100%;
        color: #2C3E50;
    }

    /* [선생님 노트 박스] */
    .teacher-note {
        background-color: #F9FBE7; /* 아주 연한 연두색 */
        border-left: 6px solid #558B2F;
        padding: 25px; border-radius: 8px;
        margin-top: 25px; font-size: 1.05rem; line-height: 1.8; color: #33691E;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
    }
    .note-label { font-weight: 900; color: #2E7D32; display: block; margin-bottom: 8px; font-size: 1.1rem; }

    /* [탭 디자인] */
    div[data-baseweb="tab-list"] { gap: 15px; justify-content: center; }
    button[data-baseweb="tab"] {
        background-color: rgba(0,0,0,0.3) !important; border-radius: 12px !important;
        border: 1px solid #555 !important; color: #AAA !important; font-weight: bold; font-size: 1.1rem; padding: 12px 25px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #D4AF37 !important; color: #1A472A !important; border: 2px solid #FFF !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.6);
    }

    /* [버튼] */
    .stButton>button {
        background: linear-gradient(135deg, #C0392B 0%, #922B21 100%) !important; /* 크리스마스 레드 */
        color: white !important; border: 2px solid #F1C40F !important;
        border-radius: 15px; height: 70px; font-size: 1.3rem; font-weight: 800; width: 100%;
        box-shadow: 0 8px 15px rgba(0,0,0,0.3); transition: all 0.2s;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 12px 20px rgba(0,0,0,0.4); }

    /* [입력창] */
    .stTextInput input {
        border: 2px solid #BDC3C7; border-radius: 12px; text-align: center; font-size: 1.3rem; color: #2C3E50; padding: 15px;
    }
    
    /* [뱃지 스타일] */
    .badge {
        display: inline-block; padding: 8px 16px; border-radius: 30px; 
        font-size: 0.95rem; font-weight: 800; color: #fff; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2); letter-spacing: 0.5px;
    }
    .b-1 { background: #e74c3c; } /* Red */
    .b-2 { background: #27ae60; } /* Green */
    .b-3 { background: #f39c12; } /* Gold */
    .b-4 { background: #8e44ad; } /* Purple */
    
    h2 { font-family: 'Gowun Dodum', sans-serif; font-weight: 900; font-size: 2.2rem; color: #1A472A; margin: 0; }
</style>
""", unsafe_allow_html=True)

# 눈 효과 JS
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(8, 15)}s; animation-delay:{np.random.uniform(0, 5)}s;">❄</div>' for _ in range(40)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine ---
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
        att = int(length*0.2); rel = int(length*0.3); sus = length - att - rel
        if sus < 0: sus = 0
        env = np.concatenate([np.linspace(0, 1, att), np.full(sus, 1.0), np.linspace(1, 0, rel)])
    env = match_len(env, length); return wave * env

def compose_music(nums, bpm, style):
    # Scale: C Major / D Major / A Minor (안전하게 길이 확보)
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

# --- 4. UI 렌더링 함수 ---

def render_class_tab(key_prefix, badge_cls, badge_text, title, subtitle, math_note, default_nums, style, color_scheme):
    c1, c2 = st.columns([1, 1.2], gap="large")
    
    with c1:
        # [HTML FIX] 닫는 태그 오류 원천 차단 및 구조 단순화
        st.markdown(f"""
        <div class="premium-card">
            <span class="badge {badge_cls}">{badge_text}</span>
            <h2>{title}</h2>
            <div style="color:#7F8C8D; font-weight:bold; margin-bottom:20px; font-size:1.1rem;">{subtitle}</div>
            
            <div class="teacher-note">
                <span class="note-label">🧑‍🏫 선생님의 이야기</span>
                {math_note}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        if key_prefix == "t4":
            st.markdown("") # 여백
            user_input = st.text_input("여기에 숫자를 입력하세요", value="", placeholder="12251225", key=f"in_{key_prefix}")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))

    with c2:
        st.markdown('<div class="premium-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("### 🎄 Melody Tree Visualization")
        st.write("") # 여백
        
        if final_nums:
            # [VISUAL UPGRADE] 진짜 트리 모양 + 오너먼트 효과
            digits = [int(d) for d in final_nums[:45] if d != '0']
            tree_data = []
            
            current_idx = 0; layer = 1; max_layers = 10 
            while current_idx < len(digits) and layer <= max_layers:
                nodes_in_layer = layer
                for i in range(nodes_in_layer):
                    if current_idx >= len(digits): break
                    note = digits[current_idx]
                    y_pos = 10 - layer 
                    width_spread = layer * 1.5
                    x_pos = np.linspace(-width_spread/2, width_spread/2, nodes_in_layer)[i]
                    # 음계(Note)에 따라 크기와 색상 변화
                    size = note * 60 + 150 
                    tree_data.append({'x': x_pos, 'y': y_pos, 'note': note, 'size': size})
                    current_idx += 1
                layer += 1
            
            df = pd.DataFrame(tree_data)
            star = pd.DataFrame({'x': [0], 'y': [10], 'note': [10], 'size': [800]})
            
            # 오너먼트 (반투명 + 테두리)
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=2).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['note']
            )
            # 별 (가장 꼭대기)
            top = alt.Chart(star).mark_point(shape='star', fill='#F4D03F', size=800, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=450).configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)
            st.caption("▲ 숫자의 높낮이가 트리의 오너먼트가 됩니다.")

        st.write("")
        if st.button(f"🔔 연주 시작 ({style.title()})", key=f"btn_{key_prefix}"):
            with st.spinner("캐롤 편곡 중... 🎼"):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
                    
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page ---
st.markdown("""
<div class="header-container">
    <h1 class="main-title">Math Christmas Carol</h1>
    <div class="sub-title">중학교 수학으로 꾸미는 나만의 멜로디 트리</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["🔴 중1 (도형)", "🟢 중2 (수)", "🟡 중3 (무리수)", "🟣 자유 탐구"])

with t1:
    render_class_tab("t1", "b-1", "중1 - 도형의 성질", "원주율 (Pi) 징글벨", "3.141592...", 
        """
        <b>"원은 완벽한 대칭이지만, 그 비율은 불규칙하단다."</b><br>
        원주율 3.14159...는 숫자가 규칙 없이 끝없이 이어져요. 
        이 불규칙한 숫자들이 <b>경쾌한 셔플 리듬</b>과 만나면 
        마치 썰매가 울퉁불퉁한 눈길을 달리는 듯한 신나는 캐롤이 됩니다!
        """, "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_class_tab("t2", "b-2", "중2 - 유리수와 순환소수", "순환소수 왈츠", "0.142857...", 
        """
        <b>"규칙적으로 반복되는 숫자를 찾아볼까?"</b><br>
        1/7 = 0.142857... 처럼 같은 숫자가 도돌이표처럼 반복되는 수를 '순환소수'라고 해요.
        이 규칙적인 패턴은 춤추기 좋은 <b>3박자 왈츠</b> 리듬과 완벽하게 어울립니다.
        """, "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_class_tab("t3", "b-3", "중3 - 제곱근과 실수", "루트2의 거룩한 밤", "1.414213...", 
        """
        <b>"인류가 처음 발견한 신비로운 수야."</b><br>
        제곱해서 2가 되는 수, 루트2(1.414...)는 끝을 알 수 없는 무리수입니다.
        이 깊고 신비로운 숫자의 느낌을 <b>웅장한 합창(Choir)</b>으로 표현해 보았어요.
        """, "141421356237309504880168872420969807856967187537694", "holy", "oranges")

with t4:
    render_class_tab("t4", "b-4", "자유 학기제", "나만의 숫자 캐롤", "Make Your Own Carol", 
        """
        <b>"여러분의 숫자도 음악이 될 수 있어요!"</b><br>
        1225(크리스마스)나 여러분의 생일, 전화번호를 입력해보세요.
        수학적 규칙(알고리즘)이 여러분의 숫자를 세상에 하나뿐인 캐롤로 바꿔줄 거예요.
        """, "12251225", "joyful", "purples")

st.markdown("<br><hr><div style='text-align:center; color:#A9DFBF; font-size:0.9rem;'>Designed for Joyful Math Education • 2025</div>", unsafe_allow_html=True)
