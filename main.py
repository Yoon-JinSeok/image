import streamlit as st
import numpy as np
from PIL import Image
import io

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(page_title="이미지 데이터의 변환", layout="wide")

# 행렬(표)을 스크롤 없이 한 번에 보여주기 위한 CSS
st.markdown("""
<style>
.matrix-table {
    border-collapse: collapse;
    width: 100%;
    table-layout: fixed;
    font-family: "Consolas", "Menlo", monospace;
}
.matrix-table th, .matrix-table td {
    border: 1px solid #d0d0d0;
    text-align: center;
    padding: 0px 0px;
    font-size: 8px;
    line-height: 11px;
    height: 12px;
    overflow: hidden;
}
.matrix-table th {
    background-color: #f2f2f2;
    font-weight: 600;
}
.matrix-wrap {
    width: 100%;
    overflow: visible;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 상수 및 세션 상태
# ============================================================
PIXEL = 30  # 30 x 30 으로 축소

if "step" not in st.session_state:
    st.session_state.step = 1

def go_next():
    st.session_state.step += 1

def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.step = 1

# ============================================================
# 유틸 함수
# ============================================================
def load_and_resize(file, size=PIXEL):
    """업로드된 파일을 RGB로 열고 size x size 로 축소."""
    img = Image.open(file).convert("RGB")
    img = img.resize((size, size), Image.LANCZOS)
    return img

def upscale_for_view(arr, scale=12, mode="RGB"):
    """작은 이미지를 픽셀 격자가 보이도록 NEAREST 로 확대."""
    if arr.ndim == 2:
        img = Image.fromarray(arr.astype(np.uint8), mode="L")
    else:
        img = Image.fromarray(arr.astype(np.uint8), mode=mode)
    w, h = img.size
    return img.resize((w * scale, h * scale), Image.NEAREST)

def matrix_to_html(M, decimals=0):
    """numpy 2D 행렬을 스크롤 없는 HTML 테이블로 변환."""
    M = np.asarray(M)
    rows, cols = M.shape
    if decimals == 0:
        fmt = lambda v: f"{int(round(v))}"
    else:
        fmt = lambda v: f"{v:.{decimals}f}"

    html = ['<div class="matrix-wrap"><table class="matrix-table">']
    # 헤더
    html.append("<tr><th></th>" + "".join(f"<th>{c+1}</th>" for c in range(cols)) + "</tr>")
    for r in range(rows):
        html.append(
            f"<tr><th>{r+1}</th>"
            + "".join(f"<td>{fmt(M[r, c])}</td>" for c in range(cols))
            + "</tr>"
        )
    html.append("</table></div>")
    return "\n".join(html)

def show_matrix(M, decimals=0):
    """행렬을 스크롤 없이 모두 표시."""
    st.markdown(matrix_to_html(M, decimals=decimals), unsafe_allow_html=True)

# ============================================================
# 사이드바: 진행 상태
# ============================================================
with st.sidebar:
    st.header("📌 진행 상태")
    steps_label = [
        "1. RGB 채널 출력",
        "2. 흑백(그레이스케일) 변환",
        "3. 행렬의 실수배 (kA)",
        "4. 이미지의 교차 교환 (aA + (1-a)B)",
    ]
    for i, lbl in enumerate(steps_label, start=1):
        if st.session_state.step > i:
            st.markdown(f"✅ {lbl}")
        elif st.session_state.step == i:
            st.markdown(f"🟢 **{lbl}**")
        else:
            st.markdown(f"⚪ {lbl}")
    st.divider()
    if st.button("🔄 처음부터 다시 시작"):
        reset_all()
        st.rerun()

# ============================================================
# 헤더
# ============================================================
st.title("🎨 이미지 데이터의 변환")
st.caption(f"이미지를 {PIXEL}×{PIXEL} 픽셀로 축소하여 행렬로 다룹니다. 단계별로 [다음 단계로 진행] 버튼을 눌러주세요.")

# ============================================================
# STEP 1 : 컬러 이미지 RGB 채널 출력
# ============================================================
st.header("1단계 · 컬러 이미지 RGB 채널 출력")

uploaded = st.file_uploader(
    "컬러 이미지 1장을 업로드하세요 (jpg, png, bmp 등)",
    type=["jpg", "jpeg", "png", "bmp", "webp"],
    key="img1",
)

if uploaded is not None:
    img_small = load_and_resize(uploaded, PIXEL)
    arr = np.array(img_small, dtype=np.uint8)  # (30,30,3)

    R = arr[:, :, 0]
    G = arr[:, :, 1]
    B = arr[:, :, 2]

    st.session_state["arr_rgb"] = arr
    st.session_state["R"] = R
    st.session_state["G"] = G
    st.session_state["B"] = B

    st.subheader("원본(축소) 이미지")
    st.image(upscale_for_view(arr, 8), caption=f"원본 → {PIXEL}×{PIXEL} 축소")

    # R 채널
    st.markdown("#### 🔴 Red 채널")
    c1, c2 = st.columns([1, 2])
    R_img = np.zeros_like(arr); R_img[:, :, 0] = R
    with c1:
        st.image(upscale_for_view(R_img, 12), caption="R 채널 이미지")
    with c2:
        st.markdown("**R 행렬 (0~255)**")
        show_matrix(R)

    # G 채널
    st.markdown("#### 🟢 Green 채널")
    c1, c2 = st.columns([1, 2])
    G_img = np.zeros_like(arr); G_img[:, :, 1] = G
    with c1:
        st.image(upscale_for_view(G_img, 12), caption="G 채널 이미지")
    with c2:
        st.markdown("**G 행렬 (0~255)**")
        show_matrix(G)

    # B 채널
    st.markdown("#### 🔵 Blue 채널")
    c1, c2 = st.columns([1, 2])
    B_img = np.zeros_like(arr); B_img[:, :, 2] = B
    with c1:
        st.image(upscale_for_view(B_img, 12), caption="B 채널 이미지")
    with c2:
        st.markdown("**B 행렬 (0~255)**")
        show_matrix(B)

    if st.session_state.step == 1:
        st.button("➡️ 다음 단계로 진행 (2단계)", on_click=go_next, type="primary")
else:
    st.info("⬆️ 위에서 컬러 이미지를 업로드해 주세요.")

# ============================================================
# STEP 2 : 흑백 이미지로 변환
# ============================================================
if st.session_state.step >= 2:
    st.header("2단계 · 흑백(그레이스케일) 변환")
    st.markdown(r"$M = \frac{1}{3}R + \frac{1}{3}G + \frac{1}{3}B$")

    R = st.session_state["R"].astype(np.float64)
    G = st.session_state["G"].astype(np.float64)
    B = st.session_state["B"].astype(np.float64)

    A = (R + G + B) / 3.0
    A_uint8 = np.clip(A, 0, 255).astype(np.uint8)
    st.session_state["A"] = A

    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(upscale_for_view(A_uint8, 12), caption="그레이스케일 이미지")
    with c2:
        st.markdown("**행렬 A (반올림 표시)**")
        show_matrix(A)

    if st.session_state.step == 2:
        st.button("➡️ 다음 단계로 진행 (3단계)", on_click=go_next, type="primary")

# ============================================================
# STEP 3 : 행렬의 실수배
# ============================================================
if st.session_state.step >= 3:
    st.header("3단계 · 행렬의 실수배 (kA)")
    st.caption("k 값을 0~100 사이에서 조절하세요. 픽셀값이 255를 초과하면 255로 고정됩니다.")

    k = st.slider("k 값", 0.0, 100.0, 1.0, 0.1, key="k_val")

    A = st.session_state["A"]
    kA = k * A
    kA_clipped = np.clip(kA, 0, 255)
    kA_uint8 = kA_clipped.astype(np.uint8)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(upscale_for_view(kA_uint8, 12), caption=f"k = {k:.2f} 적용 이미지")
    with c2:
        st.markdown(f"**행렬 kA (k = {k:.2f}, 255 클리핑 적용)**")
        show_matrix(kA_clipped)

    if st.session_state.step == 3:
        st.button("➡️ 다음 단계로 진행 (4단계)", on_click=go_next, type="primary")

# ============================================================
# STEP 4 : 이미지의 교차 교환
# ============================================================
if st.session_state.step >= 4:
    st.header("4단계 · 이미지의 교차 교환")
    st.markdown(r"$C = aA + (1-a)B \quad (0 \le a \le 1)$")

    uploaded2 = st.file_uploader(
        "두 번째 이미지를 업로드하세요 (행렬 B 가 됩니다)",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        key="img2",
    )

    if uploaded2 is not None:
        img2_small = load_and_resize(uploaded2, PIXEL)
        arr2 = np.array(img2_small, dtype=np.uint8)
        R2, G2, B2 = arr2[:, :, 0], arr2[:, :, 1], arr2[:, :, 2]
        Bmat = (R2.astype(np.float64) + G2.astype(np.float64) + B2.astype(np.float64)) / 3.0
        st.session_state["B_mat"] = Bmat

        a = st.slider("a 값", 0.0, 1.0, 0.5, 0.01, key="a_val")
        A = st.session_state["A"]
        C = a * A + (1 - a) * Bmat
        C_clipped = np.clip(C, 0, 255)
        C_uint8 = C_clipped.astype(np.uint8)

        st.subheader("입력된 두 이미지(행렬 A, B의 원본)")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.image(upscale_for_view(np.clip(A, 0, 255).astype(np.uint8), 8),
                     caption="행렬 A (1번 이미지의 그레이스케일)")
        with cc2:
            st.image(upscale_for_view(Bmat.astype(np.uint8), 8),
                     caption="행렬 B (2번 이미지의 그레이스케일)")

        st.subheader(f"합성 결과 C (a = {a:.2f})")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(upscale_for_view(C_uint8, 12), caption=f"C = {a:.2f}·A + {1-a:.2f}·B")
        with c2:
            st.markdown("**행렬 C**")
            show_matrix(C_clipped)
    else:
        st.info("⬆️ 두 번째 이미지를 업로드해 주세요.")
