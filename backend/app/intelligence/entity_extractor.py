import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

from app.intelligence.entity_normalizer import (
    AreaNormalizer,
    CurrencyNormalizer,
    DateNormalizer,
    PercentageNormalizer,
    RERANormalizer,
)
from app.intelligence.segmenter import RawClauseChunk


@dataclass
class ExtractedEntity:
    attribute_key: str
    attribute_value: str
    normalized_value: str
    unit: str
    source_page: int
    source_clause: Optional[str]
    raw_excerpt: str
    confidence: float = 1.0


class TransactionEntityExtractor:
    """
    Extracts structured real-estate parameters (metrics, financials, timelines,
    parties, payment milestones) with exact source evidence lineage.
    """

    # --- Property Patterns ---
    CARPET_AREA_PATTERNS = [
        re.compile(r"(?:rera\s+)?carpet\s+area\s+(?:of\s+|is\s+|:\s*)?([0-9,]+(?:\.[0-9]+)?\s*(?:sq\.?\s*ft\.?|sqft|sq\.?\s*m\.?|square\s+feet))", re.IGNORECASE),
        re.compile(r"([0-9,]+(?:\.[0-9]+)?\s*(?:sq\.?\s*ft\.?|sqft|sq\.?\s*m\.?))\s*(?:rera\s+)?carpet\s+area", re.IGNORECASE),
    ]

    SUPER_AREA_PATTERNS = [
        re.compile(r"super\s+(?:built-?up\s+)?area\s+(?:of\s+|is\s+|:\s*)?([0-9,]+(?:\.[0-9]+)?\s*(?:sq\.?\s*ft\.?|sqft|sq\.?\s*m\.?|square\s+feet))", re.IGNORECASE),
        re.compile(r"([0-9,]+(?:\.[0-9]+)?\s*(?:sq\.?\s*ft\.?|sqft|sq\.?\s*m\.?))\s*(?:of\s+)?super\s+(?:built-?up\s+)?area", re.IGNORECASE),
    ]

    UNIT_PATTERNS = [
        re.compile(r"(?:unit|apartment|flat)\s+(?:no\.?|number)?\s*[:\-–]?\s*([A-Za-z0-9\-]+)", re.IGNORECASE),
    ]

    TOWER_PATTERNS = [
        re.compile(r"(?:tower|block|wing)\s+[:\-–]?\s*([A-Za-z0-9\-]+)", re.IGNORECASE),
    ]

    # --- Financial Patterns ---
    TOTAL_CONSIDERATION_PATTERNS = [
        re.compile(r"(?:total\s+consideration|total\s+sale\s+price|agreed\s+consideration|total\s+price)\s+(?:of\s+|is\s+|:\s*)?([₹\w\.\s,]+?(?:\/-|\.|\n|$))", re.IGNORECASE),
        re.compile(r"total\s+consideration\s+of\s+([₹\w\.\s,]+)", re.IGNORECASE),
    ]

    BOOKING_AMOUNT_PATTERNS = [
        re.compile(r"(?:booking\s+amount|earnest\s+money|advance\s+amount)\s+(?:of\s+|is\s+|:\s*)?([₹\w\.\s,]+?(?:\/-|\.|\n|$))", re.IGNORECASE),
    ]

    DELAY_INTEREST_PATTERNS = [
        re.compile(r"interest\s+on\s+delayed\s+payment\s+(?:at\s+the\s+rate\s+of\s+|:\s*)?([0-9]+(?:\.[0-9]+)?\s*%)", re.IGNORECASE),
        re.compile(r"delayed\s+payment\s+(?:interest\s+)?at\s+(?:the\s+rate\s+of\s+)?([0-9]+(?:\.[0-9]+)?\s*%)", re.IGNORECASE),
    ]

    # --- Timeline Patterns ---
    POSSESSION_DATE_PATTERNS = [
        re.compile(
            r"(?:complete\s+construction[^.\n]*?by|possession[^.\n]*?(?:by|on|for|is|date|target)|handover[^.\n]*?(?:by|on|for|is|date|target))\s*[:\-–]?\s*([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+[0-9]{4}|[0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4}|[0-9]{4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,2})",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?:possession\s+date|handover\s+date|completion\s+date)\s*[:\-–]?\s*([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+[0-9]{4}|[0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4}|[0-9]{4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,2})",
            re.IGNORECASE,
        ),
    ]

    GRACE_PERIOD_PATTERNS = [
        re.compile(r"grace\s+period\s+of\s+([0-9]+(?:\s*\([a-z\s]+\))?\s*(?:days?|months?))", re.IGNORECASE),
    ]

    DEFECT_LIABILITY_PATTERNS = [
        re.compile(r"(?:defect\s+liability\s+period|defects\s+liability)\s+(?:of\s+|is\s+|:\s*)?([0-9]+(?:\s*\([a-z\s]+\))?\s*(?:years?|months?))", re.IGNORECASE),
    ]

    # --- Party & Regulatory Patterns ---
    RERA_PATTERNS = [
        re.compile(r"(?:(?:ha|maha|kar|tn|up)?rera\s*(?:registration\s*(?:no|number)?)?[\s:\.\-–]+)([A-Z0-9\/\-]{8,35})", re.IGNORECASE),
    ]

    DEVELOPER_PATTERNS = [
        re.compile(r"([A-Z0-9\s\.,&]+?(?:pvt\.?\s*ltd\.?|limited|developers|properties|builders|llp|realtors))\s*(?:\(hereinafter\s+referred\s+to\s+as\s+the\s+['\"](?:Promoter|Developer)['\"]\)|,\s*having\s+its\s+registered\s+office)", re.IGNORECASE),
    ]

    # --- Milestone Patterns ---
    MILESTONE_ROW_PATTERN = re.compile(
        r"^(?:(?:\d+[\.\)]\s*)?(?:on\s+|at\s+the\s+time\s+of\s+|upon\s+)?([A-Za-z0-9\s\-_–\(\)]+?))\s*[:\-–\t]\s*(\d+(?:\.\d+)?\s*%|\d+(?:,\d+)+(?:\.\d+)?)",
        re.MULTILINE | re.IGNORECASE,
    )

    def extract_from_clauses_and_pages(
        self,
        pages: List[Tuple[int, str]],
        clauses: Optional[List[RawClauseChunk]] = None,
    ) -> List[ExtractedEntity]:
        """
        Runs multi-pass entity extraction combining clause-level and page-level analysis.
        """
        entities: List[ExtractedEntity] = []

        # 1. Clause-level extraction (high precision with clause headers)
        if clauses:
            for clause in clauses:
                clause_entities = self._extract_from_text(
                    text=clause.full_excerpt,
                    page_number=clause.page_number,
                    clause_number=clause.clause_number,
                )
                entities.extend(clause_entities)

        # 2. Page-level extraction (for un-segmented text, preambles, headers)
        for page_num, page_text in pages:
            page_entities = self._extract_from_text(
                text=page_text,
                page_number=page_num,
                clause_number=None,
            )
            entities.extend(page_entities)

        # 3. Deduplicate entities by (attribute_key, normalized_value)
        return self._deduplicate_entities(entities)

    def _extract_from_text(
        self, text: str, page_number: int, clause_number: Optional[str]
    ) -> List[ExtractedEntity]:
        found: List[ExtractedEntity] = []

        # Carpet Area
        for pat in self.CARPET_AREA_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                norm = AreaNormalizer.normalize(raw_val)
                if norm:
                    found.append(
                        ExtractedEntity(
                            attribute_key="carpet_area",
                            attribute_value=raw_val,
                            normalized_value=str(norm[0]),
                            unit=norm[1],
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.95 if clause_number else 0.85,
                        )
                    )

        # Super Area
        for pat in self.SUPER_AREA_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                norm = AreaNormalizer.normalize(raw_val)
                if norm:
                    found.append(
                        ExtractedEntity(
                            attribute_key="super_area",
                            attribute_value=raw_val,
                            normalized_value=str(norm[0]),
                            unit=norm[1],
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.92,
                        )
                    )

        # Total Price / Consideration
        for pat in self.TOTAL_CONSIDERATION_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                norm = CurrencyNormalizer.normalize(raw_val)
                if norm and norm[0] >= 100_000:  # Real estate prices exceed 1 Lakh
                    found.append(
                        ExtractedEntity(
                            attribute_key="total_price",
                            attribute_value=raw_val,
                            normalized_value=str(norm[0]),
                            unit=norm[1],
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.92 if clause_number else 0.82,
                        )
                    )

        # Delayed Payment Interest Rate
        for pat in self.DELAY_INTEREST_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                norm = PercentageNormalizer.normalize(raw_val)
                if norm:
                    found.append(
                        ExtractedEntity(
                            attribute_key="delayed_payment_interest_rate",
                            attribute_value=raw_val,
                            normalized_value=str(norm),
                            unit="%",
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.95,
                        )
                    )

        # Possession Date
        for pat in self.POSSESSION_DATE_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                norm = DateNormalizer.normalize(raw_val)
                if norm:
                    found.append(
                        ExtractedEntity(
                            attribute_key="possession_date",
                            attribute_value=raw_val,
                            normalized_value=norm,
                            unit="date",
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.93 if clause_number else 0.85,
                        )
                    )

        # Grace Period
        for pat in self.GRACE_PERIOD_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                norm = DateNormalizer.normalize_grace_period(raw_val)
                if norm:
                    found.append(
                        ExtractedEntity(
                            attribute_key="grace_period_months",
                            attribute_value=raw_val,
                            normalized_value=str(norm[0]),
                            unit=norm[1],
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.94,
                        )
                    )

        # Defect Liability Period
        for pat in self.DEFECT_LIABILITY_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                clean_num = re.search(r"(\d+)", raw_val)
                if clean_num:
                    found.append(
                        ExtractedEntity(
                            attribute_key="defect_liability_years",
                            attribute_value=raw_val,
                            normalized_value=clean_num.group(1),
                            unit="years",
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.90,
                        )
                    )

        # Unit Number
        for pat in self.UNIT_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                if len(raw_val) >= 2 and not raw_val.lower().startswith("of"):
                    found.append(
                        ExtractedEntity(
                            attribute_key="unit_number",
                            attribute_value=raw_val,
                            normalized_value=raw_val.upper(),
                            unit="",
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.90,
                        )
                    )

        # Tower / Block
        for pat in self.TOWER_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                if len(raw_val) >= 1 and len(raw_val) <= 15:
                    found.append(
                        ExtractedEntity(
                            attribute_key="tower",
                            attribute_value=raw_val,
                            normalized_value=raw_val.upper(),
                            unit="",
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.88,
                        )
                    )

        # RERA Registration
        for pat in self.RERA_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                norm = RERANormalizer.normalize(raw_val)
                if norm:
                    found.append(
                        ExtractedEntity(
                            attribute_key="rera_registration_number",
                            attribute_value=raw_val,
                            normalized_value=norm,
                            unit="",
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.96,
                        )
                    )

        # Developer Legal Entity
        for pat in self.DEVELOPER_PATTERNS:
            for m in pat.finditer(text):
                raw_val = m.group(1).strip()
                clean_name = re.sub(r"^[\s\d\.\-]+", "", raw_val).strip()
                if len(clean_name) >= 5:
                    found.append(
                        ExtractedEntity(
                            attribute_key="developer_name",
                            attribute_value=clean_name,
                            normalized_value=clean_name.title(),
                            unit="",
                            source_page=page_number,
                            source_clause=clause_number,
                            raw_excerpt=self._get_context_window(text, m.start(), m.end()),
                            confidence=0.91,
                        )
                    )

        return found

    def extract_payment_milestones(
        self, text: str, page_number: int = 1
    ) -> List[Dict[str, Any]]:
        """Parses payment milestones with percentages, amounts, and trigger conditions."""
        milestones = []
        for line in text.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue

            # Look for lines with percentages or currency amounts
            pct_m = re.search(r"(\d+(?:\.\d+)?)\s*%", line_str)
            if pct_m:
                milestone_desc = line_str[:pct_m.start()].strip()
                milestone_desc = re.sub(r"^[0-9\.\-\–\)]+\s*", "", milestone_desc).strip()
                if not milestone_desc:
                    milestone_desc = line_str

                milestones.append({
                    "milestone": milestone_desc,
                    "percentage": float(pct_m.group(1)),
                    "amount": None,
                    "dueEventOrDate": milestone_desc,
                })

        return milestones

    @staticmethod
    def _get_context_window(text: str, start: int, end: int, window: int = 70) -> str:
        ctx_start = max(0, start - window)
        ctx_end = min(len(text), end + window)
        excerpt = text[ctx_start:ctx_end].replace("\n", " ").strip()
        if ctx_start > 0:
            excerpt = "..." + excerpt
        if ctx_end < len(text):
            excerpt = excerpt + "..."
        return excerpt

    @staticmethod
    def _deduplicate_entities(entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        seen = set()
        deduped = []
        # Sort so entities with clauses come before un-claused ones, and higher confidence first
        sorted_entities = sorted(
            entities,
            key=lambda e: (e.source_clause is not None, e.confidence),
            reverse=True,
        )
        for e in sorted_entities:
            key = (e.attribute_key, e.normalized_value)
            if key not in seen:
                seen.add(key)
                deduped.append(e)
        return deduped


transaction_entity_extractor = TransactionEntityExtractor()
