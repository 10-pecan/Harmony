import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Studio", page_icon="🎄", layout="wide")

# --- 2. 🎨 Ultimate Winter Design (CSS) ---
st.markdown("""
<style>
    /* [폰트] 귀여운 한글 폰트 + 깔끔한 영문 폰트 */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Outfit:wght@400;700&display=swap');
    
    /* [전체 배경: 따뜻한 겨울 화이트] */
    .stApp {
        background-color: #F8F9FA !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(224, 247, 250, 0.3) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(255, 235, 238, 0.3) 0px, transparent 50%);
        color: #2d3436 !important;
        font-family: 'Gowun Dodum', sans-serif !important;
    }

    /* [헤더] */
    .header-title {
        font-family: 'Outfit', sans-serif; font-size: 3.5rem; font-weight: 800;
        text-align: center; color: #D32F2F; margin-top: 20px;
        text-shadow: 2px 2px 0px #FADBD8; letter-spacing: -1px;
    }
    .header-sub {
        text-align: center; color: #546E7A; font-size: 1.1rem; margin-bottom: 40px; font-weight: bold;
    }

    /* [탭 디자인 - 알약 모양] */
    div[data-baseweb="tab-list"] {
        gap: 10px; justify-content: center; margin-bottom: 30px;
        background: #FFFFFF; padding: 10px; border-radius: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); width: fit-content; margin-left: auto; margin-right: auto;
    }
    button[data-baseweb="tab"] {
        background-color: transparent !important; border: none !important;
        color: #90A4AE !important; font-weight: bold; font-size: 1rem; border-radius: 30px !important;
        padding: 8px 20px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #16A085 !important; color: #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(22, 160, 133, 0.3);
    }

    /* [카드 컨테이너 - HTML 래핑 없이 스타일링] */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background-color: #FFFFFF;
        border-radius: 24px;
        padding: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.03);
        border: 1px solid #F1F3F5;
    }

    /* [뱃지 스타일] */
    .badge {
        display: inline-block; padding: 6px 14px; border-radius: 12px;
        font-size: 0.85rem; font-weight: 800; color: #fff; margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .b-red { background: linear-gradient(135deg, #FF5252, #D32F2F); }
    .b-green { background: linear-gradient(135deg, #66BB6A, #388E3C); }
    .b-gold { background: linear-gradient(135deg, #FFCA28, #F57F17); }
    .b-purple { background: linear-gradient(135deg, #AB47BC, #7B1FA2); }

    /* [텍스트 가독성 강제 적용] */
    p, li, label, .stMarkdown { color: #455A64 !important; line-height: 1.7; }
    h2, h3 { color: #263238 !important; }
    
    /* [라디오 버튼 & 입력창 텍스트 색상 수정] */
    div[role="radiogroup"] label p { color: #263238 !important; font-weight: bold; }
    .stTextInput input { color: #37474F !important; font-weight: bold; text-align: center; }

    /* [버튼 디자인] */
    .stButton>button {
        background: linear-gradient(to right, #D32F2F, #C2185B) !important;
        color: white !important; border: none !important; border-radius: 15px;
        height: 60px; font-size: 1.2rem; font-weight: 800; width: 100%;
        box-shadow: 0 8px 20px rgba(211, 47, 47, 0.2); transition: 0.2s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 12px 25px rgba(211, 47, 47, 0.3); }

    /* [눈송이 애니메이션] */
    .snowflake { position: fixed; top: -10px; z-index: 99; color: #B0BEC5; opacity: 0.5; font-size: 1rem; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(5, 15)}s; animation-delay:{np.random.uniform(0, 5)}s;">❄</div>' for _ in range(30)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (안정화 버전) ---

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

# --- 4. UI 렌더링 함수 (Native Containers 사용) ---

def render_content(key, badge_cls, badge_text, title, desc, default_nums, style, color_scheme):
    c1, c2 = st.columns([1, 1], gap="medium")
    
    # [왼쪽] 설명 카드
    with c1:
        # 뱃지 (HTML)
        st.markdown(f'<span class="badge {badge_cls}">{badge_text}</span>', unsafe_allow_html=True)
        # 제목
        st.markdown(f"## {title}")
        # 설명 (안전한 컨테이너 사용)
        st.info(desc, icon="🧑‍🏫")
        
        # 4번째 탭 커스텀 입력
        final_nums = default_nums
        final_style = style
        
        if key == "t4":
            st.markdown("---")
            st.markdown("**🔢 나만의 숫자 입력**")
            user_input = st.text_input("숫자를 입력하세요", value="", placeholder="12251225", key=f"in_{key}", label_visibility="collapsed")
            if user_input: final_nums = "".join(filter(str.isdigit, user_input))
            
            st.markdown("**🎶 음악 스타일 선택**")
            # 선택지 색상이 잘 보이도록 CSS에서 조정 완료
            s_opt = st.radio("Style", ["Joyful (신남)", "Waltz (우아함)", "Holy (웅장함)"], key=f"sel_{key}", label_visibility="collapsed")
            if "Joyful" in s_opt: final_style = "joyful"
            elif "Waltz" in s_opt: final_style = "waltz"
            else: final_style = "holy"

    # [오른쪽] 비주얼 & 플레이어
    with c2:
        if final_nums:
            # 트리 비주얼라이저
            digits = [int(d) for d in final_nums[:45] if d != '0']
            tree_data = []
            current_idx = 0; layer = 1; max_layers = 10 
            while current_idx < len(digits) and layer <= max_layers:
                nodes_in_layer = layer
                for i in range(nodes_in_layer):
                    if current_idx >= len(digits): break
                    note = digits[current_idx]
                    width = layer * 1.5
                    x = np.linspace(-width/2, width/2, nodes_in_layer)[i]
                    y = 10 - layer 
                    size = note * 50 + 100
                    tree_data.append({'x': x, 'y': y, 'note': note, 'size': size})
                    current_idx += 1
                layer += 1
            
            df = pd.DataFrame(tree_data)
            star = pd.DataFrame({'x': [0], 'y': [10], 'note': [10], 'size': [600]})
            
            base = alt.Chart(df).mark_circle(opacity=0.9, stroke='white', strokeWidth=1).encode(
                x=alt.X('x', axis=None), y=alt.Y('y', axis=None),
                size=alt.Size('size', legend=None),
                color=alt.Color('note', scale=alt.Scale(scheme=color_scheme), legend=None),
                tooltip=['note']
            )
            top = alt.Chart(star).mark_point(shape='star', fill='#FFC107', size=600, stroke='none').encode(x='x', y='y')
            
            final_chart = (base + top).properties(height=350, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True)
            st.caption("▲ 숫자가 쌓여 만들어진 멜로디 트리")

        st.write("")
        if st.button(f"🔔 캐롤 듣기 (Play)", key=f"btn_{key}"):
            with st.spinner("음악을 만들고 있습니다..."):
                bpm = 120 if final_style == "joyful" else 100 if final_style == "waltz" else 80
                audio = compose_music(final_nums, bpm, final_style)
                if audio is not None:
                    virtual_file = io.BytesIO()
                    write(virtual_file, 44100, (audio * 32767).astype(np.int16))
                    st.audio(virtual_file, format='audio/wav')

# --- Main Page ---
st.markdown("""
<div class="header-box">
    <div class="header-title">Merry Math Christmas</div>
    <div class="header-sub">중학교 수학으로 꾸미는 나만의 멜로디 트리 🎄</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["🔴 중1 도형", "🟢 중2 유리수", "🟡 중3 제곱근", "🟣 자유 탐구"])

with t1:
    render_content("t1", "b-red", "중1 - 도형의 성질", "원주율(π) 징글벨", 
        "원은 완벽한 대칭입니다. 하지만 원주율(3.14...)은 불규칙하게 끝없이 이어지죠. 이 숫자들을 **'경쾌한 셔플 리듬'**으로 연주하면 신나는 썰매 노래가 됩니다!", 
        "314159265358979323846264338327950288419716939937510", "joyful", "reds")

with t2:
    render_content("t2", "b-green", "중2 - 유리수와 순환소수", "순환소수 왈츠", 
        "1 나누기 7은 **0.142857...** 처럼 같은 숫자가 계속 반복됩니다. 이 규칙적인 패턴은 춤추기 좋은 **'3박자 왈츠'**와 완벽하게 어울립니다.", 
        "142857142857142857142857142857142857142857", "waltz", "greens")

with t3:
    render_content("t3", "b-gold", "중3 - 제곱근과 실수", "루트2의 거룩한 밤", 
        "제곱해서 2가 되는 수, **루트2(1.414...)**는 인류가 처음 발견한 무리수입니다. 끝을 알 수 없는 깊은 숫자를 **'웅장한 합창'**으로 표현했습니다.", 
        "141421356237309504880168872420969807856967187537694", "holy", "oranges")

with t4:
    render_content("t4", "b-purple", "자유 학기제 탐구", "나만의 숫자 캐롤", 
        "여러분의 생일이나 기념일을 입력해보세요. 수학적 규칙이 여러분의 소중한 숫자를 **세상에 하나뿐인 캐롤**로 바꿔줄 거예요.", 
        "12251225", "joyful", "purples")

st.markdown("<br><hr style='border-top: 1px dashed #ddd;'><div style='text-align:center; color:#90A4AE; font-size:0.9rem;'>즐거운 수학 체험 활동 | Designed for Education</div>", unsafe_allow_html=True)
