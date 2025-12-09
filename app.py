import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol: Future Edition", page_icon="❄️", layout="wide")

# --- 2. 🎨 2025 Future Glass Design (CSS) ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* [전체 테마: Deep Space & Aurora] */
    .stApp {
        background-color: #000000 !important;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        color: #FFFFFF !important;
        font-family: 'Pretendard', -apple-system, sans-serif !important;
    }

    /* [헤더 타이포그래피] */
    .hero-title {
        font-size: 3.5rem; font-weight: 800; letter-spacing: -1px; text-align: center;
        background: linear-gradient(to right, #fff, #a5b4fc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: 20px; margin-bottom: 5px;
    }
    .hero-sub {
        font-size: 1rem; color: #94a3b8; text-align: center; font-weight: 400; 
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 50px;
    }

    /* [Glass Card: 핵심 UI 컨테이너] */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px; padding: 32px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 24px; transition: transform 0.2s;
    }
    .glass-card:hover { border-color: rgba(255, 255, 255, 0.15); }

    /* [입력창 커스텀 - 모던하게] */
    .stTextInput input {
        background-color: rgba(0,0,0,0.3) !important;
        color: #fff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        padding: 12px 15px !important;
        text-align: center; font-size: 1.1rem; letter-spacing: 2px;
    }
    .stTextInput input:focus {
        border-color: #a5b4fc !important; box-shadow: 0 0 0 1px #a5b4fc;
    }

    /* [탭 디자인 - 슬릭하게] */
    div[data-baseweb="tab-list"] { 
        background-color: rgba(255,255,255,0.05); padding: 4px; border-radius: 16px; 
        gap: 0px; justify-content: center; width: fit-content; margin: 0 auto 40px auto;
    }
    button[data-baseweb="tab"] {
        background: transparent !important; border: none !important; color: #64748b !important;
        border-radius: 12px !important; padding: 8px 24px !important; font-weight: 600;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(255,255,255,0.1) !important; color: #fff !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    /* [버튼 - 네온 그라데이션] */
    .stButton>button {
        background: linear-gradient(90deg, #4f46e5, #ec4899) !important;
        color: white !important; border: none !important;
        height: 56px; border-radius: 16px; font-size: 1.1rem; font-weight: 700;
        width: 100%; transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02); box-shadow: 0 0 20px rgba(79, 70, 229, 0.4);
    }

    /* [뱃지 스타일] */
    .badge {
        display: inline-flex; align-items: center; padding: 4px 12px;
        border-radius: 999px; font-size: 0.75rem; font-weight: 700; 
        letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 16px;
    }
    .badge-dot { width: 6px; height: 6px; border-radius: 50%; margin-right: 8px; }
    
    .b-blue { background: rgba(59, 130, 246, 0.1); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); }
    .b-blue .badge-dot { background: #60a5fa; }
    
    .b-green { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); }
    .b-green .badge-dot { background: #34d399; }
    
    .b-purple { background: rgba(139, 92, 246, 0.1); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.2); }
    .b-purple .badge-dot { background: #a78bfa; }

    /* [설명 텍스트] */
    .desc { color: #cbd5e1; line-height: 1.6; font-size: 0.95rem; }
    .desc strong { color: #fff; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- 3. 🎹 Audio Engine (Final Logic) ---
# 길이 보정 및 안정적인 합성 로직 유지

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
        att = int(length*0.2); rel = int(length*0.3); sus = length - att - rel; 
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

# --- 4. UI 렌더링 (카드 UI & 비주얼라이저 수정) ---

def render_modern_ui(key, badge_class, badge_txt, title, desc, default_nums, style, color_scheme):
    
    # 2열 레이아웃: [왼쪽: 컨트롤 & 정보] | [오른쪽: 비주얼 & 플레이어]
    c1, c2 = st.columns([1, 1.3], gap="large")
    
    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="badge {badge_class}"><div class="badge-dot"></div>{badge_txt}</div>
            <h2 style="margin: 0 0 15px 0;">{title}</h2>
            <div class="desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        
        # 커스텀 탭일 때만 입력창 활성화
        if key == "t4":
            st.markdown('<div class="glass-card" style="padding:20px;">', unsafe_allow_html=True)
            st.caption("CUSTOM SEQUENCE")
            user_in = st.text_input("", value="", placeholder="Numbers Only", key=f"in_{key}", label_visibility="collapsed")
            if user_in: final_nums = "".join(filter(str.isdigit, user_in))
            st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        
        if final_nums:
            # [Visual Fix] 확실하게 표시되는 Altair 차트
            # 데이터 준비
            digits = [int(d) for d in final_nums[:40] if d != '0']
            
            # 차트 데이터 생성 (트리 구조)
            tree_data = []
            layer = 1
            idx = 0
            while idx < len(digits):
                for i in range(layer):
                    if idx >= len(digits): break
                    d = digits[idx]
                    # X: 중심에서 퍼짐, Y: 위에서 아래로
                    x = (i - (layer-1)/2) * 1.5
                    y = 10 - layer
                    size = d * 60 + 100
                    tree_data.append({'x': x, 'y': y, 'note': d, 'size': size})
                    idx += 1
                layer += 1
                if layer > 10: break # 최대 10층
                
            df = pd.DataFrame(tree_data)
            star = pd.DataFrame({'x': [0], 'y': [10], 'note': [10], 'size': [600]})
            
            # Altair 차트 (Glow Effect)
            base = alt.Chart(df).mark_circle(opacity=0.8, stroke='white', strokeWidth=1).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='white', size=600, strokeWidth=0).encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=350, background='transparent').configure_view(strokeWidth=0)
            
            st.altair_chart(final_chart, use_container_width=True)
            st.caption("Interactive Melody Tree")

        st.write("")
        if st.button("Play Sequence ▶", key=f"btn_{key}"):
            with st.spinner("Generating Audio..."):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Structure ---

st.markdown("""
<div class="hero-container">
    <div class="hero-title">MATH CAROL</div>
    <div class="hero-sub">The Sound of Numbers : Christmas Edition</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["GRADE 1", "GRADE 2", "GRADE 3", "FREE PLAY"])

with t1:
    render_modern_ui("t1", "b-blue", "SHAPES (도형)", "The Pi Jingle", 
        "원은 완벽한 대칭을 이루지만, 그 비율인 <strong>파이(π)</strong>는 불규칙하게 끝없이 이어집니다. 이 불규칙함이 <strong>경쾌한 셔플 리듬</strong>과 만나 즐거운 캐롤이 됩니다.", 
        "314159265358979323846264338327950288419716939937510", "joyful", "tealblues")

with t2:
    render_modern_ui("t2", "b-green", "NUMBER (수)", "Decimal Waltz", 
        "1/7은 <strong>0.142857</strong>이 반복되는 순환소수입니다. 이 규칙적인 숫자들의 반복은 춤추기 좋은 <strong>우아한 3박자 왈츠</strong>와 완벽하게 어울립니다.", 
        "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_modern_ui("t3", "b-purple", "IRRATIONAL (무리수)", "Root Harmony", 
        "제곱해서 2가 되는 수, <strong>루트2(√2)</strong>는 인류가 처음 발견한 무리수입니다. 끝을 알 수 없는 이 숫자의 깊이를 <strong>웅장한 합창</strong>으로 표현했습니다.", 
        "141421356237309504880168872420969807856967187537694", "holy", "magma")

with t4:
    render_modern_ui("t4", "b-blue", "CUSTOM", "Your Own Carol", 
        "<strong>1225(크리스마스)</strong>나 당신의 생일을 입력해보세요. 수학적 알고리즘이 당신만의 숫자를 세상에 하나뿐인 멜로디로 변환해 드립니다.", 
        "12251225", "joyful", "rainbow")
