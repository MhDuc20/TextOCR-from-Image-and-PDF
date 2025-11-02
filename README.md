Inmate Data Processing & Visualization Application
Desktop application for document OCR processing and inmate data management with AI-powered features.

Key Features
✅ Multi-format OCR – Single images, batch folders, multi-page PDFs
✅ AI Text Analysis – Vietnamese language support
✅ Statistics Extraction – Specialized for "THỐNG KÊ TÀI LIỆU" tables
✅ Auto PDF Splitting – Intelligent document classification
✅ Advanced Search – Search across all processed JSON data

System Requirements
RequirementVersionPython3.8+Tesseract OCRLatest (with Vietnamese pack)RAM4GB minimum (8GB recommended)OSWindows / macOS / Linux

Quick Setup (5 minutes)
Step 1: Install Tesseract OCR
Windows:
bash# Download: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR
# ✅ Check "Vietnamese" during installation
Linux:
bashsudo apt-get install tesseract-ocr tesseract-ocr-vie
macOS:
bashbrew install tesseract tesseract-lang
Step 2: Install Dependencies
bashpip install pillow pymupdf pytesseract requests
Step 3: Prepare Data Files
Place in project root:

cau_hoi_lien_quan.json
van_ban_den.json
van_ban_di.json

Step 4: Configure Paths
Edit app_gui.py:
pythonself.pdf_viewer_tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

Running the Application
bashpython app.py
```

**First run:** Loads data (~5-10s)  
**Next runs:** Quick startup (<3s)

---

## Interface When Running
```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║           INMATE DATA PROCESSING & VISUALIZATION APPLICATION                        ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

✓ Loading data files...
✓ Initializing Tesseract OCR...
✓ Configuring UI components...

Application ready!

Available Tabs:
  1. Available Questions    2. Enter Question
  3. AI Response           4. Data Processing & Viz

Started at: 11/03/2025 14:30:25
```

---

## Main Features

### 📸 Single Image OCR
1. **Data Processing & Viz** tab → **Browse Image**
2. Select image → Auto OCR
3. Results in `json_results/`

### 📊 Batch Processing (Statistics Tables)
1. Click **Process Document Stats Folder**
2. Select folder with images
3. Results in `thong_ke/`

### 📄 PDF OCR
1. **Open PDF** → Select file
2. **Extract Text (OCR)**
3. Results in:
   - `pdf_ocr_json_results/` – Full output
   - `pdf_split_json_results/` – Auto-split documents

**Progress Example:**
```
Processing page 3/15... ✓
Sending to AI for processing... ✓
✅ Completed! 15 pages processed
🔍 Search

Open Search Window
Enter keyword
View results (color-coded by match type)


Update Documents
Delete output folders and reprocess:
bashrm -rf json_results/ thong_ke/ pdf_ocr_json_results/

Usage Tips
PurposeSolutionFaster OCRReduce image quality, smaller batchesBetter accuracyHigher resolution images (300+ DPI)Change OCR APIEdit in GUI or app_gui.pyDebug issuesCheck console for detailed logs

Troubleshooting
❌ "Cannot load any data"
bash# Verify JSON files exist
ls -la *.json
❌ "Tesseract path does not exist"
bash# Check installation
tesseract --version
# Update path in app_gui.py
```

### ⚠️ Poor OCR quality
- Use 300+ DPI images
- Ensure good contrast
- Verify Vietnamese pack installed

### 🐌 Slow performance
- Close other apps
- Use SSD storage
- Upgrade to 8GB+ RAM

---

## Project Structure
```
project-root/
├── app.py                      # 🚀 Main entry
├── app_gui.py                  # 🎨 GUI logic
├── ocr.py                      # 📸 OCR module
├── pdf.py                      # 📄 PDF processing
├── handlers/                   # 🔧 Business logic
├── ui_tab_*.py                 # 🖼️ UI components
├── data_manager.py             # 💾 Data management
└── Output folders/             # 📁 Auto-generated
    ├── json_results/
    ├── thong_ke/
    └── pdf_ocr_json_results/

Important Notes
⚠️ Tesseract Required – For PDF OCR functionality
⚠️ API Optional – External OCR API not required
⚠️ Vietnamese Support – Install vie.traineddata
⚠️ Large PDFs – May take several minutes

Performance
TaskTimeRAMSingle image2-5s4GBBatch (20 images)1-2min4GBPDF (10 pages)3-5min8GB

Author
Contact: mduc11011@gmail.com
