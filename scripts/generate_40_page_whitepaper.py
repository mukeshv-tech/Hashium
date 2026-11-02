"""
Master 40-Page Academic Whitepaper PDF Generator for HCA-0.4.
Combines all 38 monograph sections with academic cover and table of contents.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

from scripts.paper.sections_1_10 import SECTIONS_PART_1
from scripts.paper.sections_11_20 import SECTIONS_PART_2
from scripts.paper.sections_21_30 import SECTIONS_PART_3
from scripts.paper.sections_31_38 import SECTIONS_PART_4

ALL_SECTIONS = SECTIONS_PART_1 + SECTIONS_PART_2 + SECTIONS_PART_3 + SECTIONS_PART_4
assert len(ALL_SECTIONS) == 38, f"Expected 38 monograph sections, got {len(ALL_SECTIONS)}"

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and stamp total page numbers and running headers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        if self._pageNumber == 1:
            # Suppress running header/footer on title cover page
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Running Header
        self.drawString(54, 755, "HCA-0.4 TECHNICAL WHITEPAPER: 1024-BIT WIDE-PIPE SPONGE")
        self.setFont("Helvetica", 8)
        self.drawRightString(558, 755, "NOVEMBER 2026")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(54, 747, 558, 747)

        # Running Footer
        self.line(54, 48, 558, 48)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(54, 36, "CONFIDENTIAL & EXPERIMENTAL RESEARCH DRAFT - HASHIUM PROJECT")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 36, page_str)
        self.restoreState()


def build_40_page_whitepaper(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom academic styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=colors.HexColor('#0F172A'),
        alignment=0,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=17,
        textColor=colors.HexColor('#334155'),
        alignment=0,
        spaceAfter=18
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#64748B'),
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'AcademicBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.6,
        leading=12.6,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6,
        alignment=4 # Justified
    )

    alert_style = ParagraphStyle(
        'AlertBox',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#991B1B'),
    )

    story = []

    # ==========================================
    # PAGE 1: TITLE & COVER
    # ==========================================
    story.append(Spacer(1, 35))
    story.append(Paragraph("THE HCA CRYPTOGRAPHIC PRIMITIVE &bull; TECHNICAL MONOGRAPH", ParagraphStyle('SuperTitle', fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=colors.HexColor('#2563EB'), spaceAfter=8)))
    story.append(Paragraph("Hashium Custom Algorithm (HCA-0.4): A 1024-Bit Wide-Pipe Sponge Construction with Multi-Core Tree Hashing and Permutation-Based Symmetrical Primitives", title_style))
    story.append(Paragraph("Comprehensive Architectural Specification, Algebraic Formulation, Cryptanalytic Boundaries, and Micro-Architectural SIMD Throughput Scaling", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0F172A'), spaceBefore=8, spaceAfter=18))

    meta_text = """
    <b>Author:</b> The Hashium Core Cryptographic Research Team<br/>
    <b>Project:</b> Hashium Open-Source Cryptography Library<br/>
    <b>Document Version:</b> 0.4.0-Production-Draft (Comprehensive 40-Page Monograph)<br/>
    <b>Target Platform:</b> x86_64 / AArch64 (Multi-Core AVX2/NEON Supported)<br/>
    <b>Distribution:</b> Public Research Draft (Experimental)<br/>
    <b>Date:</b> November 2026<br/>
    <b>Repository Reference:</b> <code>https://github.com/mukeshv-tech/Hashium</code>
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 20))

    warning_text = """
    <b>IMPORTANT CRYPTOGRAPHIC NOTICE & DISCLAIMER:</b><br/>
    HCA is an experimental custom wide-pipe sponge construction designed for academic research, high-throughput systems exploration, and comparative cryptanalysis. It has not undergone formal, multi-year third-party peer review or standardization by institutions such as NIST, IACR, or ISO/IEC. 
    It must <b>never</b> be deployed for security-critical environments, digital signatures, high-value asset storage, root certificate authority operations, or passwords.
    """
    alert_table = Table([[Paragraph(warning_text, alert_style)]], colWidths=[504])
    alert_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#DC2626')),
        ('TOPPADDING', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 9),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(alert_table)
    story.append(PageBreak())

    # ==========================================
    # PAGE 2: TABLE OF CONTENTS
    # ==========================================
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))

    toc_table_data = []
    # Two-column layout for 38 items
    left_items = ALL_SECTIONS[:19]
    right_items = ALL_SECTIONS[19:]

    for idx in range(19):
        t_left, _ = left_items[idx][0], left_items[idx][1]
        pg_left = str(idx + 3)
        t_right, _ = right_items[idx][0], right_items[idx][1]
        pg_right = str(idx + 22)

        toc_table_data.append([
            Paragraph(f"<b>{t_left}</b>", ParagraphStyle('TOCLineL', parent=styles['Normal'], fontName='Helvetica', fontSize=7.6, leading=9.6, textColor=colors.HexColor('#1E293B'))),
            Paragraph(f"<b>{pg_left}</b>", ParagraphStyle('TOCPgL', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.6, leading=9.6, alignment=2, textColor=colors.HexColor('#2563EB'))),
            Paragraph(f"<b>{t_right}</b>", ParagraphStyle('TOCLineR', parent=styles['Normal'], fontName='Helvetica', fontSize=7.6, leading=9.6, textColor=colors.HexColor('#1E293B'))),
            Paragraph(f"<b>{pg_right}</b>", ParagraphStyle('TOCPgR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.6, leading=9.6, alignment=2, textColor=colors.HexColor('#2563EB'))),
        ])

    t_toc = Table(toc_table_data, colWidths=[205, 25, 245, 25])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LINEBELOW', (0,0), (-1,-1), 0.3, colors.HexColor('#F1F5F9'))
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # ==========================================
    # PAGES 3 TO 40: THE 38 MONOGRAPH SECTIONS
    # ==========================================
    for title, subtitle, main_body, callout in ALL_SECTIONS:
        story.append(Paragraph(title, h1_style))
        story.append(Paragraph(subtitle, h2_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceBefore=2, spaceAfter=6))

        paragraphs = [p.strip() for p in main_body.strip().split("\n\n") if p.strip()]
        for p in paragraphs:
            story.append(Paragraph(p.replace("\n", " "), body_style))

        if callout:
            callout_paras = [
                Paragraph(
                    f"<b>{line.strip()}</b>" if line.strip().endswith(":") else line.strip(), 
                    ParagraphStyle('CalloutText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.0, leading=11, textColor=colors.HexColor('#1E3A8A'))
                ) 
                for line in callout.strip().split("\n") if line.strip()
            ]
            box_data = [[callout_paras]]
            box_table = Table(box_data, colWidths=[504])
            box_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#93C5FD')),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 9),
                ('RIGHTPADDING', (0,0), (-1,-1), 9),
            ]))
            story.append(Spacer(1, 3))
            story.append(box_table)

        story.append(PageBreak())

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"40-page whitepaper PDF successfully built at: {output_path}")

if __name__ == "__main__":
    out_path = os.path.abspath("docs/hca/HCA_Whitepaper.pdf")
    build_40_page_whitepaper(out_path)
