from pathlib import Path
import fitz  
import pdfplumber
import json
import re
from collections import defaultdict
from PyPDF2 import PdfReader


def is_valid_pdf(file_path):
    """Check if the provided file is a valid PDF."""
    try:
        PdfReader(file_path)
        return True
    except:
        return False


def check_formatting(pdf_path):
    """Check font size, font family, and margins on the first page of the PDF."""
    result = {
        "font_size": "pass",
        "font_family": "pass",
        "margin": "pass"
    }
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            fonts = set()
            sizes = set()

            for char in page.chars:
                fonts.add(char.get('fontname', ''))
                sizes.add(round(float(char.get('size', 0)), 1))

            if 12.0 not in sizes:
                result['font_size'] = 'fail'
            if not any("Times" in f or "TimesNewRoman" in f for f in fonts):
                result['font_family'] = 'fail'

            width = page.width
            height = page.height
            content = page.bbox

            left = content[0]
            right = width - content[2]
            top = height - content[3]
            bottom = content[1]

            one_inch = 72  
            tolerance = 5  

            if not all(abs(m - one_inch) <= tolerance for m in [left, right, top, bottom]):
                result['margin'] = 'fail'

    except:
        result = {k: 'fail' for k in result}
    return result


def detect_sections_dynamic(pdf_path, max_page_limits=None):
    """Detect section names dynamically and count how many pages each spans."""
    doc = fitz.open(pdf_path)
    section_starts = {}
    section_pages = defaultdict(list)

    for i, page in enumerate(doc):
        text = page.get_text("text")
        lines = text.split("\n")

        for line in lines:
            line_clean = line.strip().lower()
            if re.match(r"^[A-Z][A-Za-z\s\-]+:$", line.strip()) or line.isupper():
                section_name = re.sub(r"[^a-z ]", "", line_clean).strip()
                if section_name and section_name not in section_starts:
                    section_starts[section_name] = i
                    section_pages[section_name].append(i)
            elif section_starts:
                last_section = list(section_starts.keys())[-1]
                section_pages[last_section].append(i)

    for k in section_pages:
        section_pages[k] = sorted(set(section_pages[k]))

    result = {}
    for sec, pages in section_pages.items():
        page_key = f"{sec.replace(' ', '_')}_pages"
        status_key = sec.replace(' ', '_')

        result[page_key] = len(pages)

        if max_page_limits and sec in max_page_limits:
            result[status_key] = "pass" if len(pages) <= max_page_limits[sec] else "fail"
        else:
            result[status_key] = "n/a"  

    return result


def analyze_pdf(pdf_path, max_page_limits=None):
    """Run full analysis: format + content section validation."""
    report = {
        "format": {},
        "content": {}
    }

    if not is_valid_pdf(pdf_path):
        report["format"]["file_type"] = "fail"
        return report

    report["format"]["file_type"] = "pass"
    report["format"].update(check_formatting(pdf_path))
    report["content"].update(detect_sections_dynamic(pdf_path, max_page_limits))
    return report
