# 📄 PDF Compliance Analyzer

This tool validates uploaded PDF files against formatting and content structure rules. It is ideal for organizations receiving documents like proposals, resumes, or reports that must comply with strict submission guidelines.

---

## 🚀 Features

-  Validates if the file is a real PDF
-  Checks:
  - Font size = **12 pt**
  - Font family = **Times New Roman**
  - **1-inch** margins (top, bottom, left, right)
-  Dynamically detects sections based on heading patterns
-  Counts how many pages each section spans
-  (Optional) Validates sections against page limits
-  Streamlit interface for easy upload and report download

---

##  Tool Usage Instructions

###  Requirements

Install dependencies:

```
pip install -r requirements.txt
```

###  Running via Script (Local)

You can call the analyzer directly:

```python
from pdf_checker import analyze_pdf

pdf_path = "your_pdf_file.pdf"
limits = {
    "skills": 2,
    "qualifications_and_education_requirements": 2
}
result = analyze_pdf(pdf_path, max_page_limits=limits)
print(result)
```

---

###  Running via Streamlit (Web Interface)

Create a file `app.py` with the Streamlit interface.  
Then run:

```
streamlit run app.py
```

Features of the UI:
- Upload a `.pdf` file
- Optionally paste section page limits as JSON:
  ```json
  {
    "skills": 2,
    "budget": 4
  }
  ```
- View a formatted report
- Download the analysis as a `.json` file

---

## 📁 Folder Structure

```
PDF_Analyzer/
├── app.py                  # Streamlit app
├── pdf_checker.py          # Core logic
├── requirements.txt        # Python dependencies
├── sample.pdf              # Sample PDF (optional)
└── README.md               # This file
```

---

##  Assumptions Made

- **Section Detection**:
  - Headings are detected using text heuristics:
    - All-uppercase lines
    - Lines ending with a colon (`:`)
    - Capitalized titles
  - If no clear section format exists, detection may be limited.

- **Formatting**:
  - Only the **first page** is used to validate font size, font family, and margin.
  - PDF must have extractable text (non-scanned image PDFs will fail unless OCR is added).

- **Page Limits**:
  - Validation against section page limits is optional.
  - If no limits are provided, `"n/a"` is used in the report.

- **Font Check**:
  - Relies on PDF metadata from `pdfplumber`.
  - Font names are matched loosely to include “Times” or “TimesNewRoman”.

---

##  Sample Output

```json
{
  "format": {
    "file_type": "pass",
    "font_size": "pass",
    "font_family": "fail",
    "margin": "fail"
  },
  "content": {
    "skills_pages": 3,
    "skills": "fail",
    "qualifications_and_education_requirements_pages": 2,
    "qualifications_and_education_requirements": "pass"
  }
}
```