import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
import pandas as pd
import altair as alt

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Carol Frame Edition", page_icon="🎄", layout="wide")

# --- 2. 🎨 Christmas Frame Design ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700;900&family=Mountains+of+Christmas:wght@700&display=swap');
    
    /* [전체 배경 - 칠판 느낌] */
    .stApp {
        background-color: #2d3436 !important;
        background-image: url('https://www.transparenttextures.com/patterns/chalkboard.png'); /* 칠판 텍스처 */
        color: #dfe6e9 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* [눈 효과] */
    .snowflake { position: fixed; top: -10px; z-index: 99; color: #dfe6e9; font-size: 1.2em; animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translateY(-10vh); } 100% { transform: translateY(110vh); } }

    /* [메인 타이틀 - 크리스마스 리스 프레임] */
    .title-container {
        text-align: center; padding: 40px;
        background: url('https://i.imgur.com/8Q7Y46K.png') no-repeat center center; /* 크리스마스 리스 이미지 (예시) */
        background-size: contain;
        margin-bottom: 30px;
    }
    .main-title {
        font-family: 'Mountains of Christmas', cursive; font-size: 4.5rem; color: #e74c3c;
        text-shadow: 3px 3px 0px #2d3436, 5px 5px 0px #c0392b; margin: 0;
    }
    .sub-title { font-family: 'Noto Sans KR', sans-serif; color: #b2bec3; font-size: 1.2rem; letter-spacing: 2px; margin-top: 10px; }

    /* [탭 스타일 - 선물 상자 느낌] */
    div[data-baseweb="tab-list"] { gap: 15px; margin-bottom: 25px; }
    button[data-baseweb="tab"] {
        background: #636e72 !important; color: #dfe6e9 !important; border: 2px solid #b2bec3 !important;
        border-radius: 15px 15px 0 0 !important; font-weight: bold; font-size: 1.1rem;
        padding: 10px 20px;
    }
    /* 선택된 탭 강조 */
    button[data-baseweb="tab"][aria-selected="true"] {
        background: #e74c3c !important; color: #fff !important; border-color: #c0392b !important;
    }

    /* [카드 스타일 - 수학 공책 프레임] */
    .music-card {
        background: rgba(255, 255, 255, 0.95); color: #2d3436;
        border: 5px solid #b2bec3; border-radius: 25px;
        padding: 35px; box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        margin-bottom: 25px; height: 100%;
        background-image: url('https://www.transparenttextures.com/patterns/graphy.png'); /* 모눈종이 텍스처 */
    }

    /* [버튼 스타일 - 크리스마스 장식] */
    .stButton>button {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%) !important;
        color: white !important; border-radius: 20px; height: 70px; font-size: 1.4rem; font-weight: 800; border: 3px solid #f1c40f !important; /* 금테 */
        box-shadow: 0 8px 20px rgba(192, 57, 43, 0.5); transition: 0.3s; width: 100%;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 12px 25px rgba(192, 57, 43, 0.6); }

    /* [기타 스타일] */
    .badge { padding: 8px 16px; border-radius: 25px; font-size: 1rem; font-weight: bold; color: white; display: inline-block; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); }
    .b-1 { background-color: #e74c3c; } .b-2 { background-color: #27ae60; } .b-3 { background-color: #f1c40f; color: #333; }
    .desc-box { font-size: 1.1rem; line-height: 1.8; color: #555; background: #fff; padding: 25px; border-radius: 20px; border: 3px dashed #c0392b; }
    h2 { font-family: 'Mountains of Christmas', cursive; color: #c0392b; font-size: 2.5rem; }
</style>
""", unsafe_allow_html=True)

# 눈 효과
def create_snow():
    snow_html = "".join([f'<div class="snowflake" style="left:{np.random.randint(0,100)}vw; animation-duration:{np.random.uniform(8, 15)}s; animation-delay:{np.random.uniform(0, 5)}s;">❄</div>' for _ in range(40)])
    st.markdown(snow_html, unsafe_allow_html=True)
create_snow()

# --- 3. 🎹 Audio Engine (이전과 동일) ---
# (지면 관계상 오디오 엔진 코드는 생략하고 이전 버전과 동일하게 사용합니다. 실제 실행 시에는 이전 코드의 오디오 엔진 부분을 여기에 포함시켜야 합니다.)
# ... [오디오 엔진 코드 삽입] ...
# (편의를 위해 핵심 함수만 간략히 포함)
def get_sine(freq, duration): t = np.linspace(0, duration, int(44100 * duration), False); return np.sin(2 * np.pi * freq * t)
def apply_envelope(wave, duration, type="plucked"): length = len(wave); env = np.exp(np.linspace(0, -4, length)) if type == "plucked" else np.concatenate([np.linspace(0,1,int(length*0.2)), np.full(length-int(length*0.2)-int(length*0.4),1.0), np.linspace(1,0,int(length*0.4))]); return wave * np.resize(env, length)
def synth_bell(freq, duration): return apply_envelope(np.sin(2 * np.pi * freq * t + 2.0 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-3*t)), duration, "plucked")
# ... (나머지 악기 및 작곡 함수 동일) ...

# --- 4. UI 렌더링 함수 (새로운 트리 비주얼 적용) ---

def render_content(key, style, title, badge, desc, default_nums):
    c1, c2 = st.columns([1, 1], gap="large")
    
    with c1:
        st.markdown(f'<div class="music-card">', unsafe_allow_html=True)
        st.markdown(f'{badge}', unsafe_allow_html=True)
        st.markdown(f"## {title}")
        st.markdown(f'<div class="desc-box">{desc}</div>', unsafe_allow_html=True)
        
        user_in = st.text_input("숫자 입력 (나만의 악보 만들기)", value=default_nums, key=f"in_{key}")
        nums = "".join(filter(str.isdigit, user_in))
        
        style_desc = {"joyful": "🔔 <b>Joyful:</b> 징글벨처럼 신나는 셔플 리듬", "waltz": "💃 <b>Waltz:</b> 우아하고 몽환적인 3박자 춤곡", "holy": "👼 <b>Holy:</b> 웅장하고 성스러운 대성당의 합창"}[style]
        st.caption(style_desc, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="music-card">', unsafe_allow_html=True)
        
        # [VISUAL NEW] 음계 연동 트리 비주얼라이저
        colors = {'joyful': 'reds', 'waltz': 'greens', 'holy': 'oranges'}
        if nums:
            digits = [int(d) for d in nums[:30] if d != '0'] # 더 많은 숫자 표시
            tree_data = []
            
            # 트리 모양 배치를 위한 계산 (아래는 넓고 위는 좁게)
            max_width = 10 # 트리 밑단 최대 너비
            height_scale = 1.5 # 트리 높이 비율

            for i, d in enumerate(digits):
                # Y축: 숫자가 클수록(높은 음) 위쪽으로
                level = d * height_scale
                # X축: 숫자가 작을수록(낮은 음) 바깥쪽으로 퍼짐 (트리 모양)
                spread = (10 - d) * max_width / 10 
                # X 좌표를 좌우로 번갈아 배치하여 균형 맞춤
                pos = spread * (1 if i % 2 == 0 else -1) * np.random.uniform(0.5, 1.0)

                tree_data.append({'Level': level, 'Pos': pos, 'Note': d, 'Order': i})
            
            df = pd.DataFrame(tree_data)
            
            # 별 장식 (트리 꼭대기)
            star = pd.DataFrame({'Level': [11 * height_scale], 'Pos': [0], 'Note': [11], 'Order': [-1]})
            df = pd.concat([df, star], ignore_index=True)

            # 기본 마커 (동그라미 장식)
            base = alt.Chart(df).mark_circle(size=300, opacity=0.9).encode(
                x=alt.X('Pos', axis=None),
                y=alt.Y('Level', axis=None, scale=alt.Scale(domain=[0, 12*height_scale])),
                color=alt.Color('Note', scale=alt.Scale(scheme=colors[style], domain=[0, 11]), legend=None),
                tooltip=['Note', 'Order']
            )

            # 별 마커 (꼭대기 강조)
            star_marker = base.transform_filter(alt.datum.Note == 11).mark_point(shape='star', size=800, fill='gold')
            
            # 최종 차트 결합
            chart = alt.layer(base, star_marker).properties(height=400).configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)
            st.caption("▲ 숫자의 높낮이가 트리의 장식이 되었어요!")
        
        # 재생 버튼 (이전 코드와 동일한 로직 사용)
        if st.button(f"🎼 Play {title}", key=f"btn_{key}"):
            # ... [오디오 생성 및 재생 코드 삽입] ...
            pass # (실제 코드에서는 이 부분에 오디오 생성 로직이 들어가야 합니다.)

        st.markdown('</div>', unsafe_allow_html=True)

# --- Main UI ---

st.markdown("""
<div class="title-container">
    <h1 class="main-title">CHRISTMAS MATH CAROL</h1>
    <div class="sub-title">수학으로 꾸미는 나만의 멜로디 트리</div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🔴 1학년 (도형)", "🟢 2학년 (수)", "🟡 3학년 (무리수)"])

with t1:
    render_content(
        "t1", "joyful", "원주율 (Pi) 징글벨", 
        '<span class="badge b-1">중1 - 도형의 성질</span>',
        """
        <b>3.141592...</b> 원주율은 끝없이 이어지는 비순환 소수입니다.
        규칙 없는 숫자들이 만드는 예측 불가능한 멜로디가
        마치 썰매를 타고 달리는 듯한 신나는 캐롤이 됩니다! 🛷
        """,
        "314159265358979323846264338327950288419716939937510"
    )
# ... (t2, t3 탭 내용도 동일한 방식으로 작성) ...

st.markdown("<br><hr><div style='text-align:center; color:#b2bec3;'>Designed for Joyful Math Education 🎁</div>", unsafe_allow_html=True)
