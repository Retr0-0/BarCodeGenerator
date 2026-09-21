import io
import os
import zipfile
import pandas as pd
import streamlit as st
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


st.set_page_config(page_title="Bulk Barcode Generator", layout="wide")
st.title("Bulk Barcode Generator")

# --- Hide Streamlit / GitHub Footer ---
hide_footer_style = """
    <style>
    /* Hides the bottom left profile / creator tag & footer */
    footer {visibility: hidden;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    #MainMenu {visibility: hidden;}
    </style>
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

# --- Initialize Session State Variables ---
if "zip_data" not in st.session_state:
    st.session_state.zip_data = None
if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None
if "preview_barcodes" not in st.session_state:
    st.session_state.preview_barcodes = []
if "file_base_name" not in st.session_state:
    st.session_state.file_base_name = "Barcodes"

# --- Step 1: File Upload ---
uploaded_file = st.sidebar.file_uploader(
    "Upload Excel or CSV file", 
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
    # Extract base filename without extension (e.g., "Amazon Product.csv" -> "Amazon Product")
    raw_filename = uploaded_file.name
    base_name = os.path.splitext(raw_filename)[0]

    try:
        if raw_filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.subheader("Data Preview")
    st.dataframe(df.head(5))

    # --- Step 2: Automatic Column Detection ---
    columns_list = list(df.columns)
    target_keywords = ["barcode", "sku", "upc", "ean", "id", "code", "item_number", "product_id"]
    
    default_index = 0
    for idx, col in enumerate(columns_list):
        col_clean = str(col).strip().lower().replace("_", "").replace(" ", "")
        if any(keyword in col_clean for keyword in target_keywords):
            default_index = idx
            break

    # --- Step 3: Sidebar Configuration ---
    st.sidebar.subheader("Barcode Settings")
    column_name = st.sidebar.selectbox(
        "Select column containing barcode data", 
        columns_list,
        index=default_index
    )
    
    barcode_type = st.sidebar.selectbox(
        "Barcode Format", 
        ["code128", "code39", "ean13", "qr"]
    )

    def generate_barcode_img(value, btype):
        val_str = str(value).strip()
        if btype == "qr":
            qr = qrcode.QRCode(box_size=10, border=2)
            qr.add_data(val_str)
            qr.make(fit=True)
            return qr.make_image(fill_color="black", back_color="white").convert("RGB")
        else:
            try:
                CODE = barcode.get_barcode_class(btype)
                rv = io.BytesIO()
                CODE(val_str, writer=ImageWriter()).write(rv)
                return Image.open(rv)
            except Exception:
                return Image.new("RGB", (300, 100), color=(255, 230, 230))

    # --- Step 4: Generation Trigger ---
    if st.sidebar.button("Generate Barcodes"):
        valid_rows = df[column_name].dropna().tolist()

        if not valid_rows:
            st.warning("The selected column has no data!")
            st.stop()

        progress_bar = st.progress(0)
        zip_buffer = io.BytesIO()
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        page_width, page_height = letter
        
        cols, rows = 3, 10
        margin_x, margin_y = 36, 36
        cell_w = (page_width - 2 * margin_x) / cols
        cell_h = (page_height - 2 * margin_y) / rows

        preview_list = []

        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for idx, raw_val in enumerate(valid_rows):
                val_str = str(raw_val).strip()
                img = generate_barcode_img(val_str, barcode_type)
                
                # Save PNG to ZIP
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                zip_file.writestr(f"barcode_{idx+1}_{val_str}.png", img_bytes.getvalue())

                # Add to PDF Grid
                col_idx = idx % cols
                row_idx = (idx // cols) % rows
                x = margin_x + col_idx * cell_w
                y = page_height - margin_y - (row_idx + 1) * cell_h

                img_reader = ImageReader(img)
                c.drawImage(img_reader, x + 5, y + 15, width=cell_w - 10, height=cell_h - 20, preserveAspectRatio=True)
                c.setFont("Helvetica", 8)
                c.drawCentredString(x + cell_w / 2, y + 5, val_str)

                if (idx + 1) % (cols * rows) == 0 and idx != len(valid_rows) - 1:
                    c.showPage()

                if idx < 12:
                    preview_list.append((val_str, img))

                progress_bar.progress((idx + 1) / len(valid_rows))

        c.save()

        # Store binary buffers and uploaded base filename into session_state
        st.session_state.zip_data = zip_buffer.getvalue()
        st.session_state.pdf_data = pdf_buffer.getvalue()
        st.session_state.preview_barcodes = preview_list
        st.session_state.row_count = len(valid_rows)
        st.session_state.file_base_name = base_name

    # --- Step 5: Display Downloads & Preview with Dynamic File Names ---
    if st.session_state.zip_data is not None:
        st.success(f"Successfully generated {st.session_state.row_count} barcodes!")
        
        # Build dynamic file names based on uploaded file
        zip_filename = f"{st.session_state.file_base_name} Barcode.zip"
        pdf_filename = f"{st.session_state.file_base_name} Barcode Labels.pdf"

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download All Barcodes (ZIP)",
                data=st.session_state.zip_data,
                file_name=zip_filename,
                mime="application/zip",
                key="dl_zip"
            )
        with col2:
            st.download_button(
                label="📄 Download Printable Label Sheet (PDF)",
                data=st.session_state.pdf_data,
                file_name=pdf_filename,
                mime="application/pdf",
                key="dl_pdf"
            )

        if st.session_state.preview_barcodes:
            st.subheader("Preview (First 12 Items)")
            preview_cols = st.columns(4)
            for i, (val, img) in enumerate(st.session_state.preview_barcodes):
                with preview_cols[i % 4]:
                    st.image(img, caption=f"Value: {val}", width="stretch")