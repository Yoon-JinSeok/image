
import streamlit as st
import numpy as np
from PIL import Image
import io

# ---------------- 페이지 설정 ----------------
st.set_page_config(page_title="이미지 데이터의 변환", layout="wide")

# ---------------- 전역 CSS ----------------
st.markdown(
    """
    <style>
    /* 행렬 테이블 - 정사각형 셀 */
    table.mat {
        border-collapse: collapse;
        font-family: Consolas, Menlo, monospace;
        font-size: 8px;
        line-height: 1;
        table-layout: fixed;
        width: auto;            /* 내용 크기에 맞게 */
        margin: 0 auto;         /* 가운데 정렬 */
    }
    table.mat td, table.mat th {
        width: 16px;
        height: 16px;
        min-width: 16px;
        max-width: 16px;
        padding: 0;
        margin: 0;
        text-align: center;
        vertical-align: middle;
        border: 1px solid #ddd;
        box-sizing: border-box;
        overflow: hidden;
    }
    table.mat th {
        background: #f3f3f3;
        font-weight: 600;
        color: #555;
    }
    /* 행렬 컨테이너 */
    .mat-wrap {
        overflow: visible;
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- 상수 ----------------
PIXEL = 30          # 30 x 30 픽셀
DISPLAY_SCALE = 12  # 이미지를 화면에 표시할 때 확대 배율 (픽셀 격자가 보이도록)

# ---------------- 유틸 함수 ----------------
def load_and_resize(file) -> Image.Image:
    """업로드된 파일을 RGB로 변환 후 30x30으로 리사이즈"""
    img = Image.open(file).convert("RGB")
    img = img.resize((PIXEL, PIXEL), Image.LANCZOS)
    return img

def upscale_for_display(arr: np.ndarray) -> Image.Image:
    """행렬(또는 이미지)을 화면 표시용으로 확대"""
    if arr.ndim == 2:
        img = Image.fromarray(arr.astype(np.uint8), mode="L")
    else:
        img = Image.fromarray(arr.astype(np.uint8), mode="RGB")
    return img.resize(
        (PIXEL * DISPLAY_SCALE, PIXEL * DISPLAY_SCALE), Image.NEAREST
    )

def matrix_to_html(M: np.ndarray, decimals: int = 0) -> str:
    """numpy 2D 배열을 정사각형 HTML 테이블로 변환"""
    M = np.asarray(M)
    if decimals == 0:
        fmt = lambda v: f"{int(round(float(v)))}"
    else:
        fmt = lambda v: f"{float(v):.{decimals}f}"

    rows, cols = M.shape
    html = ['<div class="mat-wrap"><table class="mat">']
    # 헤더(열 번호)
    html.append("<tr><th></th>")
    for c in range(cols):
        html.append(f"<th>{c}</th>")
    html.append("</tr>")
    # 본문
    for r in range(rows):
        html.append(f"<tr><th>{r}</th>")
        for c in range(cols):
            html.append(f"<td>{fmt(M[r, c])}</td>")
        html.append("</tr>")
    html.append("</table></div>")
    return "".join(html)

def show_matrix(M: np.ndarray, decimals: int = 0):
    st.markdown(matrix_to_html(M, decimals=decimals), unsafe_allow_html=True)

def show_image_and_matrix(img_array: np.ndarray, matrix: np.ndarray,
                          left_caption: str, right_caption: str,
                          decimals: int = 0):
    """좌측 이미지, 우측 행렬을 한 줄로 출력"""
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.markdown(f"**{left_caption}**")
        st.image(upscale_for_display(img_array))
    with col_r:
        st.markdown(f"**{right_caption}**")
        show_matrix(matrix, decimals=decimals)

# ---------------- 세션 상태 ----------------
if "step" not in st.session_state:
    st.session_state.step = 1

def goto(step):
    st.session_state.step = step

# ---------------- 사이드바: 진행 상태 ----------------
st.sidebar.title("📚 진행 단계")
steps_info = [
    (1, "컬러 이미지 RGB 채널 출력"),
    (2, "흑백 이미지로 변환"),
    (3, "행렬의 실수배 (kA)"),
    (4, "이미지의 교차 교환 (aA + (1-a)B)"),
]
for s, name in steps_info:
    if st.session_state.step > s:
        st.sidebar.markdown(f"✅ **{s}단계.** {name}")
    elif st.session_state.step == s:
        st.sidebar.markdown(f"🟢 **{s}단계.** {name}")
    else:
        st.sidebar.markdown(f"⚪ {s}단계. {name}")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 처음부터 다시 시작"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# ---------------- 본문 ----------------
st.title("🎨 이미지 데이터의 변환")
st.caption("컬러 이미지를 30×30으로 축소하여 채널 분리 → 흑백 변환 → 실수배 → 두 이미지의 선형 결합 순서로 진행합니다.")

# ============ 1단계 ============
st.header("1단계 · 컬러 이미지 RGB 채널 출력")
uploaded_1 = st.file_uploader(
    "컬러 이미지 1개를 업로드하세요 (jpg, png 등)",
    type=["jpg", "jpeg", "png", "bmp", "webp"],
    key="img1",
)

if uploaded_1 is not None:
    img1 = load_and_resize(uploaded_1)
    arr = np.array(img1)  # (30,30,3) uint8
    st.session_state.arr_rgb = arr

    st.markdown("**원본 이미지(30×30 축소)**")
    st.image(upscale_for_display(arr), width=PIXEL * DISPLAY_SCALE)

    R = arr[:, :, 0]
    G = arr[:, :, 1]
    B = arr[:, :, 2]

    # 채널별 컬러 이미지(해당 채널만 살리기)
    R_img = np.zeros_like(arr); R_img[:, :, 0] = R
    G_img = np.zeros_like(arr); G_img[:, :, 1] = G
    B_img = np.zeros_like(arr); B_img[:, :, 2] = B

    st.subheader("🔴 Red 채널")
    show_image_and_matrix(R_img, R, "Red 채널 이미지", "Red 채널 행렬 (0~255)")

    st.subheader("🟢 Green 채널")
    show_image_and_matrix(G_img, G, "Green 채널 이미지", "Green 채널 행렬 (0~255)")

    st.subheader("🔵 Blue 채널")
    show_image_and_matrix(B_img, B, "Blue 채널 이미지", "Blue 채널 행렬 (0~255)")

    if st.session_state.step == 1:
        if st.button("➡️ 다음 단계로 진행 (2단계)"):
            goto(2)
            st.rerun()

# ============ 2단계 ============
if st.session_state.step >= 2 and "arr_rgb" in st.session_state:
    st.header("2단계 · 흑백 이미지로 변환")
    st.latex(r"M = \tfrac{1}{3}R + \tfrac{1}{3}G + \tfrac{1}{3}B")

    arr = st.session_state.arr_rgb.astype(np.float32)
    A = (arr[:, :, 0] + arr[:, :, 1] + arr[:, :, 2]) / 3.0
    A = np.clip(A, 0, 255)
    st.session_state.A = A

    show_image_and_matrix(
        A.astype(np.uint8), A.astype(np.uint8),
        "흑백 이미지 (행렬 A)", "행렬 A (0~255)"
    )

    if st.session_state.step == 2:
        if st.button("➡️ 다음 단계로 진행 (3단계)"):
            goto(3)
            st.rerun()

# ============ 3단계 ============
if st.session_state.step >= 3 and "A" in st.session_state:
    st.header("3단계 · 행렬의 실수배 (kA)")
    st.markdown(
        "슬라이드바로 **k** 값을 조절하면 **kA** 의 결과 이미지와 행렬이 갱신됩니다. "
        "픽셀 값이 255를 초과하면 255로 고정(clip)합니다."
    )

    k = st.slider("k 값", min_value=0.0, max_value=100.0, value=1.0, step=0.1, key="k_slider")

    A = st.session_state.A
    kA = np.clip(k * A, 0, 255)

    show_image_and_matrix(
        kA.astype(np.uint8), kA.astype(np.uint8),
        f"kA 이미지 (k = {k:.2f})", f"행렬 kA (k = {k:.2f})"
    )

    if st.session_state.step == 3:
        if st.button("➡️ 다음 단계로 진행 (4단계)"):
            goto(4)
            st.rerun()

# ============ 4단계 ============
if st.session_state.step >= 4 and "A" in st.session_state:
    st.header("4단계 · 이미지의 교차 교환")
    st.latex(r"C = aA + (1-a)B,\quad 0 \le a \le 1")

    uploaded_2 = st.file_uploader(
        "두 번째 이미지(행렬 B)를 업로드하세요",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        key="img2",
    )

    if uploaded_2 is not None:
        img2 = load_and_resize(uploaded_2)
        arr2 = np.array(img2).astype(np.float32)
        B = (arr2[:, :, 0] + arr2[:, :, 1] + arr2[:, :, 2]) / 3.0
        B = np.clip(B, 0, 255)
        st.session_state.B = B

        # 두 번째 이미지(흑백 B) 미리보기
        st.markdown("**두 번째 이미지의 흑백 행렬 B 미리보기**")
        show_image_and_matrix(
            B.astype(np.uint8), B.astype(np.uint8),
            "흑백 이미지 B", "행렬 B (0~255)"
        )

        a = st.slider("a 값", min_value=0.0, max_value=1.0, value=0.5, step=0.01, key="a_slider")

        A = st.session_state.A
        C = a * A + (1 - a) * B
        C = np.clip(C, 0, 255)

        show_image_and_matrix(
            C.astype(np.uint8), C.astype(np.uint8),
            f"이미지 C (a = {a:.2f})", f"행렬 C (a = {a:.2f})"
        )

        st.success("🎉 모든 단계를 완료했습니다!")
