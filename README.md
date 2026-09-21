# Bulk Barcode & QR Code Generator

A lightweight, web-based tool built with Streamlit and Python for generating bulk barcodes and printable PDF label sheets directly from uploaded CSV or Excel files.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=streamlit&logoColor=white)

---

## Features

* **Flexible File Upload:** Supports `.csv`, `.xlsx`, and `.xls` spreadsheets.
* **Smart Column Auto-Detection:** Scans headers for keywords (`barcode`, `sku`, `upc`, `ean`, `id`, `code`) and automatically selects the target data column.
* **Multiple Formats Supported:**
  * **Code 128:** Recommended for general alphanumeric SKUs and IDs.
  * **Code 39:** Standard 1D barcode format.
  * **EAN-13:** Standard 13-digit retail numbers.
  * **QR Code:** 2D high-density codes for long text, URLs, or hashes.
* **Bulk Downloads:**
  * **ZIP Archive:** Individual PNG image files for every generated barcode.
  * **Printable Label Sheet (PDF):** Auto-arranged 3x10 grid on standard Letter size, ready for sticker printing.
* **Dynamic File Naming:** Output ZIP and PDF files automatically inherit the name of your uploaded spreadsheet (e.g., `Amazon Product.csv` $\rightarrow$ `Amazon Product Barcode.zip`).
* **Session Persistence:** Generated files stay ready in memory for continuous downloads without re-processing.

---

## Installation

### 1. Clone or Download the Repository
```bash
git clone https://github.com/your-username/bulk-barcode-generator.git
cd bulk-barcode-generator
```

### 2. Install Dependencies
Make sure you have Python 3.9+ installed, then run:

```bash
pip install -r requirements.txt
```

---

## Quick Start

Launch the application locally with Streamlit:

```bash
streamlit run app.py
```

Your default browser will automatically open at `http://localhost:8501`.

---

## How to Use

1. **Upload Spreadsheet:** Upload your `.csv` or `.xlsx` file using the sidebar.
2. **Select Column:** Confirm or adjust the auto-detected target column containing your identifiers.
3. **Choose Barcode Format:** Select between `code128`, `code39`, `ean13`, or `qr`.
4. **Generate:** Click **Generate Barcodes**.
5. **Download:** Click to download individual PNGs as a **ZIP file** or a complete multi-page **Printable PDF Sheet**.

---

## Project Structure

```text
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

---

## Requirements (`requirements.txt`)

* `streamlit`
* `pandas`
* `openpyxl`
* `python-barcode`
* `qrcode[pil]`
* `pillow`
* `reportlab`