import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Math Music", page_icon="🎵", layout="wide")

# --- 2. 스타일링 (완전히 현대적인 디자인) ---
st.markdown("""
<style>
    /* 1. 폰트 변경: 요즘 스타일의 깔끔한 고딕체(Pretendard/System font) 적용 */
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif !important;
        color: #171717 !important;
    }
    
    /* 2. 배경: 깨끗한 화이트 & 연한 그레이 */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* 3. 제목 스타일: 굵고 모던하게 */
    h1 {
        font-weight: 800;
        letter-spacing: -1px;
        color: #111 !important;
        margin-bottom: 10px;
    }
    
    /* 4. 카드 디자인 (박스) */
    .modern-card {
        background-color: #F8F9FA; /* 아주 연한 회색 */
        padding: 24px;
        border-radius: 16px; /* 둥근 모서리 */
        border: 1px solid #E9ECEF;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); /* 아주 은은한 그림자 */
    }
    
    /* 5. 팁 박스 (말풍선 느낌) */
    .tip-box {
        background-color: #E3F2FD; /* 산뜻한 파랑 */
        padding: 16px;
        border-radius: 12px;
        color: #0D47A1;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .tip-box b { color: #0056b3; }

    /* 6. 입력창 & 버튼 디자인 */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #fff;
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    .stButton>button {
        background-color: #111 !important; /* 검정 버튼 */
        color: #fff !important;
        border-radius: 10px;
        height: 50px;
        font-weight: 600;
        border: none;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #333 !important;
        transform: scale(1.01);
    }
    
    /* 7. 차트 색상 커스텀 */
    div[data-testid="stBarChart"] {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 오디오 엔진 (소리 개선됨) ---
def generate_tone(freq, duration, wave_type):
    sample_
