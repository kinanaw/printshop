import streamlit as st
import pypdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import FloatObject, ArrayObject, NameObject, RectangleObject
import io
import math
import pandas as pd
from PIL import Image
import fitz  # PyMuPDF
import tempfile
import os

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(

    page_title="GolanCopy Roll Organizer",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
col1, col2, col3 = st.columns([0.5, 2, 0.5])
with col2:
    st.image("logo.png", use_container_width=True)
# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --ink: #0a0a0f;
    --paper: #f5f2eb;
    --blueprint: #1a3a5c;
    --cyan: #00b4d8;
    --amber: #f4a261;
    --grid: rgba(26,58,92,0.08);
    --success: #2a9d8f;
    --warning: #e9c46a;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--paper);
    color: var(--ink);
}

/* Blueprint grid background */
.stApp {
    background-color: var(--paper);
    background-image:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 28px 28px;
}

/* Header */
.main-header {
    background: var(--blueprint);
    color: white;
    padding: 2.5rem 3rem;
    margin: -1rem -1rem 2rem -1rem;
    border-bottom: 4px solid var(--cyan);
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(0,180,216,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,180,216,0.06) 1px, transparent 1px);
    background-size: 20px 20px;
}
.main-header h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -1px;
    margin: 0;
    position: relative;
    z-index: 1;
}
.main-header p {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    opacity: 0.75;
    margin: 0.4rem 0 0;
    position: relative;
    z-index: 1;
    letter-spacing: 0.05em;
}

/* Cards */
.card {
    background: white;
    border: 1.5px solid rgba(26,58,92,0.15);
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 3px 3px 0 rgba(26,58,92,0.08);
}

/* Metric boxes */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
}
.metric-box {
    flex: 1;
    background: var(--blueprint);
    color: white;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    border-left: 4px solid var(--cyan);
}
.metric-box .label {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.65;
    font-family: 'Space Mono', monospace;
}
.metric-box .value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'Space Mono', monospace;
    line-height: 1.1;
}
.metric-box .unit {
    font-size: 0.85rem;
    opacity: 0.7;
}

/* Roll tags */
.roll-60 {
    display: inline-block;
    background: rgba(42,157,143,0.12);
    color: var(--success);
    border: 1px solid var(--success);
    border-radius: 2px;
    padding: 0.15rem 0.6rem;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.roll-91 {
    display: inline-block;
    background: rgba(244,162,97,0.12);
    color: var(--amber);
    border: 1px solid var(--amber);
    border-radius: 2px;
    padding: 0.15rem 0.6rem;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.tag-a4 {
    display: inline-block;
    background: rgba(114,9,183,0.1);
    color: #7209b7;
    border: 1px solid #7209b7;
    border-radius: 2px;
    padding: 0.15rem 0.6rem;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.tag-a3 {
    display: inline-block;
    background: rgba(247,37,133,0.1);
    color: #f72585;
    border: 1px solid #f72585;
    border-radius: 2px;
    padding: 0.15rem 0.6rem;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* Section headers */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--blueprint);
    opacity: 0.6;
    margin-bottom: 0.5rem;
    border-bottom: 1px dashed rgba(26,58,92,0.2);
    padding-bottom: 0.3rem;
}

/* Streamlit overrides */
.stButton > button {
    background: var(--blueprint) !important;
    color: white !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.4rem !important;
    box-shadow: 3px 3px 0 rgba(26,58,92,0.2) !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    transform: translate(-1px, -1px) !important;
    box-shadow: 4px 4px 0 rgba(26,58,92,0.3) !important;
}

.stDownloadButton > button {
    background: var(--success) !important;
    color: white !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    box-shadow: 3px 3px 0 rgba(42,157,143,0.25) !important;
    width: 100% !important;
}

div[data-testid="stFileUploader"] {
    border: 2px dashed rgba(26,58,92,0.25) !important;
    border-radius: 6px !important;
    background: rgba(255,255,255,0.6) !important;
}

.stAlert {
    border-radius: 3px !important;
}

/* Table */
.dataframe {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🖨️ GolanCopy Roll Organizer 🗺️</h1>
    <p>Automated PDF sorting, trimming & paper calculation</p>
    <p> made by kinanaw from GolanCopy</p>
    <p> GolanCopy@gmail.com </p>
</div>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────
PTS_PER_CM = 72 / 2.54   # 1 cm = 28.346 pts
ROLL_60_CM = 60.0
ROLL_91_CM = 91.0
ROLL_60_PTS = ROLL_60_CM * PTS_PER_CM
ROLL_91_PTS = ROLL_91_CM * PTS_PER_CM

# Standard paper sizes in pts (tolerance ±5pts ~1.8mm)
A4_W_PTS = 595.28   # 21.0 cm
A4_H_PTS = 841.89   # 29.7 cm
A3_W_PTS = 841.89   # 29.7 cm
A3_H_PTS = 1190.55  # 42.0 cm
SIZE_TOLERANCE = 10.0  # pts


def is_a4(w, h):
    """True if page dimensions match A4 in either orientation."""
    portrait  = abs(w - A4_W_PTS) < SIZE_TOLERANCE and abs(h - A4_H_PTS) < SIZE_TOLERANCE
    landscape = abs(w - A4_H_PTS) < SIZE_TOLERANCE and abs(h - A4_W_PTS) < SIZE_TOLERANCE
    return portrait or landscape


def is_a3(w, h):
    """True if page dimensions match A3 in either orientation."""
    portrait  = abs(w - A3_W_PTS) < SIZE_TOLERANCE and abs(h - A3_H_PTS) < SIZE_TOLERANCE
    landscape = abs(w - A3_H_PTS) < SIZE_TOLERANCE and abs(h - A3_W_PTS) < SIZE_TOLERANCE
    return portrait or landscape


# ─── Helper Functions ────────────────────────────────────────────────────────

def pts_to_cm(pts):
    return pts / PTS_PER_CM

def cm_to_pts(cm):
    return cm * PTS_PER_CM

def get_page_dimensions(page):
    """Return (width_pts, height_pts) for a single PdfReader page."""
    box = page.mediabox
    return float(box.width), float(box.height)

def trim_whitespace_page(page_bytes: bytes) -> bytes:
    """
    Trim white bleed from a single-page PDF bytes.
    Falls back to original if trimming fails or saves <5%.
    """
    try:
        doc = fitz.open(stream=page_bytes, filetype="pdf")
        page = doc[0]
        mat = fitz.Matrix(0.5, 0.5)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
        img = Image.frombytes("L", [pix.width, pix.height], pix.samples)

        import numpy as np
        arr_np = 255 - np.array(img)
        rows = np.any(arr_np > 10, axis=1)
        cols = np.any(arr_np > 10, axis=0)
        if not rows.any():
            doc.close()
            return page_bytes

        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        scale = 2.0
        orig_rect = page.rect
        margin = 5 * scale

        new_rect = fitz.Rect(
            max(0, cmin * scale - margin),
            max(0, rmin * scale - margin),
            min(orig_rect.width, cmax * scale + margin),
            min(orig_rect.height, rmax * scale + margin),
        )

        orig_area = orig_rect.width * orig_rect.height
        new_area = new_rect.width * new_rect.height
        if new_area < orig_area * 0.95:
            page.set_cropbox(new_rect)
            out = io.BytesIO()
            doc.save(out)
            doc.close()
            return out.getvalue()
        else:
            doc.close()
            return page_bytes
    except Exception:
        return page_bytes


def extract_single_page(pdf_bytes: bytes, page_index: int) -> bytes:
    """Extract a single page from a PDF as its own PDF bytes."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    writer.add_page(reader.pages[page_index])
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def categorize_pdfs(files_data: list):
    """
    files_data: list of (filename, bytes)
    Processes ALL pages in every uploaded PDF.
    Each page is treated independently and sorted into:
      roll60_items, roll91_items, a4_items, a3_items
    """
    roll60 = []
    roll91 = []
    a4_items = []
    a3_items = []

    for filename, raw_bytes in files_data:
        reader = PdfReader(io.BytesIO(raw_bytes))
        num_pages = len(reader.pages)

        for page_index in range(num_pages):
            # Label: filename for single-page, "filename (p2)" etc for multi-page
            if num_pages == 1:
                name = filename
            else:
                name = f"{filename} (p{page_index + 1})"

            # Extract this page as its own PDF
            page_bytes = extract_single_page(raw_bytes, page_index)

            # Trim whitespace
            trimmed = trim_whitespace_page(page_bytes)

            # Get dimensions after trimming
            w, h = get_page_dimensions(PdfReader(io.BytesIO(trimmed)).pages[0])
            w_cm = pts_to_cm(w)
            h_cm = pts_to_cm(h)

            # Detect A4/A3 using original (untrimmed) page dimensions
            orig_w, orig_h = get_page_dimensions(reader.pages[page_index])
            base_item = dict(name=name, bytes=trimmed, w_pts=w, h_pts=h,
                             w_cm=w_cm, h_cm=h_cm, rotated=False)

            if is_a4(orig_w, orig_h):
                a4_items.append(base_item)
                continue  # excluded from roll lists
            elif is_a3(orig_w, orig_h):
                a3_items.append(base_item)
                continue  # excluded from roll lists

            # Roll categorization — only non-A4/A3 pages reach here
            if w <= ROLL_60_PTS:
                item = dict(name=name, bytes=trimmed, w_pts=w, h_pts=h,
                            w_cm=w_cm, h_cm=h_cm, rotated=False)
                roll60.append(item)
            elif h <= ROLL_60_PTS:
                item = dict(name=name, bytes=trimmed, w_pts=h, h_pts=w,
                            w_cm=h_cm, h_cm=w_cm, rotated=True)
                roll60.append(item)
            else:
                item = dict(name=name, bytes=trimmed, w_pts=w, h_pts=h,
                            w_cm=w_cm, h_cm=h_cm, rotated=False)
                roll91.append(item)

    return roll60, roll91, a4_items, a3_items


def merge_pdfs(items: list, roll_width_cm: float) -> bytes:
    """
    Merge a list of PDF items into one PDF.
    Each item is placed on its own page.
    If item is marked rotated=True, the page is rotated 90°.
    """
    writer = PdfWriter()

    for item in items:
        reader = PdfReader(io.BytesIO(item['bytes']))
        page = reader.pages[0]
        if item.get('rotated'):
            page.rotate(90)
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def calculate_paper(items: list) -> float:
    """Total paper length in meters (sum of each page's length along roll)."""
    total_cm = sum(item['h_cm'] for item in items)
    return total_cm / 100.0  # convert cm → meters


def round_up_to_half_meter(cm: float) -> float:
    """
    Round a dimension in cm UP to the nearest 50 cm (0.5 m).
    E.g. 159 cm → 200 cm (2.0 m), 370 cm → 400 cm (4.0 m),
         90 cm → 100 cm (1.0 m), 200 cm → 200 cm (2.0 m)
    """
    return math.ceil(cm / 50.0) * 50.0  # result in cm


def calculate_paper_rounded(items: list) -> tuple:
    """
    For each page:
      1. Take max(w_cm, h_cm) — the longer dimension
      2. Round it UP to the nearest 50 cm
      3. Sum all rounded values

    Returns:
        total_rounded_cm (float) — total in cm
        total_rounded_m  (float) — total in meters
        per_page         (list of dicts) — breakdown per page
    """
    per_page = []
    total_rounded_cm = 0.0

    for item in items:
        long_side_cm = max(item['w_cm'], item['h_cm'])
        rounded_cm = round_up_to_half_meter(long_side_cm)
        total_rounded_cm += rounded_cm
        per_page.append({
            'name': item['name'],
            'w_cm': item['w_cm'],
            'h_cm': item['h_cm'],
            'long_side_cm': long_side_cm,
            'rounded_cm': rounded_cm,
            'rounded_m': rounded_cm / 100.0,
        })

    return total_rounded_cm, total_rounded_cm / 100.0, per_page


# ─── Main App ────────────────────────────────────────────────────────────────

col_upload, col_info = st.columns([2, 1])

with col_upload:
    st.markdown('<div class="section-label">Upload Blueprints</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drop your PDF blueprints here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Upload one or more PDF blueprints. The app will auto-sort them by roll size."
    )

with col_info:
    st.markdown("""
    <div class="card" style="margin-top:0">
        <div class="section-label">Output Groups</div>
        <div style="margin-top:.6rem">
            <span class="roll-60">● 60 cm</span>
            <span style="font-size:.85rem; margin-left:.5rem;">Narrow roll</span>
        </div>
        <div style="margin-top:.5rem">
            <span class="roll-91">● 91 cm</span>
            <span style="font-size:.85rem; margin-left:.5rem;">Wide roll</span>
        </div>
        <div style="margin-top:.5rem">
            <span class="tag-a4">● A4</span>
            <span style="font-size:.85rem; margin-left:.5rem;">A4 pages</span>
        </div>
        <div style="margin-top:.5rem">
            <span class="tag-a3">● A3</span>
            <span style="font-size:.85rem; margin-left:.5rem;">A3 pages</span>
        </div>
        <div style="margin-top:1rem; font-size:.8rem; opacity:.6; font-family:'Space Mono',monospace; line-height:1.6">
            PDFs are auto-rotated<br>
            if rotation helps fit.<br>
            White bleed is trimmed<br>
            before sorting.<br>
        </div>
    </div>
    """, unsafe_allow_html=True)


if uploaded_files:
    st.markdown("---")

    # Read all files
    files_data = [(f.name, f.read()) for f in uploaded_files]

    with st.spinner("Analysing PDFs… trimming bleed, detecting dimensions…"):
        roll60_items, roll91_items, a4_items, a3_items = categorize_pdfs(files_data)

    # ── Summary Table ──────────────────────────────────────────────────────
    st.markdown('<div class="section-label">File Analysis</div>', unsafe_allow_html=True)

    all_items = (
        [dict(**i, roll="60 cm") for i in roll60_items] +
        [dict(**i, roll="91 cm") for i in roll91_items] +
        [dict(**i, roll="A4") for i in a4_items] +
        [dict(**i, roll="A3") for i in a3_items]
    )

    a4_names = {i['name'] for i in a4_items}
    a3_names = {i['name'] for i in a3_items}

    table_rows = []
    for item in all_items:
        size_tag = "A4" if item['name'] in a4_names else ("A3" if item['name'] in a3_names else "–")
        table_rows.append({
            "File": item['name'],
            "Width (cm)": f"{item['w_cm']:.1f}",
            "Length (cm)": f"{item['h_cm']:.1f}",
            "Size": size_tag,
            "Rotated": "✓" if item['rotated'] else "–",
            "Roll": item['roll'],
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Metrics ────────────────────────────────────────────────────────────
    paper_60 = calculate_paper(roll60_items)
    paper_91 = calculate_paper(roll91_items)

    # Rounded paper calculations per roll
    paper_60_rounded_cm, paper_60_rounded_m, breakdown_60_rounded = calculate_paper_rounded(roll60_items)
    paper_91_rounded_cm, paper_91_rounded_m, breakdown_91_rounded = calculate_paper_rounded(roll91_items)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Files on 60 cm roll", len(roll60_items))
    with m2:
        st.metric("Paper needed (60 cm)", f"{paper_60:.2f} m",
                  help="Raw total length (no rounding)")
    with m3:
        st.metric("Files on 91 cm roll", len(roll91_items))
    with m4:
        st.metric("Paper needed (91 cm)", f"{paper_91:.2f} m",
                  help="Raw total length (no rounding)")

    # ── Rounded paper totals ───────────────────────────────────────────────
    if roll60_items or roll91_items:
        st.markdown("---")
        st.markdown('<div class="section-label">📐 Rounded Paper Estimate (per page → nearest 0.5 m)</div>',
                    unsafe_allow_html=True)

        rc1, rc2 = st.columns(2)

        with rc1:
            if roll60_items:
                st.markdown(f"""
                <div class="card">
                    <span class="roll-60">60 CM ROLL</span>
                    <div style="margin-top:.6rem; font-family:'Space Mono',monospace; font-size:1.6rem; font-weight:700; color:#1a3a5c;">
                        {paper_60_rounded_m:.1f} m
                    </div>
                    <div style="font-size:.8rem; opacity:.6;">total rounded estimate</div>
                </div>
                """, unsafe_allow_html=True)

        with rc2:
            if roll91_items:
                st.markdown(f"""
                <div class="card">
                    <span class="roll-91">91 CM ROLL</span>
                    <div style="margin-top:.6rem; font-family:'Space Mono',monospace; font-size:1.6rem; font-weight:700; color:#1a3a5c;">
                        {paper_91_rounded_m:.1f} m
                    </div>
                    <div style="font-size:.8rem; opacity:.6;">total rounded estimate</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Paper detail breakdown ─────────────────────────────────────────────
    with st.expander("📏 Paper calculation breakdown"):
        if roll60_items:
            st.markdown("**60 cm roll — raw lengths**")
            breakdown60 = [f"{i['name']} → {i['h_cm']:.1f} cm" for i in roll60_items]
            st.write(" + ".join([f"{i['h_cm']:.1f}" for i in roll60_items]) +
                     f" = **{sum(i['h_cm'] for i in roll60_items):.1f} cm = {paper_60:.2f} m**")
            for b in breakdown60:
                st.write(f"  • {b}")

            st.markdown("**60 cm roll — rounded per page (max side → nearest 50 cm)**")
            for p in breakdown_60_rounded:
                st.write(
                    f"  • {p['name']} → max({p['w_cm']:.1f}, {p['h_cm']:.1f}) = "
                    f"{p['long_side_cm']:.1f} cm → **{p['rounded_cm']:.0f} cm ({p['rounded_m']:.1f} m)**"
                )
            st.write(f"  **Total: {paper_60_rounded_cm:.0f} cm = {paper_60_rounded_m:.1f} m**")

        if roll91_items:
            st.markdown("**91 cm roll — raw lengths**")
            breakdown91 = [f"{i['name']} → {i['h_cm']:.1f} cm" for i in roll91_items]
            st.write(" + ".join([f"{i['h_cm']:.1f}" for i in roll91_items]) +
                     f" = **{sum(i['h_cm'] for i in roll91_items):.1f} cm = {paper_91:.2f} m**")
            for b in breakdown91:
                st.write(f"  • {b}")

            st.markdown("**91 cm roll — rounded per page (max side → nearest 50 cm)**")
            for p in breakdown_91_rounded:
                st.write(
                    f"  • {p['name']} → max({p['w_cm']:.1f}, {p['h_cm']:.1f}) = "
                    f"{p['long_side_cm']:.1f} cm → **{p['rounded_cm']:.0f} cm ({p['rounded_m']:.1f} m)**"
                )
            st.write(f"  **Total: {paper_91_rounded_cm:.0f} cm = {paper_91_rounded_m:.1f} m**")

    # ── Generate & Download ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-label">Download Merged PDFs</div>', unsafe_allow_html=True)

    dl1, dl2, dl3, dl4 = st.columns(4)

    with dl1:
        if roll60_items:
            with st.spinner("Merging 60 cm PDFs…"):
                merged60 = merge_pdfs(roll60_items, ROLL_60_CM)
            st.markdown(f"""
            <div class="card">
                <span class="roll-60">60 CM ROLL</span>
                <div style="margin-top:.7rem; font-size:.9rem;">
                    <strong>{len(roll60_items)} files</strong> · {paper_60:.2f} m paper<br>
                    <span style="color:#2a9d8f; font-family:'Space Mono',monospace; font-weight:700;">
                        📐 {paper_60_rounded_m:.1f} m rounded
                    </span>
                </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="⬇ Download 60cm_roll.pdf",
                data=merged60,
                file_name="60cm_roll.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No PDFs fit the 60 cm roll.")

    with dl2:
        if roll91_items:
            with st.spinner("Merging 91 cm PDFs…"):
                merged91 = merge_pdfs(roll91_items, ROLL_91_CM)
            st.markdown(f"""
            <div class="card">
                <span class="roll-91">91 CM ROLL</span>
                <div style="margin-top:.7rem; font-size:.9rem;">
                    <strong>{len(roll91_items)} files</strong> · {paper_91:.2f} m paper<br>
                    <span style="color:#f4a261; font-family:'Space Mono',monospace; font-weight:700;">
                        📐 {paper_91_rounded_m:.1f} m rounded
                    </span>
                </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="⬇ Download 91cm_roll.pdf",
                data=merged91,
                file_name="91cm_roll.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No PDFs require the 91 cm roll.")

    with dl3:
        if a4_items:
            with st.spinner("Merging A4 PDFs…"):
                merged_a4 = merge_pdfs(a4_items, 21.0)
            st.markdown(f"""
            <div class="card">
                <span class="tag-a4">A4 PAGES</span>
                <div style="margin-top:.7rem; font-size:.9rem;">
                    <strong>{len(a4_items)} files</strong> · 21 × 29.7 cm
                </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="⬇ Download a4_pages.pdf",
                data=merged_a4,
                file_name="a4_pages.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No A4-sized PDFs detected.")

    with dl4:
        if a3_items:
            with st.spinner("Merging A3 PDFs…"):
                merged_a3 = merge_pdfs(a3_items, 29.7)
            st.markdown(f"""
            <div class="card">
                <span class="tag-a3">A3 PAGES</span>
                <div style="margin-top:.7rem; font-size:.9rem;">
                    <strong>{len(a3_items)} files</strong> · 29.7 × 42 cm
                </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="⬇ Download a3_pages.pdf",
                data=merged_a3,
                file_name="a3_pages.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No A3-sized PDFs detected.")

else:
    st.markdown("""
    <div class="card" style="text-align:center; padding: 3rem 2rem; opacity:.7">
        <div style="font-size:3rem">🗺️</div>
        <div style="font-family:'Space Mono',monospace; font-size:.9rem; margin-top:.8rem">
            Upload PDFs above to begin sorting
        </div>
        <div style="font-size:.8rem; margin-top:.4rem; opacity:.6">
            Blueprints will be analysed, trimmed, sorted by roll width,<br>
            and combined into downloadable files.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; margin-top:3rem; font-family:'Space Mono',monospace;
     font-size:.15; opacity:.70; letter-spacing:.1em">
    העתקות הגולן - מג'דל שמס - קצרין 
</div>
""", unsafe_allow_html=True)
