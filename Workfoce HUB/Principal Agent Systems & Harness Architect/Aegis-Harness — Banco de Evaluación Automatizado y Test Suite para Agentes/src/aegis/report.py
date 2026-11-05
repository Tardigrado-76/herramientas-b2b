"""
Report Generator for Aegis-Harness.
Emits comprehensive Markdown summaries and NIS2-compliant PDF certificates via ReportLab.
"""

from pathlib import Path
from typing import Optional, List
from aegis.models import SuiteSummary, TestResult

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 802, "🛡️ AEGIS-HARNESS — Certificado de Evaluación & Quality Gate")
            self.drawRightString(559, 802, "NIS2 Art. 21 · EU AI Act Art. 12/15 Compliant")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 796, 559, 796)
        
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 38, 559, 38)
        
        self.drawString(36, 26, "Aegis-Harness Audit Ledger — Cero Docker / Host Nativo")
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(559, 26, page_text)
        self.restoreState()


class ReportGenerator:
    """Generates Markdown and PDF reports from evaluation suite summaries."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown(self, summary: SuiteSummary, filename: Optional[str] = None) -> Path:
        fname = filename or f"{summary.suite_name.lower().replace(' ', '_')}_report.md"
        out_path = self.output_dir / fname

        lines = [
            f"# 🛡️ Aegis-Harness Evaluation Report: {summary.suite_name}",
            f"> **Generated UTC:** {summary.timestamp}  ",
            f"> **Quality Gate:** {'✅ PASSED (Production Ready)' if summary.quality_gate_passed else '❌ FAILED (Deployment Blocked)'}",
            "",
            "## 1. Executive Summary",
            "",
            "| Metric | Value |",
            "|:---|:---|",
            f"| **Total Tests** | `{summary.total_tests}` |",
            f"| **Passed Tests** | `{summary.passed_tests}` |",
            f"| **Failed Tests** | `{summary.failed_tests}` |",
            f"| **Pass Rate** | `{summary.pass_rate_percent:.1f}%` |",
            f"| **Overall Score** | `{summary.overall_score:.1f} / 100` |",
            f"| **Average Latency** | `{summary.average_latency_ms:.1f} ms` |",
            "",
            "## 2. Category Performance",
            "",
            "| Category | Score |",
            "|:---|:---|",
        ]

        for cat, score in summary.category_scores.items():
            lines.append(f"| **{cat.capitalize()}** | `{score:.1f} / 100` |")

        lines.extend([
            "",
            "## 3. Detailed Results",
            "",
            "| ID | Category | Score | Status | Details |",
            "|:---|:---|:---|:---:|:---|",
        ])

        for r in summary.results:
            status = "✅ PASS" if r.passed else "❌ FAIL"
            details = r.failure_reason if not r.passed else "All criteria satisfied"
            lines.append(f"| `{r.test_case_id}` | `{r.category.value}` | `{r.overall_score:.1f}` | {status} | {details} |")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return out_path

    def generate_pdf(self, summary: SuiteSummary, filename: Optional[str] = None) -> Path:
        fname = filename or f"{summary.suite_name.lower().replace(' ', '_')}_report.pdf"
        out_path = self.output_dir / fname

        doc = SimpleDocTemplate(
            str(out_path),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=46,
            bottomMargin=46
        )

        styles = getSampleStyleSheet()
        PRIMARY = colors.HexColor("#0F172A")
        ACCENT = colors.HexColor("#0284C7")
        BORDER_LIGHT = colors.HexColor("#E2E8F0")
        BG_CARD = colors.HexColor("#F8FAFC")

        title_style = ParagraphStyle(
            'DocTitle',
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=PRIMARY,
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=12
        )
        h1_style = ParagraphStyle(
            'H1',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=PRIMARY,
            spaceBefore=10,
            spaceAfter=5
        )
        body_style = ParagraphStyle(
            'Body',
            fontName='Helvetica',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155")
        )
        th_style = ParagraphStyle(
            'TH',
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.white
        )

        story = []

        # Title
        story.append(Paragraph("🛡️ AEGIS-HARNESS AUDIT CERTIFICATE", title_style))
        story.append(Paragraph(f"<b>Suite:</b> {summary.suite_name} · <b>Evaluated UTC:</b> {summary.timestamp}", subtitle_style))

        # Metrics Card Table
        gate_text = "<b>✅ QUALITY GATE PASSED (READY FOR DEPLOYMENT)</b>" if summary.quality_gate_passed else "<b>❌ QUALITY GATE FAILED (DEPLOYMENT BLOCKED)</b>"
        gate_bg = colors.HexColor("#F0FDF4") if summary.quality_gate_passed else colors.HexColor("#FEF2F2")
        gate_border = colors.HexColor("#86EFAC") if summary.quality_gate_passed else colors.HexColor("#FCA5A5")

        gate_card = Table([[Paragraph(gate_text, body_style)]], colWidths=[523])
        gate_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), gate_bg),
            ('BOX', (0,0), (-1,-1), 1, gate_border),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(gate_card)
        story.append(Spacer(1, 10))

        # Executive Metrics Table
        summary_rows = [
            [
                Paragraph("<b>Métrica</b>", th_style),
                Paragraph("<b>Resultado</b>", th_style),
                Paragraph("<b>Métrica</b>", th_style),
                Paragraph("<b>Resultado</b>", th_style)
            ],
            [
                Paragraph("Total Casos de Prueba:", body_style),
                Paragraph(f"<b>{summary.total_tests}</b>", body_style),
                Paragraph("Tasa de Aprobación:", body_style),
                Paragraph(f"<b>{summary.pass_rate_percent:.1f}%</b>", body_style)
            ],
            [
                Paragraph("Casos Aprobados:", body_style),
                Paragraph(f"<b>{summary.passed_tests}</b>", body_style),
                Paragraph("Puntuación Global:", body_style),
                Paragraph(f"<b>{summary.overall_score:.1f} / 100</b>", body_style)
            ],
            [
                Paragraph("Casos Fallidos:", body_style),
                Paragraph(f"<b>{summary.failed_tests}</b>", body_style),
                Paragraph("Latencia Media:", body_style),
                Paragraph(f"<b>{summary.average_latency_ms:.1f} ms</b>", body_style)
            ]
        ]
        sum_table = Table(summary_rows, colWidths=[130, 131, 130, 132])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PRIMARY),
            ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 10))

        # Category Breakdown
        story.append(Paragraph("Rendimiento por Categoría", h1_style))
        cat_rows = [
            [
                Paragraph("<b>Categoría Evaluada</b>", th_style),
                Paragraph("<b>Puntuación Media</b>", th_style),
                Paragraph("<b>Estado de Conformidad</b>", th_style)
            ]
        ]
        for cat, score in summary.category_scores.items():
            status = "CONFORME (Score >= 85)" if score >= 85.0 else "NO CONFORME"
            cat_rows.append([
                Paragraph(f"<b>{cat.capitalize()}</b>", body_style),
                Paragraph(f"{score:.1f} / 100", body_style),
                Paragraph(status, body_style)
            ])
        cat_table = Table(cat_rows, colWidths=[200, 150, 173])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), ACCENT),
            ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ]))
        story.append(cat_table)

        doc.build(story, canvasmaker=NumberedCanvas)
        return out_path
