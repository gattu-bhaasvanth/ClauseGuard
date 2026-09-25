import re
from datetime import datetime
from typing import Optional, Tuple


class AreaNormalizer:
    """Normalizes real-estate area measurements into standardized square feet (sq.ft)."""

    SQFT_PATTERNS = [
        re.compile(r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:sq\.?\s*ft\.?|sqft|sft|square\s+feet)", re.IGNORECASE),
    ]
    SQM_PATTERNS = [
        re.compile(r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:sq\.?\s*m\.?|sqm|square\s+met(?:er|re)s?)", re.IGNORECASE),
    ]

    SQM_TO_SQFT_FACTOR = 10.7639104

    @classmethod
    def normalize(cls, raw: str) -> Optional[Tuple[float, str]]:
        if not raw:
            return None

        # Check square meters first (often cited in parentheses e.g. (128.20 sq. m.))
        for pat in cls.SQM_PATTERNS:
            m = pat.search(raw)
            if m:
                num_str = m.group(1).replace(",", "")
                try:
                    sqm_val = float(num_str)
                    sqft_val = round(sqm_val * cls.SQM_TO_SQFT_FACTOR, 2)
                    return (sqft_val, "sq.ft")
                except ValueError:
                    pass

        # Check square feet
        for pat in cls.SQFT_PATTERNS:
            m = pat.search(raw)
            if m:
                num_str = m.group(1).replace(",", "")
                try:
                    return (float(num_str), "sq.ft")
                except ValueError:
                    pass

        # Fallback pure number string
        clean_num = re.sub(r"[^\d\.]", "", raw)
        if clean_num:
            try:
                return (float(clean_num), "sq.ft")
            except ValueError:
                pass

        return None


class CurrencyNormalizer:
    """Normalizes Indian and international currency representations into float INR."""

    # Matches: ₹ 1.42 Cr, Rs. 1.42 Crores, 1.42 Crore, Rs 45 Lakhs, 1,42,00,000, I75,00,000
    CR_PATTERN = re.compile(
        r"(?:₹|rs\.?|inr|I|\|)?\s*(\d+(?:\.\d+)?)\s*(?:cr(?:ore)?s?\.?)", re.IGNORECASE
    )
    LAKH_PATTERN = re.compile(
        r"(?:₹|rs\.?|inr|I|\|)?\s*(\d+(?:\.\d+)?)\s*(?:lakh?s?|lacs?\.?)", re.IGNORECASE
    )
    INR_RAW_PATTERN = re.compile(
        r"(?:₹|rs\.?|inr|I|\|)\s*(\d+(?:,\d+)+(?:\.\d+)?)", re.IGNORECASE
    )

    WORD_NUMS = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
        "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
        "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    }

    @classmethod
    def _parse_words_to_number(cls, s: str) -> float:
        parts = re.split(r"[\s\-]+", s.lower().strip())
        total = 0.0
        current = 0.0
        for p in parts:
            if p in cls.WORD_NUMS:
                current += cls.WORD_NUMS[p]
            elif p in ("hundred", "hundreds"):
                current = (current or 1) * 100
            elif p in ("thousand", "thousands"):
                total += (current or 1) * 1000
                current = 0
            elif p in ("lakh", "lakhs", "lac", "lacs"):
                total += (current or 1) * 100000
                current = 0
            elif p in ("crore", "crores", "cr"):
                total += (current or 1) * 10000000
                current = 0
        return total + current

    @classmethod
    def normalize(cls, raw: str) -> Optional[Tuple[float, str]]:
        if not raw:
            return None

        text = raw.strip()

        # 1. Crores numeric
        m_cr = cls.CR_PATTERN.search(text)
        if m_cr:
            try:
                val = float(m_cr.group(1)) * 10_000_000.0
                return (round(val, 2), "INR")
            except ValueError:
                pass

        # 2. Lakhs numeric
        m_lakh = cls.LAKH_PATTERN.search(text)
        if m_lakh:
            try:
                val = float(m_lakh.group(1)) * 100_000.0
                return (round(val, 2), "INR")
            except ValueError:
                pass

        # 3. Textual word amounts: e.g. "Rupees Seventy-Five Lakh", "One Crore Fifty Lakh"
        m_words = re.search(r"(?:rupees\s+)?([a-z\-\s]+)\s+(lakhs?|lacs?|crores?|cr)", text, re.IGNORECASE)
        if m_words:
            word_part = m_words.group(0).lower().replace("rupees", "").strip()
            num = cls._parse_words_to_number(word_part)
            if num >= 100_000:
                return (round(num, 2), "INR")

        # 4. Formatted currency with comma separators (including I75,00,000, ₹75,00,000)
        m_inr = cls.INR_RAW_PATTERN.search(text)
        if m_inr:
            num_clean = m_inr.group(1).replace(",", "")
            try:
                val = float(num_clean)
                if val >= 1000:
                    return (val, "INR")
            except ValueError:
                pass

        # 5. Pure digits with commas (Indian or western format)
        clean_commas = re.sub(r"[^\d\.]", "", text)
        if clean_commas:
            try:
                val = float(clean_commas)
                if val >= 1000:
                    return (val, "INR")
            except ValueError:
                pass

        return None


class DateNormalizer:
    """
    Normalizes real-estate transaction dates into ISO 8601 while strictly
    preserving extracted precision (DAY, MONTH, or YEAR).
    Never invents missing day or month precision.
    """

    MONTHS = {
        "january": 1, "jan": 1,
        "february": 2, "feb": 2,
        "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "may": 5,
        "june": 6, "jun": 6,
        "july": 7, "jul": 7,
        "august": 8, "aug": 8,
        "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10,
        "november": 11, "nov": 11,
        "december": 12, "dec": 12,
    }

    # Matches: "31st December 2027", "30 June 2027", "18th day of September 2026", "31-Dec-2027"
    TEXTUAL_DATE = re.compile(
        r"(\d{1,2})(?:st|nd|rd|th)?(?:\s+day\s+of)?[\s\-]+([A-Za-z]+)[,\s\-]+(\d{4})",
        re.IGNORECASE,
    )
    # Matches: "December 31, 2027"
    TEXTUAL_DATE_REV = re.compile(
        r"([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?[,\s]+(\d{4})",
        re.IGNORECASE,
    )
    # Matches: "30/06/2027", "30-06-2027" (DD/MM/YYYY)
    NUMERIC_DATE_IN = re.compile(
        r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})"
    )
    # Matches: "2027-12-31", "2027/12/31" (ISO)
    ISO_DATE = re.compile(
        r"(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})"
    )
    # Matches month + year: "June 2027", "Jun 2027", "December 2027", "06/2027"
    MONTH_YEAR_DATE = re.compile(
        r"\b([A-Za-z]+)[,\s]+(\d{4})\b",
        re.IGNORECASE,
    )
    MONTH_NUMERIC_YEAR = re.compile(
        r"\b(0?[1-9]|1[0-2])[\/\-](\d{4})\b"
    )
    # Matches standalone valid transaction year e.g. 2026, 2027, 2028, 2030
    STANDALONE_YEAR = re.compile(
        r"\b(20[2-3]\d)\b"
    )

    @classmethod
    def normalize_with_precision(cls, raw: str) -> Optional[Tuple[str, str]]:
        """
        Returns (normalized_date_str, precision) where precision is 'DAY', 'MONTH', or 'YEAR'.
        Guarantees that a year-only date is never artificially converted into an exact day.
        """
        if not raw:
            return None

        clean_raw = raw.strip()

        # 1. Check ISO (YYYY-MM-DD) -> DAY precision
        m_iso = cls.ISO_DATE.search(clean_raw)
        if m_iso:
            y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
            try:
                dt = datetime(y, m, d)
                return (dt.strftime("%Y-%m-%d"), "DAY")
            except ValueError:
                pass

        # 2. Check textual date "31st December 2027" -> DAY precision
        m_text = cls.TEXTUAL_DATE.search(clean_raw)
        if m_text:
            d_str, month_str, y_str = m_text.group(1), m_text.group(2).lower(), m_text.group(3)
            if month_str in cls.MONTHS:
                m_num = cls.MONTHS[month_str]
                try:
                    dt = datetime(int(y_str), m_num, int(d_str))
                    return (dt.strftime("%Y-%m-%d"), "DAY")
                except ValueError:
                    pass

        # 3. Check textual date reverse "December 31, 2027" -> DAY precision
        m_rev = cls.TEXTUAL_DATE_REV.search(clean_raw)
        if m_rev:
            month_str, d_str, y_str = m_rev.group(1).lower(), m_rev.group(2), m_rev.group(3)
            if month_str in cls.MONTHS:
                m_num = cls.MONTHS[month_str]
                try:
                    dt = datetime(int(y_str), m_num, int(d_str))
                    return (dt.strftime("%Y-%m-%d"), "DAY")
                except ValueError:
                    pass

        # 4. Check DD/MM/YYYY -> DAY precision
        m_num = cls.NUMERIC_DATE_IN.search(clean_raw)
        if m_num:
            d_val, m_val, y_val = int(m_num.group(1)), int(m_num.group(2)), int(m_num.group(3))
            try:
                dt = datetime(y_val, m_val, d_val)
                return (dt.strftime("%Y-%m-%d"), "DAY")
            except ValueError:
                pass

        # 5. Check Month + Year "June 2027" -> MONTH precision
        m_my = cls.MONTH_YEAR_DATE.search(clean_raw)
        if m_my:
            month_str, y_str = m_my.group(1).lower(), m_my.group(2)
            if month_str in cls.MONTHS:
                return (f"{y_str}-{cls.MONTHS[month_str]:02d}", "MONTH")

        m_mny = cls.MONTH_NUMERIC_YEAR.search(clean_raw)
        if m_mny:
            m_val, y_val = int(m_mny.group(1)), int(m_mny.group(2))
            return (f"{y_val}-{m_val:02d}", "MONTH")

        # 6. Check Year-only "target 2027 handover" -> YEAR precision
        m_y = cls.STANDALONE_YEAR.search(clean_raw)
        if m_y:
            return (m_y.group(1), "YEAR")

        return None

    @classmethod
    def normalize(cls, raw: str) -> Optional[str]:
        res = cls.normalize_with_precision(raw)
        return res[0] if res else None

    @classmethod
    def normalize_grace_period(cls, raw: str) -> Optional[Tuple[int, str]]:
        """Parses grace periods like '180 days' -> (6, 'months') or '6 months' -> (6, 'months')."""
        if not raw:
            return None

        # Check days
        m_days = re.search(r"(\d+)\s*(?:days?)", raw, re.IGNORECASE)
        if m_days:
            days = int(m_days.group(1))
            months = round(days / 30)
            return (months, "months")

        # Check months
        m_months = re.search(r"(\d+)\s*(?:months?)", raw, re.IGNORECASE)
        if m_months:
            return (int(m_months.group(1)), "months")

        return None


class PercentageNormalizer:
    """Normalizes interest rates and variation tolerances."""

    @classmethod
    def normalize(cls, raw: str) -> Optional[float]:
        if not raw:
            return None
        m = re.search(r"(?:[±\+\-]?)\s*(\d+(?:\.\d+)?)\s*%", raw)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
        return None


class RERANormalizer:
    """Standardizes and sanitizes RERA registration identification strings."""

    @classmethod
    def normalize(cls, raw: str) -> Optional[str]:
        if not raw:
            return None
        # Clean prefix labels
        clean = re.sub(
            r"^(?:(?:HA|MAHA|KAR|TN|UP)?RERA\s*(?:REGISTRATION\s*(?:NO|NUMBER)?)?[\s:\.\-–]+)",
            "",
            raw.strip(),
            flags=re.IGNORECASE,
        )
        clean = clean.strip()
        # Find RERA pattern: letters, dashes, numbers, slashes e.g. HRERA-PKL-GGM-1248-2023 or PRM/KA/RERA/...
        m = re.search(r"([A-Z0-9\/\-]{8,40})", clean, re.IGNORECASE)
        if m:
            return m.group(1).upper()
        return clean.upper() if len(clean) >= 6 else None
