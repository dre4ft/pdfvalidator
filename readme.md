# 🛡️ PDF Validator - Advanced PDF Security Pipeline

A complete security solution for PDF files combining **YARA detection**, **PDF/A conversion**, and **secure deletion**, with a modern web interface.

## 🎯 Overview

**PDF Validator** is a Python pipeline that automatically analyzes PDF files to:
- Detect **malicious or suspicious content** using YARA rules
- Neutralize active content by converting to **PDF/A-2b**
- Apply **recursive logic** for suspicious files
- Perform **secure deletion** (multi-pass + encryption) of dangerous files
- Provide **complete traceability** via logs and web interface

---

## 🏗️ Architecture

### Main Components

| Component | Role |
|-----------|------|
| **web_server.py** | FastAPI server exposing web interface and APIs |
| **api.py** | FastAPI endpoints for analysis, upload and YARA rules management |
| **pdf_validator.py** | Main pipeline processing engine |
| **yara_detection.py** | Loading, compilation and execution of YARA rules |
| **ghostscript.py** | PDF → PDF/A-2 conversion (neutralization) |
| **shredder.py** | Secure deletion with multi-pass + AES-256 encryption |
| **static/** | Web interface (HTML/CSS/JS) |

### Processing Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1️⃣  Upload PDF                                             │
└────────────────┬────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────────┐
│  2️⃣  YARA Analysis → Score + Verdict                       │
│      • Score < 40  = Benign ✅                              │
│      • 40 ≤ Score < 70 = Suspect ⚠️                         │
│      • Score ≥ 70  = Malicious ❌                           │
└────┬──────────────┬──────────────────────────┬──────────────┘
     │              │                          │
     ↓ Benign ✅    ↓ Suspect ⚠️               ↓ Malicious ❌
     │              │                          │
 ┌───────────┐  ┌──────────────┐         ┌──────────────┐
 │ Conversion│  │ Conversion   │         │ Secure       │
 │ PDF/A     │  │ PDF/A        │         │ Deletion     │
 │ + Delete  │  │ + Reanalysis │         │ (10 passes)  │
 │ Original  │  │ Recursive    │         │ + AES-256    │
 └───────────┘  └──────────────┘         └──────────────┘
     ↓              ↓                          ↓
     └──────────┬───┴──────────┬──────────────┘
                ↓
         📋 Timestamped logs
         📁 Quarantined files
         🔍 Web interface
```

---

## 📋 Detailed Processing Logic

### Verdict by YARA Score Threshold
- **Score < 40** : Benign PDF
  - ✅ PDF/A conversion (removal of active content)
  - ✅ Original PDF deletion
  - ✅ PDF/A archival

- **Score 40-69** : Suspicious PDF
  - ⚠️ PDF/A conversion
  - ⚠️ Original PDF deletion
  - ⚠️ **Recursive reanalysis** of converted PDF/A
  - 🛡️ Anti-loop protection: stop after 3 conversions

- **Score ≥ 70** : Malicious PDF
  - 🚫 Immediate and secure deletion
  - 🔒 Multi-pass overwrite (10 passes)
  - 🔐 AES-256 encryption
  - ❌ Complete destruction

### Anti-loop Protection
Converted files receive the suffix `_pdfa.pdf`. If this suffix appears **more than 2 times** in the filename, the file is moved to quarantine (folder `suspect_files/`) to prevent infinite loops.

---

## 🚀 Installation and Setup

### Prerequisites
- **Python 3.8+**
- **Ghostscript** (for PDF/A conversion)
  ```bash
  # macOS
  brew install ghostscript
  
  # Linux
  sudo apt-get install ghostscript
  
  # Windows
  # Download from https://www.ghostscript.com/download/gsdnld.html
  ```

### Installation

1. **Clone/access the project**
   ```bash
   git clone https://github.com/dre4ft/pdfvalidator.git
   cd pdfvalidator
   ```

2. **Create virtual environment (optional but recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Startup

```bash
python3 web_server.py
```

The application will be accessible at: **http://127.0.0.1:8000**

---

## 📦 Dependencies

| Package | Role |
|---------|------|
| `fastapi` | Modern web framework |
| `uvicorn` | ASGI server for FastAPI |
| `yara-python` | Threat detection via YARA rules |
| `pypdf` | PDF file manipulation |
| `fpdf2` | PDF generation |
| `cryptography` | AES-256 encryption |
| `python-multipart` | Multipart form parsing |

---

## 🌐 REST API

### POST `/api/scan/remote`
Analyzes and processes one or more PDF files

**Parameters:**
- `files` : PDF files (multipart/form-data)

**Response:**
```json
{
  "mode": "remote",
  "received_paths": ["document.pdf"],
  "status": {
    "document.pdf": "Benign file, PDF/A conversion completed."
  }
}
```

### GET `/api/yara/rules`
Retrieves current YARA rules

**Response:**
```json
{
  "rules": "rule example { ... }"
}
```

### POST `/api/yara/update`
Adds new YARA rules

**Parameters:**
- `body` : New rules (text/plain)

**Response:**
```json
{
  "status": "YARA rules updated successfully."
}
```

---

## 📁 Directory Structure

```
.
├── api.py                          # FastAPI endpoints
├── web_server.py                   # Main server
├── pdf_validator.py                # Processing pipeline
├── yara_detection.py               # YARA engine
├── ghostscript.py                  # PDF/A conversion
├── shredder.py                     # Secure deletion
├── requirements.txt                # Python dependencies
│
├── static/                         # Web interface
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── yara_rules/                     # Detection rules
│   ├── pdf.yara
│   ├── pdf2.yara
│   └── pdf.yara.old
│
├── to_analyze/                     # PDFs waiting for analysis
├── benign/                         # Benign PDFs archival (converted)
├── suspect_files/                  # Quarantined PDFs (anti-loop)
├── malicious/                      # Malicious PDFs (deleted)
├── suspicious_pdfs/                # Detailed logs
│
├── test/                           # Test suite
│   ├── main.py
│   ├── runner.py
│   ├── caster.py
│   ├── clean_result.py
│   ├── kpi.py
│   └── gen_mal_pdf/                # Malicious PDF generator
│
└── pipeline.log                    # Timestamped journal
```

---

## 🎮 Web Interface

### "Scan PDF" Tab
- **Drop zone** : Drag & drop or click to select PDFs
- **Real-time logs** : Track processing (verdict, conversion, deletion)
- **Result consultation** : Complete processing history

### "YARA Rules" Tab
- **Visualization** : Displays all currently active rules
- **Rule addition** : Add new detection rules
- **Live updates** : Changes are applied immediately

---

## 🔍 Usage Examples

### Via web interface
1. Access http://127.0.0.1:8000
2. Go to "Scan PDF" tab
3. Click on the drop zone or perform a drag & drop
4. Select your PDF files
5. Check logs to follow processing

### Via API (curl)
```bash
curl -X POST "http://127.0.0.1:8000/api/scan/remote" \
  -F "files=@document.pdf"
```

### Via Python
```bash
python3 pdf_validator.py path/to/file.pdf
```

---

## 📊 Log Files

**pipeline.log** : Detailed processing timestamps
```
2026-01-24 14:32:15 - /Users/romain_travail/pdfvalidator/to_analyze/doc.pdf : [+] Benign file, PDF/A conversion completed.
2026-01-24 14:32:18 - /Users/romain_travail/pdfvalidator/to_analyze/suspect.pdf : [*] Suspect file, PDF/A conversion completed additional analysis in progress...
```

**Quarantine files** : Stored in `suspect_files/` (anti-loop protection)

---

## ⚠️ Limitations and Warnings

- **Depends on YARA rules** : Result quality directly depends on configured rules
- **False positives/negatives** : YARA rules can generate incorrect detections
- **Ghostscript required** : PDF/A conversion requires local Ghostscript installation
- **Content loss** : PDF/A conversion may lose complex content (scripts, advanced forms)

---

## 🛠️ Troubleshooting

### Error: "Ghostscript not found"
- Verify Ghostscript installation: `gs --version`
- Ensure `gs` is in the PATH

### Error: "YARA rules not found"
- Verify `yara_rules/` folder contains `pdf.yara`
- Check YARA rules syntax

### Files are not being analyzed
- Verify "Scan PDF" tab is active in the interface
- Check browser console (F12) for JavaScript errors
- Check Python logs in terminal

---

## 📝 Developer Notes

- The pipeline applies **recursive logic** for suspicious files
- **Anti-loop protection** prevents infinite conversions
- **Secure deletion** uses 10 passes of filling + AES-256 encryption
- **Logs** are fully timestamped for traceability
- Web interface uses **Fetch API** for asynchronous calls

---

## 📄 License

To be defined according to your needs.

---

## 👤 Author

Advanced PDF security project.
