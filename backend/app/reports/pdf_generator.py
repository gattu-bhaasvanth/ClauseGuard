import io
from typing import List, Dict, Any
import fitz

from app.schemas.report import TransactionAuditReportSchema


class AuditReportPDFGenerator:
    """
    Renders professional multi-page vector-quality PDF audit reports using PyMuPDF.
    """

    PAGE_WIDTH = 595
    PAGE_HEIGHT = 842

    DARK_NAVY = (0.08, 0.09, 0.12)
    EMERALD = (0.06, 0.6, 0.38)
    AMBER = (0.85, 0.55, 0.1)
    ROSE = (0.85, 0.2, 0.25)
    LIGHT_GRAY = (0.94, 0.95, 0.96)
    TEXT_DARK = (0.15, 0.15, 0.18)
    TEXT_MUTED = (0.45, 0.45, 0.5)

    def generate_pdf(self, report: TransactionAuditReportSchema) -> bytes:
        doc = fitz.open()

        # ================= PAGE 1 =================
        page1 = doc.new_page(width=self.PAGE_WIDTH, height=self.PAGE_HEIGHT)
        self._draw_header(page1, report)
        y = 110

        # Executive Summary Box
        y = self._draw_section_title(page1, "1. Executive Summary & Property Profile", y)
        y = self._draw_paragraph(page1, report.executiveSummary.transactionProfile, y, fontsize=9.5)
        y += 6
        y = self._draw_paragraph(page1, report.executiveSummary.keyFindingsNarrative, y, fontsize=9)
        y += 6
        y = self._draw_paragraph(page1, report.executiveSummary.criticalRisksNarrative, y, fontsize=9)
        y += 12

        # Recommended Actions
        y = self._draw_section_title(page1, "2. Key Recommended Actions Before Signing", y)
        for act in report.executiveSummary.recommendedActions[:4]:
            page1.draw_circle(fitz.Point(45, y + 4), 2.5, color=self.EMERALD, fill=self.EMERALD)
            y = self._draw_paragraph(page1, act, y, left_margin=55, fontsize=8.5)
            y += 4
        y += 12

        # Document Checklist Table
        y = self._draw_section_title(page1, "3. Statutory Document Completeness Audit", y)
        y = self._draw_checklist_table(page1, report.documentChecklist, y)

        self._draw_footer(page1, 1, 2)

        # ================= PAGE 2 =================
        page2 = doc.new_page(width=self.PAGE_WIDTH, height=self.PAGE_HEIGHT)
        self._draw_header_compact(page2, report)
        y2 = 70

        # Cross-Document Inconsistencies
        y2 = self._draw_section_title(page2, "4. Cross-Document Discrepancy Evidence", y2)
        if report.inconsistencies:
            for inc in report.inconsistencies[:3]:
                y2 = self._draw_inconsistency_card(page2, inc, y2)
                y2 += 8
        else:
            y2 = self._draw_paragraph(page2, "No cross-document inconsistencies detected.", y2, fontsize=9)
            y2 += 10

        # High-Risk Clauses
        y2 = self._draw_section_title(page2, "5. Contractual Risk & Asymmetry Breakdown", y2)
        if report.risks:
            for r in report.risks[:3]:
                y2 = self._draw_risk_card(page2, r, y2)
                y2 += 6
        else:
            y2 = self._draw_paragraph(page2, "No high-risk clauses identified.", y2, fontsize=9)
            y2 += 10

        # Category Risk Index Bar
        y2 = self._draw_section_title(page2, "6. Risk Indices by Category", y2)
        y2 = self._draw_risk_indices(page2, report.categoryRiskScores, y2)

        self._draw_footer(page2, 2, 2)

        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def _draw_header(self, page: fitz.Page, report: TransactionAuditReportSchema):
        # Header Dark Box
        page.draw_rect(fitz.Rect(0, 0, self.PAGE_WIDTH, 80), color=None, fill=self.DARK_NAVY)
        page.insert_text((35, 30), "ClauseGuard", fontsize=15, color=(1, 1, 1), fontname="hebo")
        page.insert_text((135, 30), "|  Transaction Intelligence & Audit Report", fontsize=11, color=(0.7, 0.7, 0.75), fontname="helv")
        
        sub = f"Project: {report.projectTitle}  •  Unit: {report.unit}  •  Developer: {report.developer}"
        page.insert_text((35, 52), sub, fontsize=9, color=(0.85, 0.85, 0.9), fontname="helv")

        date_str = f"Date: {report.generatedAt[:10]}  •  ID: {report.reportId}"
        page.insert_text((35, 68), date_str, fontsize=8, color=(0.6, 0.6, 0.65), fontname="helv")

        # Health score pill
        score_color = self.EMERALD if report.healthScore >= 80 else (self.AMBER if report.healthScore >= 65 else self.ROSE)
        page.draw_rect(fitz.Rect(460, 20, 560, 60), color=score_color, fill=score_color, width=1)
        page.insert_text((475, 40), f"SCORE {report.healthScore}/100", fontsize=10, color=(1, 1, 1), fontname="hebo")
        page.insert_text((475, 52), report.status.replace("_", " "), fontsize=7.5, color=(1, 1, 1), fontname="helv")

    def _draw_header_compact(self, page: fitz.Page, report: TransactionAuditReportSchema):
        page.draw_rect(fitz.Rect(0, 0, self.PAGE_WIDTH, 45), color=None, fill=self.DARK_NAVY)
        page.insert_text((35, 25), f"ClauseGuard Audit Report  —  {report.projectTitle} ({report.unit})", fontsize=10, color=(1, 1, 1), fontname="hebo")
        score_color = self.EMERALD if report.healthScore >= 80 else (self.AMBER if report.healthScore >= 65 else self.ROSE)
        page.insert_text((480, 25), f"Score: {report.healthScore}/100", fontsize=9, color=score_color, fontname="hebo")

    def _draw_section_title(self, page: fitz.Page, title: str, y: float) -> float:
        page.insert_text((35, y), title, fontsize=11, color=self.DARK_NAVY, fontname="hebo")
        page.draw_line(fitz.Point(35, y + 4), fitz.Point(560, y + 4), color=(0.85, 0.85, 0.88), width=0.8)
        return y + 16

    def _draw_paragraph(
        self, page: fitz.Page, text: str, y: float, left_margin: float = 35, width: float = 525, fontsize: float = 9
    ) -> float:
        rect = fitz.Rect(left_margin, y, left_margin + width, y + 150)
        rc = page.insert_textbox(rect, text, fontsize=fontsize, fontname="helv", color=self.TEXT_DARK)
        # Approximate advance based on lines of text
        est_lines = max(1, len(text) // 95 + 1)
        return y + est_lines * (fontsize * 1.35)

    def _draw_checklist_table(
        self, page: fitz.Page, checklist: List[Any], y: float
    ) -> float:
        # Table Header
        page.draw_rect(fitz.Rect(35, y, 560, y + 16), color=None, fill=self.LIGHT_GRAY)
        page.insert_text((40, y + 12), "Document Type", fontsize=8, color=self.TEXT_MUTED, fontname="hebo")
        page.insert_text((240, y + 12), "Importance", fontsize=8, color=self.TEXT_MUTED, fontname="hebo")
        page.insert_text((340, y + 12), "Status", fontsize=8, color=self.TEXT_MUTED, fontname="hebo")
        page.insert_text((420, y + 12), "File Citation", fontsize=8, color=self.TEXT_MUTED, fontname="hebo")
        y += 18

        for item in checklist[:6]:
            status_color = self.EMERALD if item.status == "PRESENT" else (self.ROSE if item.importance in ("MANDATORY", "REQUIRED") else self.AMBER)
            page.insert_text((40, y + 10), item.displayName[:35], fontsize=8, color=self.TEXT_DARK, fontname="helv")
            page.insert_text((240, y + 10), item.importance, fontsize=7.5, color=self.TEXT_MUTED, fontname="helv")
            page.insert_text((340, y + 10), item.status, fontsize=8, color=status_color, fontname="hebo")
            f_name = (item.fileName or "Not uploaded")[:26]
            page.insert_text((420, y + 10), f_name, fontsize=7.5, color=self.TEXT_MUTED, fontname="helv")
            y += 14

        return y

    def _draw_inconsistency_card(self, page: fitz.Page, inc: Any, y: float) -> float:
        # Outer Card Box
        page.draw_rect(fitz.Rect(35, y, 560, y + 70), color=(0.8, 0.82, 0.85), fill=self.LIGHT_GRAY, width=0.6)
        
        # Title & Category Tag
        page.insert_text((45, y + 15), inc.title, fontsize=9.5, color=self.DARK_NAVY, fontname="hebo")
        page.insert_text((420, y + 15), f"[{inc.category} • {inc.severity}]", fontsize=8, color=self.ROSE, fontname="hebo")

        # Excerpts comparison
        p_doc = inc.primaryEvidence.documentName
        p_txt = inc.primaryEvidence.excerpt[:110]
        s_doc = inc.secondaryEvidence.documentName
        s_txt = inc.secondaryEvidence.excerpt[:110]

        page.insert_text((45, y + 32), f"Primary ({p_doc}, P.{inc.primaryEvidence.pageNumber}): \"{p_txt}...\"", fontsize=7.5, color=self.TEXT_DARK, fontname="helv")
        page.insert_text((45, y + 46), f"Contradicting ({s_doc}, P.{inc.secondaryEvidence.pageNumber}): \"{s_txt}...\"", fontsize=7.5, color=self.ROSE, fontname="helv")
        page.insert_text((45, y + 60), f"Impact: {inc.description[:110]}...", fontsize=7.5, color=self.TEXT_MUTED, fontname="helv")

        return y + 75

    def _draw_risk_card(self, page: fitz.Page, r: Any, y: float) -> float:
        page.draw_rect(fitz.Rect(35, y, 560, y + 55), color=(0.85, 0.8, 0.8), fill=(0.99, 0.98, 0.98), width=0.6)
        page.insert_text((45, y + 15), r.title, fontsize=9, color=self.DARK_NAVY, fontname="hebo")
        page.insert_text((440, y + 15), f"[{r.severity}]", fontsize=8, color=self.ROSE, fontname="hebo")

        citation_str = f"Source: {r.citation.documentName}, P.{r.citation.pageNumber} ({r.citation.clauseNumber or 'General'})"
        page.insert_text((45, y + 30), citation_str, fontsize=7.5, color=self.TEXT_MUTED, fontname="helv")
        page.insert_text((45, y + 44), f"Note: {r.recommendationNote[:120]}...", fontsize=7.5, color=self.TEXT_DARK, fontname="helv")

        return y + 60

    def _draw_risk_indices(self, page: fitz.Page, scores: List[Any], y: float) -> float:
        for s in scores[:5]:
            bar_color = self.EMERALD if s.score >= 75 else (self.AMBER if s.score >= 50 else self.ROSE)
            page.insert_text((40, y + 10), s.category, fontsize=8, color=self.TEXT_DARK, fontname="helv")
            page.insert_text((220, y + 10), f"{s.score}/100 ({s.riskLevel})", fontsize=8, color=bar_color, fontname="hebo")
            page.insert_text((300, y + 10), s.primaryConcern[:60] + "...", fontsize=7.5, color=self.TEXT_MUTED, fontname="helv")
            y += 14
        return y

    def _draw_footer(self, page: fitz.Page, current_page: int, total_pages: int):
        page.draw_line(fitz.Point(35, self.PAGE_HEIGHT - 35), fitz.Point(560, self.PAGE_HEIGHT - 35), color=(0.85, 0.85, 0.88), width=0.5)
        disclaimer = "INFORMATIONAL ANALYSIS ONLY — NOT FORMAL LEGAL ADVICE. VERIFY WITH QUALIFIED COUNSEL BEFORE SIGNING."
        page.insert_text((35, self.PAGE_HEIGHT - 20), disclaimer, fontsize=6.5, color=self.TEXT_MUTED, fontname="helv")
        page.insert_text((515, self.PAGE_HEIGHT - 20), f"Page {current_page} of {total_pages}", fontsize=7.5, color=self.TEXT_MUTED, fontname="helv")


audit_report_pdf_generator = AuditReportPDFGenerator()
