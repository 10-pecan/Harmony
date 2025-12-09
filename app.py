import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Christmas Card", page_icon="🎅", layout="wide")

# --- 2. 🎨 Vintage Christmas Card Design (CSS) ---
st.markdown("""
<style>
    /* [폰트 임포트] 장식용 필기체 + 본문용 고딕 */
    @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&family=Noto+Sans+KR:wght@300;500;700&display=swap');

    /* [전체 배경: 따뜻한 벽난로 느낌의 배경과 눈송이] */
    .stApp {
        background-color: #2c0a0a; /* 깊은 버건디 배경 */
        background-image: radial-gradient(circle at 50% 50%, #5a1a1a 0%, #2c0a0a 100%);
        color: #f8f1e5 !important; /* 크림색 텍스트 */
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* [눈 내리는 효과 (은은한 금빛)] */
    .snowflake { position: fixed; top: -10px; z-index: 99; color: #f1e3c4; font-size: 1.2em; opacity: 0.8; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh) rotate(0deg); } 100% { transform: translateY(110vh) rotate(360deg); } }

    /* [메인 타이틀: 금박 필기체 느낌] */
    .card-title-box {
        text-align: center; padding: 30px;
        border-bottom: 3px double #c49b63; /* 앤틱 골드 테두리 */
        margin-bottom: 40px;
        background: rgba(44, 10, 10, 0.6);
        border-radius: 20px 20px 0 0;
    }
    .main-title {
        font-family: 'Great Vibes', cursive;
        font-size: 5rem; color: #f1e3c4; /* 크림 골드 */
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5), 0 0 20px #c49b63;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 1.3rem; color: #d4af37; letter-spacing: 2px; font-weight: 500;
    }

    /* [메인 카드 프레임: 종이 질감의 팝업 카드] */
    .card-frame {
        background-color: #f8f1e5; /* 크림색 종이 배경 */
        background-image: url('https://www.transparenttextures.com/patterns/cream-paper.png'); /* 종이 텍스처 */
        border: 8px solid #8b0000; /* 진한 레드 테두리 */
        border-image: repeating-linear-gradient(45deg, #8b0000, #8b0000 10px, #1a472a 10px, #1a472a 20px) 10; /* 크리스마스 패턴 테두리 */
        border-radius: 25px;
        padding: 40px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        color: #3e2723; /* 짙은 갈색 텍스트 */
    }

    /* [내부 컨텐츠 박스: 편지지 느낌] */
    .inner-box {
        background: #fffaf0;
        border: 2px solid #d4af37;
        border-radius: 15px; padding: 25px; height: 100%;
    }

    /* [단원 태그: 선물 태그 스타일] */
    .gift-tag {
        display: inline-block; padding: 8px 18px;
        border-radius: 5px; font-size: 0.9rem; font-weight: 700;
        color: #fffaf0; margin-bottom: 15px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
        position: relative;
    }
    /* 태그 끈 효과 */
    .gift-tag::before { content: '●'; color: #f1e3c4; position: absolute; left: -10px; top: 50%; transform: translateY(-50%); font-size: 1.2rem; }
    
    .tag-1 { background: #c0392b; } /* 레드 */
    .tag-2 { background: #27ae60; } /* 그린 */
    .tag-3 { background: #f39c12; } /* 골드 */
    .tag-4 { background: #8e44ad; } /* 퍼플 */

    /* [탭 스타일: 리본 느낌] */
    div[data-baseweb="tab-list"] { gap: 15px; margin-bottom: 30px; justify-content: center; }
    button[data-baseweb="tab"] {
        background: #3e2723 !important; color: #d4af37 !important; border: 2px solid #d4af37 !important;
        border-radius: 10px 10px 0 0 !important; font-weight: bold; font-size: 1.1rem; padding: 10px 25px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: #8b0000 !important; color: #fffaf0 !important; border-color: #c49b63 !important;
    }

    /* [버튼: 오너먼트/왁스 실링 스타일] */
    .stButton>button {
        background: radial-gradient(circle at 30% 30%, #e74c3c, #c0392b) !important; /* 입체적인 레드 볼 */
        color: #fffaf0 !important; border: 4px solid #d4af37 !important; height: 75px; border-radius: 40px;
        font-family: 'Noto Sans KR', sans-serif; font-size: 1.4rem; font-weight: 800; width: 100%;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4), inset 0 5px 10px rgba(255,255,255,0.2);
        transition: all 0.3s; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    .stButton>button:hover { transform: scale(1.03); box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 5px 15px rgba(255,255,255,0.3); }

    /* [설명 텍스트] */
    .desc-text { font-size: 1.1rem; line-height: 1.8; color: #5d4037; }
    .desc-text b { color: #8b0000; background: #fbe9e7; padding: 2px 6px; border-radius: 4px; }
    h2 { font-family: 'Great Vibes', cursive; font-size: 2.8rem; color: #8b0000; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(8, 15)}s; animation-delay:{np.random.uniform(0, 5)}s; font-size:{np.random.uniform(0.8, 1.5)}em;">❄</div>' for _ in range(40)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (안정된 3가지 스타일) ---
# (이전 버전의 안정된 오디오 엔진 코드를 그대로 사용합니다.)
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
    else: att = int(length * 0.2); rel = int(length * 0.3); sus = length - att - rel
    if sus < 0: sus = 0; env = np.concatenate([np.linspace(0, 1, att), np.full(sus, 1.0), np.linspace(1, 0, rel)])
    env = match_len(env, length); return wave * env
def compose_music(nums, bpm, style):
    if style == "joyful": scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    elif style == "waltz": scale = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33, 659.25, 739.99]
    else: scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    beat_sec = 60.0 / bpm; full_track = []
    for digit in nums:
        if not digit.isdigit(): continue
        idx = int(digit); base_freq = scale[idx % len(scale)]; notes = []
        if style == "joyful": notes = [(base_freq, 0.75), (base_freq, 0.25), (base_freq*1.25, 1.0)] if idx % 2 == 0 else [(base_freq*1.5, 0.5), (base_freq*1.25, 0.5), (base_freq, 0.5), (base_freq*0.75, 0.5)]
        elif style == "waltz": notes = [(base_freq, 1.0), (base_freq*1.25, 1.0), (base_freq*1.5, 1.0)]
        else: notes = [(base_freq, 4.0)]
        melody_waves = []
        for f, d in notes: dur = d * beat_sec; w = generate_wave(f, dur, "bell" if style != "holy" else "choir"); w = apply_envelope(w, dur, "short" if style != "holy" else "long"); melody_waves.append(w)
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
        <div class="inner-box">
            <span class="gift-tag {tag_cls}">{tag_text}</span>
            <h2>{title}</h2>
            <div class="desc-text">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        final_nums = default_nums
        if key_prefix == "t4":
            st.write("")
            user_input = st.text_input("나만의 숫자 입력 (예: 1225)", value="", key=f"in_{key_prefix}")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))

    with c2:
        st.markdown('<div class="inner-box" style="text-align:center;">', unsafe_allow_html=True)
        
        if final_nums:
            digits = [int(d) for d in final_nums[:30] if d != '0']
            tree_data = []
            max_width = 12; height_scale = 1.5
            for i, d in enumerate(digits):
                level = d * height_scale; spread = (10 - d) * max_width / 10 
                pos = spread * (1 if i % 2 == 0 else -1) * np.random.uniform(0.4, 0.9)
                size = d * 60 + 150 
                tree_data.append({'Level': level, 'Pos': pos, 'Note': d, 'Size': size})
            df = pd.DataFrame(tree_data)
            
            # [VISUAL] 크리스마스 오너먼트 스타일 차트
            color_map = {'t1': 'reds', 't2': 'greens', 't3': 'oranges', 't4': 'purples'}
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='#fffaf0', strokeWidth=2).encode(
                x=alt.X('Pos', axis=None), y=alt.Y('Level', axis=None, scale=alt.Scale(domain=[0, 13*height_scale])),
                size=alt.Size('Size', legend=None, scale=alt.Scale(range=[100, 500])),
                color=alt.Color('Note', scale=alt.Scale(scheme=color_map[key_prefix]), legend=None),
                tooltip=['Note']
            )
            # 빛나는 효과 추가
            glow = base.mark_circle(opacity=0.4, strokeWidth=0).encode(size=alt.Size('Size', scale=alt.Scale(range=[200, 800])))

            chart = alt.layer(glow, base).properties(height=320, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)
            st.caption(f"▲ {style.title()} 스타일로 장식된 수학 트리")

        st.write("")
        # 버튼: 입체적인 오너먼트 스타일
        if st.button(f"🔔 Play Carol ({style.title()})", key=f"btn_{key_prefix}"):
            with st.spinner("산타가 악보를 연주합니다... 🎅"):
                bpm = 120 if style == "joyful" else 100 if style == "waltz" else 80
                audio = compose_music(final_nums, bpm, style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page ---
st.markdown("""
<div class="card-title-box">
    <div class="main-title">Merry Math Christmas</div>
    <div class="sub-title">🎄 중학교 수학으로 꾸미는 나만의 캐롤 카드 🎄</div>
</div>
""", unsafe_allow_html=True)

# 전체를 감싸는 카드 프레임
st.markdown('<div class="card-frame">', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎁 1학년 (도형)", "🎁 2학년 (수)", "🎁 3학년 (무리수)", "🎁 나만의 카드"])

with tab1:
    render_tab("t1", "tag-1", "중1 | 원과 부채꼴", "원주율(π)의 징글벨", 
               """
               사랑하는 친구에게,<br>
               동그란 크리스마스 리스를 보면 <b>원주율(3.141592...)</b>이 생각나.<br>
               끝없이 이어지는 파이(π)의 숫자들처럼, 우리의 우정도 영원히 변치 않기를 바랄게.<br>
               이 불규칙한 숫자들이 만드는 <b>신나는 셔플 리듬</b>을 즐겨봐! 메리 크리스마스!
               """, 
               "314159265358979323846264338327950288419716939937510", "joyful")

with tab2:
    render_tab("t2", "tag-2", "중2 | 순환소수", "순환소수의 왈츠", 
               """
               소중한 가족에게,<br>
               똑같은 일상이 반복되는 것 같아도, 그 안에는 <b>순환소수(0.142857...)</b>처럼 변치 않는 사랑이 숨어있단다.<br>
               규칙적으로 반복되는 숫자들이 만들어내는 <b>우아한 3박자 왈츠</b>를 들으며,<br>
               따뜻하고 행복한 연말 보내렴. 사랑한다!
               """, 
               "142857142857142857142857142857142857142857", "waltz")

with tab3:
    render_tab("t3", "tag-3", "중3 | 실수와 그 계산", "루트2의 성탄 밤", 
               """
               존경하는 선생님께,<br>
               정사각형 속에서 묵묵히 대각선을 지키는 <b>루트2(1.414213...)</b>처럼,<br>
               언제나 저희를 바른 길로 이끌어 주셔서 감사합니다.<br>
               무리수의 깊이 있는 울림이 전하는 <b>웅장한 합창</b>과 함께 평안한 성탄절 되세요.
               """, 
               "141421356237309504880168872420969807856967187537694", "holy")

with tab4:
    render_tab("t4", "tag-4", "자유학기제 | 창의 탐구", "나만의 소원 캐롤", 
               """
               나 자신에게 보내는 카드,<br>
               올 한 해 수고 많았어! 1225(크리스마스)나 내 생일처럼 특별한 숫자를 입력해봐.<br>
               그 숫자들 속에 숨겨진 너만의 멜로디가 <b>세상에 하나뿐인 캐롤</b>로 탄생할 거야.<br>
               내년에도 반짝이는 트리의 오너먼트처럼 빛나는 한 해가 되길!
               """, 
               "12251225", "joyful")

st.markdown('</div>', unsafe_allow_html=True) # End card-frame
st.markdown("<br><div style='text-align:center; color:#f1e3c4; font-size:0.9rem;'>From. Math Santa 🎅 (중등 수학 탐구 활동)</div><br>", unsafe_allow_html=True)
