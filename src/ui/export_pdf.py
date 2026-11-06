"""
PDF report generation utility using fpdf2.
Formats the multi-agent investment dossier into a publication-ready downloadable PDF.
"""

import io
from typing import Optional
from fpdf import FPDF


class DossierPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, "MarketMind AI - Autonomous Investment Dossier", border=False, align="L")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(127, 140, 141)
        self.cell(0, 10, f"Page {self.page_no()} | Confidential AI Intelligence Briefing", align="C")


def generate_dossier_pdf(report_text: str, ticker: str) -> bytes:
    """
    Converts Markdown-formatted agent research dossier into PDF bytes.
    """
    pdf = DossierPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    # Document Header Badge
    pdf.set_fill_color(240, 242, 246)
    pdf.set_text_color(41, 128, 185)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, f"Target Symbol: {ticker.upper()}", fill=True, ln=True, align="L")
    pdf.ln(5)

    # Parse and write report lines safely
    pdf.set_text_color(44, 62, 80)
    lines = report_text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(3)
            continue

        # Handle Markdown Headings
        if stripped.startswith("# "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(41, 128, 185)
            # Remove symbols/hashtags
            clean_title = stripped.replace("#", "").strip()
            # Encode/decode to handle non-latin1 characters gracefully
            safe_title = clean_title.encode("latin-1", "replace").decode("latin-1")
            pdf.cell(0, 9, safe_title, ln=True)
            pdf.set_text_color(44, 62, 80)
            pdf.set_font("Helvetica", size=10)
        elif stripped.startswith("## "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(52, 73, 94)
            clean_title = stripped.replace("##", "").strip()
            safe_title = clean_title.encode("latin-1", "replace").decode("latin-1")
            pdf.cell(0, 8, safe_title, ln=True)
            pdf.set_text_color(44, 62, 80)
            pdf.set_font("Helvetica", size=10)
        elif stripped.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            clean_title = stripped.replace("###", "").strip()
            safe_title = clean_title.encode("latin-1", "replace").decode("latin-1")
            pdf.cell(0, 7, safe_title, ln=True)
            pdf.set_font("Helvetica", size=10)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            safe_bullet = stripped.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 6, f"  • {safe_bullet[2:]}")
        else:
            safe_text = stripped.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 6, safe_text)

    # Convert to bytes
    pdf_output = pdf.output()
    return bytes(pdf_output)

