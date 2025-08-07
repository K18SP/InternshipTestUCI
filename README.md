#  Multi-Part Python Project

This repository contains three Python-based data projects designed to demonstrate skills in Exploratory Data Analysis, LLM-based content generation, and document compliance checking.

---

##  Part 1: EDA on Retail Store Sales (Dirty)

###  Location: `Part1_EDA/eda_retail_sales.ipynb`

###  Dataset:
- **Source**: [Retail Store Sales (Dirty) - Kaggle](https://www.kaggle.com/datasets/competitions/retail-store-sales-forecasting)
- This dataset includes messy real-world retail store transaction data with missing values, inconsistent formatting, and hidden patterns.

###  Key Steps:
- **Data Cleaning**
  - Handled missing values, fixed column names, converted datatypes.
  - Normalized inconsistent formats (e.g., sales with commas).
- **Feature Engineering**
  - Extracted temporal features (year, month, day, weekend).
  - Created promotion flag, holiday indicators.
- **Visualizations**
  - Used `matplotlib` and `seaborn` for:
    - Daily/weekly/monthly sales trends.
    - Promotion vs non-promotion comparisons.
    - Store-type-wise performance.
- **Libraries Used**
  - `pandas` – data manipulation.
  - `matplotlib`, `seaborn` – effective and easy-to-use plotting.
  - `plotly` (optional) – interactive charts.

###  Output:
- Clear understanding of sales patterns, top stores, and issues like outliers or imbalanced data.

---

##  Part 2: Social Media Content Generator (LLM-Free)

###  Location: `Part2_SocialMedia/social_media_generator.py`

###  Objective:
- Generate **5 platform-specific social media posts** from a blog article.

###  Features:
- Input: `sample_blog.txt` or console input.
- Output: JSON file with posts for:
  - Twitter (concise, 280 char)
  - LinkedIn (professional)
  - Instagram (with emojis and hashtags)
  - Facebook (engaging style)
  - Reddit (casual + informative)
- No API required – uses a **template-based** or **LLM plug-in** architecture (compatible with GPT4All, LM Studio).

###  Design:
- `PlatformConfig` class to define post length/style.
- Modular post generation logic per platform.
- Optional integration with local LLM for enhanced phrasing.

---

##  Part 3: PDF Compliance Analyzer

###  Location: `Part3_PDFAnalyzer/pdf_analyzer.py`

###  Objective:
Automatically validate proposal documents in PDF format against formatting and content rules.

###  Functional Checks:
1. **File Format Validation**
   - Ensures uploaded file is a valid `.pdf`.

2. **Formatting Rules**
   - Font size must be **12 px**
   - Font family must be **Times New Roman**
   - Margin on all sides must be **1 inch**
   - Uses `pdfplumber` or `PyMuPDF` to check fonts and layout.

3. **Content Section Detection**
   - Required sections:
     - `Technical Requirements` → max **8 pages**
     - `Budget` → max **4 pages**
     - `Qualification` → max **4 pages**
   - Uses regex-based detection or fuzzy keyword matching.
   - Optionally integrates OCR (`pytesseract`) for scanned documents.

4. **Output Report**
   - Generates structured JSON summary:
     ```json
     {
       "format": {
         "file_type": "pass",
         "font_size": "fail",
         "font_family": "pass",
         "margin": "pass"
       },
       "content": {
         "technical_requirements_pages": 9,
         "technical_requirements": "fail",
         "budget_pages": 3,
         "budget": "pass",
         "qualification_pages": 4,
         "qualification": "pass"
       }
     }
     ```

###  (Optional)
- Streamlit-based minimal web UI for file upload + report view.
- Highlight violations in annotated PDFs.

---

##  How to Run

###  Install Requirements
```bash
pip install -r requirements.txt
```

###  Run Each Part

#### EDA
```bash
jupyter notebook Part1_EDA/eda_retail_sales.ipynb
```

#### Social Media Generator
```bash
cd Part2_SocialMedia
python social_media_generator.py --input sample_blog.txt
```

#### PDF Analyzer
```bash
cd Part3_PDFAnalyzer
python pdf_analyzer.py --file proposal.pdf
```

---

##  Requirements

```
pandas
numpy
matplotlib
seaborn
pdfplumber
PyMuPDF
pytesseract
opencv-python
python-docx


##  Folder Structure

```
project/
│
├── Part1_EDA/
│   └── eda_retail_sales.ipynb
│
├── Part2_SocialMedia/
│   ├── social_media_generator.py

├── Part3_PDFAnalyzer/
│   ├── pdf_analyzer.py

├── README.md
└── requirements.txt
```

---

##  Author

Developed by Kushal Pandya  
