import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import io

# ---------------------------------------------------------------
# 페이지 설정
# ---------------------------------------------------------------
st.set_page_config(
    page_title="이미지 데이터의 변환",
    page_icon="🎨",
    layout="wide",
)

# 행렬을 스크롤 없이 모두 보여주기 위한 CSS
st.markdown(
    """
    <style>
    /* st.dataframe 내부 셀/헤더 폰트 축소 */
    div[data-testid="stDataFrame"] * {
        font-size: 11px !important;
    }
    div[data-testid="stDataFrame"] td, 
    div[data-testid="stDataFrame"] th {
        padding: 2px 4px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PIXEL = 30          # 리사이즈 픽셀 크기
DISPLAY_SCALE = 12  # 화면 표시용 배율

# ---------------------------------------------------------------
# 세션 상태 초기화
# ---------------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "img1" not in st.session_state:
    st.session_state.img1 = None
if "img2" not in st.session_state:
    st.session_state.img2 = None


def go_next():
    st.session_state.step += 1


def reset():
    st.session_state.step = 1
    st.session_state.img1 = None
    st.session_state.img2 = None


# ---------------------------------------------------------------
# 유틸 함수
# ---------------------------------------------------------------
def load_and_resize(uploaded, size=PIXEL):
    """업로드된 이미지를 RGB로 변환 후 size x size 로 리사이즈."""
    img = Image.open(uploaded).convert("RGB")
    img = img.resize((size, size), Image.LANCZOS)
    return img


def show_image(arr, caption=""):
    """numpy 배열을 픽셀이 보이도록 확대해서 표시."""
    if arr.ndim == 2:
        pil = Image.fromarray(arr.astype(np.uint8), mode="L")
    else:
        pil = Image.fromarray(arr.astype(np.uint8), mode="RGB")
    pil_big = pil.resize(
        (PIXEL * DISPLAY_SCALE, PIXEL * DISPLAY_SCALE), Image.NEAREST
    )
    st.image(pil_big, caption=caption)


def show_matrix(arr, fmt="{:d}"):
    """30x30 행렬 전체가 스크롤 없이 보이도록 출력."""
    if np.issubdtype(arr.dtype, np.floating):
        df = pd.DataFrame(np.round(arr, 1))
    else:
        df = pd.DataFrame(arr.astype(int))
    df.columns = [str(i) for i in range(df.shape[1])]
    # 30행 전부 표시되도록 충분한 높이 지정 (행당 ~22px + 헤더)
    row_h = 22
    height = row_h * (df.shape[0] + 1) + 8
    st.dataframe(df, height=height, use_container_width=True)


# ---------------------------------------------------------------
# 사이드바: 진행 상태 + 리셋
# ---------------------------------------------------------------
with st.sidebar:
    st.title("📚 진행 단계")
    steps = [
        "1️⃣ RGB 채널 출력",
        "2️⃣ 흑백 이미지 변환",
        "3️⃣ 행렬의 실수배 (kA)",
        "4️⃣ 이미지 교차 교환 (aA+(1-a)B)",
    ]
    for i, name in enumerate(steps, start=1):
        if i < st.session_state.step:
            st.markdown(f"✅ {name}")
        elif i == st.session_state.step:
            st.markdown(f"🟢 **{name}**")
        else:
            st.markdown(f"⚪ {name}")

    st.divider()
    if st.button("🔄 처음부터 다시 시작"):
        reset()
        st.rerun()

# ---------------------------------------------------------------
# 메인
# ---------------------------------------------------------------
st.title("🎨 이미지 데이터의 변환")
st.caption(f"이미지를 {PIXEL}×{PIXEL} 픽셀로 축소한 뒤 단계별로 행렬 연산을 수행합니다.")
st.divider()

# ===============================================================
# 1단계: 컬러 이미지 RGB 채널 출력
# ===============================================================
st.header("1단계 · 컬러 이미지 RGB 채널 출력")
st.write(
    f"컬러 이미지를 업로드하면 **{PIXEL}×{PIXEL}** 픽셀로 축소한 뒤 "
    "Red / Green / Blue 채널 이미지와 각 채널의 행렬(0~255)을 출력합니다."
)

uploaded1 = st.file_uploader(
    "컬러 이미지 1개 업로드", type=["png", "jpg", "jpeg", "bmp", "webp"], key="u1"
)

if uploaded1 is not None:
    st.session_state.img1 = load_and_resize(uploaded1)

if st.session_state.img1 is not None:
    arr1 = np.array(st.session_state.img1)  # (30,30,3)
    R, G, B = arr1[:, :, 0], arr1[:, :, 1], arr1[:, :, 2]

    # R 채널
    st.subheader("🟥 Red 채널")
    cR1, cR2 = st.columns([1, 2])
    with cR1:
        red_img = np.zeros_like(arr1)
        red_img[:, :, 0] = R
        show_image(red_img, "Red 채널 이미지")
    with cR2:
        st.markdown("**R 행렬 (0~255)**")
        show_matrix(R)

    # G 채널
    st.subheader("🟩 Green 채널")
    cG1, cG2 = st.columns([1, 2])
    with cG1:
        green_img = np.zeros_like(arr1)
        green_img[:, :, 1] = G
        show_image(green_img, "Green 채널 이미지")
    with cG2:
        st.markdown("**G 행렬 (0~255)**")
        show_matrix(G)

    # B 채널
    st.subheader("🟦 Blue 채널")
    cB1, cB2 = st.columns([1, 2])
    with cB1:
        blue_img = np.zeros_like(arr1)
        blue_img[:, :, 2] = B
        show_image(blue_img, "Blue 채널 이미지")
    with cB2:
        st.markdown("**B 행렬 (0~255)**")
        show_matrix(B)

    if st.session_state.step == 1:
        st.success("✅ 1단계 완료! 아래 버튼을 눌러 다음 단계로 진행하세요.")
        st.button("➡️ 다음 단계로 진행", on_click=go_next, key="next1")

# ===============================================================
# 2단계: 흑백 이미지로 변환
# ===============================================================
if st.session_state.step >= 2 and st.session_state.img1 is not None:
    st.divider()
    st.header("2단계 · 흑백 이미지로 변환")
    st.latex(r"M = \tfrac{1}{3}R + \tfrac{1}{3}G + \tfrac{1}{3}B")

    arr1 = np.array(st.session_state.img1).astype(np.float32)
    A = (arr1[:, :, 0] + arr1[:, :, 1] + arr1[:, :, 2]) / 3.0
    A_int = np.clip(A, 0, 255).astype(np.uint8)
    st.session_state.A = A  # 다음 단계에서 사용

    c1, c2 = st.columns([1, 2])
    with c1:
        show_image(A_int, "그레이스케일 이미지")
    with c2:
        st.markdown("**행렬 A (0~255)**")
        show_matrix(A_int)

    if st.session_state.step == 2:
        st.success("✅ 2단계 완료! 아래 버튼을 눌러 다음 단계로 진행하세요.")
        st.button("➡️ 다음 단계로 진행", on_click=go_next, key="next2")

# ===============================================================
# 3단계: 행렬의 실수배
# ===============================================================
if st.session_state.step >= 3 and "A" in st.session_state:
    st.divider()
    st.header("3단계 · 행렬의 실수배 (kA)")
    st.write("슬라이더로 k값을 조절하여 결과를 확인하세요. 픽셀값이 255를 넘으면 255로 고정됩니다.")

    k = st.slider("k 값", min_value=0.0, max_value=100.0, value=1.0, step=0.1, key="kval")

    A = st.session_state.A
    kA = k * A
    kA_clipped = np.clip(kA, 0, 255).astype(np.uint8)

    c1, c2 = st.columns([1, 2])
    with c1:
        show_image(kA_clipped, f"kA 이미지 (k={k})")
    with c2:
        st.markdown(f"**행렬 kA (k={k}, 255 클리핑 적용)**")
        show_matrix(kA_clipped)

    if st.session_state.step == 3:
        st.success("✅ 3단계 완료! 아래 버튼을 눌러 다음 단계로 진행하세요.")
        st.button("➡️ 다음 단계로 진행", on_click=go_next, key="next3")

# ===============================================================
# 4단계: 이미지 교차 교환
# ===============================================================
if st.session_state.step >= 4 and "A" in st.session_state:
    st.divider()
    st.header("4단계 · 이미지 교차 교환")
    st.latex(r"C = aA + (1-a)B,\quad 0 \le a \le 1")

    uploaded2 = st.file_uploader(
        "두 번째 이미지 업로드 (행렬 B로 사용)",
        type=["png", "jpg", "jpeg", "bmp", "webp"],
        key="u2",
    )
    if uploaded2 is not None:
        st.session_state.img2 = load_and_resize(uploaded2)

    if st.session_state.img2 is not None:
        arr2 = np.array(st.session_state.img2).astype(np.float32)
        B_mat = (arr2[:, :, 0] + arr2[:, :, 1] + arr2[:, :, 2]) / 3.0

        a = st.slider("a 값", min_value=0.0, max_value=1.0, value=0.5, step=0.01, key="aval")

        A = st.session_state.A
        C = a * A + (1 - a) * B_mat
        C_clipped = np.clip(C, 0, 255).astype(np.uint8)

        c1, c2 = st.columns([1, 2])
        with c1:
            show_image(C_clipped, f"이미지 C (a={a})")
        with c2:
            st.markdown(f"**행렬 C (a={a})**")
            show_matrix(C_clipped)

        st.success("🎉 모든 단계가 완료되었습니다! 슬라이더를 움직여 결과를 자유롭게 비교해보세요.")
    else:
        st.info("⬆️ 두 번째 이미지를 업로드하면 결과가 표시됩니다.")
