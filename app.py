import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="중등 수학 캐롤 탐구", page_icon="📘", layout="wide")

# --- 2. 🎨 Textbook Style Design (CSS) ---
st.markdown("""
<style>
    /* [폰트] 가독성 좋은 현대적 고딕 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* [전체 배경: 깨끗한 화이트/라이트 그레이] */
    .stApp {
        background-color: #F8F9FA !important;
        color: #343A40 !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    /* [메인 타이틀: 교과서 대단원 제목 스타일] */
    .main-title-box {
        text-align: center; padding: 40px 20px;
        border-bottom: 2px solid #DEE2E6; margin-bottom: 40px;
        background: #FFFFFF;
    }
    .main-title {
        font-size: 3rem; font-weight: 800; color: #212529;
        letter-spacing: -0.5px; margin-bottom: 10px;
    }
    .sub-title {
        font-size: 1.2rem; color: #868E96; font-weight: 500;
    }
    .sub-title b { color: #c92a2a; } /* 크리스마스 포인트 컬러 */

    /* [컨텐츠 카드: 학습 활동지 스타일] */
    .edu-card {
        background: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        height: 100%;
    }
    .card-header {
        border-bottom: 2px solid #F1F3F5;
        padding-bottom: 15px; margin-bottom: 20px;
    }
    .card-header h3 { margin: 0; font-size: 1.5rem; font-weight: 700; color: #343A40; }

    /* [단원 태그] */
    .edu-tag {
        display: inline-block; padding: 6px 12px;
        border-radius: 4px; font-size: 0.85rem; font-weight: 700;
        color: #495057; background: #F1F3F5;
        margin-bottom: 10px; border-left: 4px solid #ADB5BD;
    }
    /* 학년별 포인트 컬러 */
    .tag-1 { border-left-color: #e03131; color: #c92a2a; background: #fff5f5; } /* 1학년 레드 */
    .tag-2 { border-left-color: #2f9e44; color: #2b8a3e; background: #ebfbee; } /* 2학년 그린 */
    .tag-3 { border-left-color: #f08c00; color: #e67700; background: #fff9db; } /* 3학년 옐로우 */
    .tag-4 { border-left-color: #5f3dc4; color: #5f3dc4; background: #f3f0ff; } /* 커스텀 퍼플 */

    /* [본문 텍스트] */
    .desc-text {
        font-size: 1rem; line-height: 1.7; color: #495057;
        background-color: #F8F9FA; padding: 20px; border-radius: 8px;
    }
    .desc-text b { color: #212529; font-weight: 700; }

    /* [탭 스타일: 깔끔한 언더라인] */
    div[data-baseweb="tab-list"] { gap: 20px; margin-bottom: 30px; border-bottom: 2px solid #E9ECEF; }
    button[data-baseweb="tab"] {
        background: transparent !important; border: none !important;
        color: #ADB5BD !important; font-size: 1.1rem !important; font-weight: 600 !important;
        padding-bottom: 10px !important; border-radius: 0 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #212529 !important; border-bottom: 3px solid #212529 !important;
    }

    /* [버튼: 학습 도구 스타일] */
    .stButton>button {
        background: #228be6 !important; /* 차분한 블루 */
        color: #ffffff !important; border: none; height: 55px; border-radius: 8px;
        font-size: 1.1rem; font-weight: 700; width: 100%;
        transition: all 0.2s;
    }
    .stButton>button:hover { background: #1c7ed6 !important; }
    
    /* [입력창 커스텀] */
    .stTextInput input { border: 1px solid #ced4da; border-radius: 4px; padding: 10px; }
</style>
""", unsafe_allow_html=True)


# --- 3. 🎹 Audio Engine (안정된 최종 버전) ---

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
    if type == "short": 
        env = np.exp(np.linspace(0, -5, length))
    else:
        att = int(length * 0.2); rel = int(length * 0.3); sus = length - att - rel
        if sus < 0: sus = 0
        env = np.concatenate([np.linspace(0, 1, att), np.full(sus, 1.0), np.linspace(1, 0, rel)])
    env = match_len(env, length)
    return wave * env

def compose_music(nums, bpm, style):
    if style == "joyful": scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    elif style == "waltz": scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    else: scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    beat_sec = 60.0 / bpm; full_track = []
    
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit); base_freq = scale[idx % len(scale)]
        
        notes = []
        if style == "joyful": notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)] if idx % 2 == 0 else [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        elif style == "waltz": notes = [(base_freq, 1.0), (base_freq*1.25, 1.0), (base_freq*1.5, 1.0)]
        else: notes = [(base_freq, 4.0)]
            
        melody_waves = []
        for f, d in notes:
            dur = d * beat_sec
            w = generate_wave(f, dur, "bell" if style != "holy" else "choir")
            w = apply_envelope(w, dur, "short" if style != "holy" else "long")
            melody_waves.append(w)
        melody = np.concatenate(melody_waves); total_len = len(melody)
        
        pad = generate_wave(base_freq * 0.5, total_len/44100, "strings"); pad = match_len(pad, total_len); pad = apply_envelope(pad, total_len/44100, "long") * 0.3
        sleigh = generate_wave(0, total_len/44100, "sleigh"); sleigh = match_len(sleigh, total_len) * 0.3 if style == "joyful" else np.zeros(total_len)
        full_track.append(melody + pad + sleigh)
        
    if not full_track: return None
    full = np.concatenate(full_track); delay = int(44100 * 0.4); res = np.zeros(len(full) + delay); res[:len(full)] += full; res[delay:] += full * 0.4
    m = np.max(np.abs(res)); return res / m * 0.95 if m > 0 else res

# --- 4. UI Rendering ---

def render_tab(key_prefix, tag_cls, tag_text, title, desc, default_nums, style):
    c1, c2 = st.columns([1, 1.2], gap="large")
    
    with c1:
        st.markdown(f"""
        <div class="edu-card">
            <div class="card-header">
                <span class="edu-tag {tag_cls}">{tag_text}</span>
                <h3>{title}</h3>
            </div>
            <div class="desc-text">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        if key_prefix == "t4":
            st.write("")
            st.markdown("**🔢 나만의 숫자 입력** (예: 생일, 기념일)")
            user_input = st.text_input("", value="", key=f"in_{key_prefix}", label_visibility="collapsed")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))

    with c2:
        st.markdown('<div class="edu-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>📊 소리의 시각화 (Visualizer)</h3></div>', unsafe_allow_html=True)
        
        if final_nums:
            digits = [int(d) for d in final_nums[:30] if d != '0']
            tree_data = []
            max_width = 12; height_scale = 1.5
            
            for i, d in enumerate(digits):
                level = d * height_scale
                spread = (10 - d) * max_width / 10 
                pos = spread * (1 if i % 2 == 0 else -1) * np.random.uniform(0.4, 0.9)
                size = d * 80 + 200 
                tree_data.append({'Level': level, 'Pos': pos, 'Note': d, 'Size': size})
            
            df = pd.DataFrame(tree_data)
            
            # [VISUAL] 교과서 스타일의 깔끔한 차트 (빛 번짐 제거)
            color_map = {'t1': 'reds', 't2': 'greens', 't3': 'oranges', 't4': 'purples'}
            
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=1).encode(
                x=alt.X('Pos', axis=None),
                y=alt.Y('Level', axis=None, scale=alt.Scale(domain=[0, 13*height_scale])),
                size=alt.Size('Size', legend=None, scale=alt.Scale(range=[100, 600])), # 크기 조절
                color=alt.Color('Note', scale=alt.Scale(scheme=color_map[key_prefix]), legend=None),
                tooltip=['Note']
            )
            
            chart = base.properties(height=300, background='transparent').configure_view(strokeWidth=0)
            
            st.altair_chart(chart, use_container_width=True)
            st.caption("▲ 숫자의 크기가 음의 높이와 원의 크기로 표현됩니다.")

        # 재생 버튼
        st.write("")
        if st.button(f"▶ 캐롤 재생하기 ({style.title()} Ver.)", key=f"btn_{key_prefix}"):
            with st.spinner("음원 생성 중입니다..."):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page ---
st.markdown("""
<div class="main-title-box">
    <div class="main-title">중등 수학과 함께하는 캐롤 탐구</div>
    <div class="sub-title">수학적 규칙이 어떻게 <b>아름다운 음악</b>으로 변하는지 체험해 봅시다.</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["1학년: 도형", "2학년: 수", "3학년: 무리수", "자유탐구"])

with tab1:
    render_tab("t1", "tag-1", "중1 | 도형의 성질", "원주율 (Pi) 징글벨", 
               """
               <b>탐구 주제:</b> 원주율(π)의 불규칙성<br>
               <b>수학적 특징:</b> 원주율 3.141592...는 순환하지 않는 무한소수입니다. 이 불규칙한 숫자의 배열이 <b>예측할 수 없는 즐거운 리듬(셔플)</b>을 만들어냅니다.
               """, 
               "314159265358979323846264338327950288419716939937510", "joyful")

with tab2:
    render_tab("t2", "tag-2", "중2 | 유리수와 순환소수", "순환소수 왈츠", 
               """
               <b>탐구 주제:</b> 순환소수의 규칙성<br>
               <b>수학적 특징:</b> 1/7 = 0.142857... 처럼 일정한 구간이 반복되는 수를 순환소수라고 합니다. 이 규칙적인 반복이 <b>우아한 3박자 왈츠</b>의 리듬이 됩니다.
               """, 
               "142857142857142857142857142857142857142857", "waltz")

with tab3:
    render_tab("t3", "tag-3", "중3 | 제곱근과 실수", "무리수(√2)의 울림", 
               """
               <b>탐구 주제:</b> 무리수의 깊이<br>
               <b>수학적 특징:</b> √2는 인류가 최초로 발견한 무리수입니다. 한 변이 1인 정사각형의 대각선 길이와 같죠. 이 깊이 있는 숫자가 <b>웅장한 합창(Choir)</b> 소리로 표현됩니다.
               """, 
               "141421356237309504880168872420969807856967187537694", "holy")

with tab4:
    render_tab("t4", "tag-4", "전학년 | 자유 탐구 활동", "나만의 숫자 악보 만들기", 
               """
               <b>탐구 활동:</b> 우리 주변의 숫자 찾아보기<br>
               <b>활동 안내:</b> 여러분의 생일, 전화번호 뒷자리, 또는 좋아하는 숫자를 입력해보세요. 어떤 수학적 규칙이 어떤 음악으로 변환될지 실험해 봅시다.
               """, 
               "12251225", "joyful")

st.markdown("<br><hr><div style='text-align:center; color:#868E96; font-size:0.9rem;'>중학교 수학 교과 과정 연계 탐구 활동 자료</div><br>", unsafe_allow_html=True)
