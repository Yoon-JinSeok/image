
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="이미지 데이터의 변환", layout="wide")

st.title("🖼️ 이미지 데이터의 변환")
st.caption("단계별로 이미지를 행렬로 다루어 봅니다.")

# ---------------------------
# 세션 상태 초기화
# ---------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "img_a" not in st.session_state:
    st.session_state.img_a = None  # 30x30 RGB ndarray
if "matrix_A" not in st.session_state:
    st.session_state.matrix_A = None  # 30x30 grayscale ndarray (float)
if "img_b" not in st.session_state:
    st.session_state.img_b = None  # 30x30 RGB ndarray
if "matrix_B" not in st.session_state:
    st.session_state.matrix_B = None  # 30x30 grayscale ndarray (float)


SIZE = 30  # 30x30 픽셀로 축소

def to_small_rgb(file) -> np.ndarray:
    """업로드 파일을 30x30 RGB ndarray(uint8)로 변환"""
    img = Image.open(file).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
    return np.array(img, dtype=np.uint8)

def show_matrix(mat: np.ndarray, fmt="{:d}"):
    """행렬을 데이터프레임으로 보기 좋게 표시"""
    if mat.dtype != np.int64 and mat.dtype != np.int32:
        df = pd.DataFrame(mat).round(1)
    else:
        df = pd.DataFrame(mat)
    st.dataframe(df, height=520, use_container_width=True)

def display_array_as_image(arr: np.ndarray, caption: str):
    """행렬을 이미지로 크게 표시 (확대해서 보여줌)"""
    if arr.ndim == 2:
        pil = Image.fromarray(arr.astype(np.uint8), mode="L")
    else:
        pil = Image.fromarray(arr.astype(np.uint8), mode="RGB")
    # 화면에서 잘 보이도록 확대 (Nearest Neighbor)
    pil_big = pil.resize((SIZE * 12, SIZE * 12), Image.NEAREST)
    st.image(pil_big, caption=caption, use_container_width=False)


# ---------------------------
# 사이드바: 진행 상태
# ---------------------------
st.sidebar.header("진행 단계")
steps_label = {
    1: "1단계 · RGB 채널 분리",
    2: "2단계 · 그레이스케일 변환",
    3: "3단계 · 행렬의 실수배 (kA)",
    4: "4단계 · 이미지 선형보간 (aA + (1-a)B)",
}
for k, v in steps_label.items():
    mark = "✅" if k < st.session_state.step else ("🟢" if k == st.session_state.step else "⚪")
    st.sidebar.write(f"{mark} {v}")

if st.sidebar.button("🔄 처음부터 다시 시작"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()


# =====================================================
# 1단계 : 컬러 이미지 RGB 채널 출력
# =====================================================
st.header("1단계 · 컬러 이미지의 RGB 채널 분리")

st.markdown(
    """
    컬러 이미지를 업로드하면 **30×30 픽셀**로 축소한 뒤,
    **R / G / B** 각 채널 이미지와 0~255 범위의 8비트 행렬을 함께 보여줍니다.
    """
)

uploaded = st.file_uploader("컬러 이미지를 업로드하세요 (jpg/png)", type=["jpg", "jpeg", "png"], key="upload1")

if uploaded is not None:
    rgb = to_small_rgb(uploaded)
    st.session_state.img_a = rgb

    st.subheader("원본 이미지 (30×30로 축소)")
    display_array_as_image(rgb, "원본 RGB")

    channel_names = ["Red", "Green", "Blue"]
    channel_colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]

    for i, (name, color) in enumerate(zip(channel_names, channel_colors)):
        st.markdown(f"### {name} 채널")
        col_img, col_mat = st.columns([1, 1.2])

        # 채널만 강조한 컬러 이미지 (해당 채널 값을 그 색상으로만 표시)
        ch = rgb[:, :, i]
        vis = np.zeros_like(rgb)
        vis[:, :, i] = ch  # 해당 채널만 살림

        with col_img:
            display_array_as_image(vis, f"{name} 채널 이미지")
        with col_mat:
            st.write(f"**{name} 채널 행렬 (0~255)**")
            show_matrix(ch.astype(int))

    st.success("1단계 완료! 아래 버튼을 눌러 다음 단계로 진행하세요.")
    if st.button("➡️ 2단계로 진행", key="to2"):
        st.session_state.step = max(st.session_state.step, 2)
        st.rerun()


# =====================================================
# 2단계 : 흑백 이미지로 변환
# =====================================================
if st.session_state.step >= 2 and st.session_state.img_a is not None:
    st.header("2단계 · 그레이스케일 흑백 이미지로 변환")
    st.latex(r"M \;=\; \tfrac{1}{3}R + \tfrac{1}{3}G + \tfrac{1}{3}B")

    rgb = st.session_state.img_a
    R = rgb[:, :, 0].astype(np.float64)
    G = rgb[:, :, 1].astype(np.float64)
    B = rgb[:, :, 2].astype(np.float64)
    A = (R + G + B) / 3.0
    st.session_state.matrix_A = A

    col_img, col_mat = st.columns([1, 1.2])
    with col_img:
        display_array_as_image(np.clip(A, 0, 255).astype(np.uint8), "흑백 이미지 (행렬 A)")
    with col_mat:
        st.write("**행렬 A (0~255, 소수점 1자리 반올림)**")
        show_matrix(A)

    if st.session_state.step == 2:
        if st.button("➡️ 3단계로 진행", key="to3"):
            st.session_state.step = 3
            st.rerun()


# =====================================================
# 3단계 : 행렬의 실수배
# =====================================================
if st.session_state.step >= 3 and st.session_state.matrix_A is not None:
    st.header("3단계 · 행렬의 실수배 ( kA )")
    st.markdown("슬라이더로 **k 값(0~100)**을 조절하세요. 픽셀 값이 255를 넘으면 255로 고정됩니다.")

    k = st.slider("k 값", min_value=0.0, max_value=100.0, value=1.0, step=0.1, key="k_slider")

    A = st.session_state.matrix_A
    kA = k * A
    kA_clipped = np.clip(kA, 0, 255)

    col_img, col_mat = st.columns([1, 1.2])
    with col_img:
        display_array_as_image(kA_clipped.astype(np.uint8), f"k·A 이미지 (k = {k:.1f})")
    with col_mat:
        st.write(f"**행렬 kA (k = {k:.1f}, 255 초과 시 255로 클리핑)**")
        show_matrix(kA_clipped)

    if st.session_state.step == 3:
        if st.button("➡️ 4단계로 진행", key="to4"):
            st.session_state.step = 4
            st.rerun()


# =====================================================
# 4단계 : 이미지의 교차 교환
# =====================================================
if st.session_state.step >= 4 and st.session_state.matrix_A is not None:
    st.header("4단계 · 이미지의 교차 교환 (선형 보간)")
    st.latex(r"C \;=\; a\,A + (1-a)\,B,\quad 0 \le a \le 1")

    uploaded2 = st.file_uploader(
        "두 번째 이미지를 업로드하세요 (jpg/png)",
        type=["jpg", "jpeg", "png"],
        key="upload2",
    )

    if uploaded2 is not None:
        rgb_b = to_small_rgb(uploaded2)
        st.session_state.img_b = rgb_b
        Rb = rgb_b[:, :, 0].astype(np.float64)
        Gb = rgb_b[:, :, 1].astype(np.float64)
        Bb = rgb_b[:, :, 2].astype(np.float64)
        B_mat = (Rb + Gb + Bb) / 3.0
        st.session_state.matrix_B = B_mat

        st.subheader("두 번째 이미지(흑백 변환) 미리보기")
        col1, col2 = st.columns(2)
        with col1:
            display_array_as_image(st.session_state.img_a, "이미지 A (원본)")
        with col2:
            display_array_as_image(np.clip(B_mat, 0, 255).astype(np.uint8), "이미지 B (흑백)")

        a = st.slider("a 값", min_value=0.0, max_value=1.0, value=0.5, step=0.01, key="a_slider")

        A = st.session_state.matrix_A
        C = a * A + (1.0 - a) * B_mat
        C_clipped = np.clip(C, 0, 255)

        col_img, col_mat = st.columns([1, 1.2])
        with col_img:
            display_array_as_image(C_clipped.astype(np.uint8), f"이미지 C (a = {a:.2f})")
        with col_mat:
            st.write(f"**행렬 C = aA + (1-a)B  (a = {a:.2f})**")
            show_matrix(C_clipped)

        st.success("🎉 모든 단계를 완료했습니다!")
