import re
from datetime import datetime
from typing import Optional, Tuple


class AreaNormalizer:
    """Normalizes real-estate area measurements into standardized square feet (sq.ft)."""

    SQFT_PATTERNS = [
        re.compile(r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:sq\.?\s*ft\.?|sqft|square\s+feet)", re.IGNORECASE),
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

    # Matches: ₹ 1.42 Cr, Rs. 1.42 Crores, 1.42 Crore, Rs 45 Lakhs, 1,42,00,000
    CR_PATTERN = re.compile(
        r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:cr(?:ore)?s?\.?)", re.IGNORECASE
    )
    LAKH_PATTERN = re.compile(
        r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:lakh?s?|lacs?\.?)", re.IGNORECASE
    )
    INR_RAW_PATTERN = re.compile(
        r"(?:₹|rs\.?|inr)\s*(\d+(?:,\d+)+(?:\.\d+)?)", re.IGNORECASE
    )

    @classmethod
    def normalize(cls, raw: str) -> Optional[Tuple[float, str]]:
        if not raw:
            return None

        text = raw.strip()

        # 1. Crores
        m_cr = cls.CR_PATTERN.search(text)
        if m_cr:
            try:
                val = float(m_cr.group(1)) * 10_000_000.0
                return (round(val, 2), "INR")
            except ValueError:
                pass

        # 2. Lakhs
        m_lakh = cls.LAKH_PATTERN.search(text)
        if m_lakh:
            try:
                val = float(m_lakh.group(1)) * 100_000.0
                return (round(val, 2), "INR")
            except ValueError:
                pass

        # 3. Formatted currency with comma separators
        m_inr = cls.INR_RAW_PATTERN.search(text)
        if m_inr:
            num_clean = m_inr.group(1).replace(",", "")
            try:
                return (float(num_clean), "INR")
            except ValueError:
                pass

        # 4. Pure digits with commas
        clean_commas = re.sub(r"[^\d\.]", "", text)
        if clean_commas:
            try:
                return (float(clean_commas), "INR")
            except ValueError:
                pass

        return None


class DateNormalizer:
    """Normalizes dates into standard ISO 8601 (YYYY-MM-DD)."""

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

    # Matches: "31st December 2027", "30 June 2027", "18th day of September 2026"
    TEXTUAL_DATE = re.compile(
        r"(\d{1,2})(?:st|nd|rd|th)?(?:\s+day\s+of)?\s+([A-Za-z]+)[,\s]+(\d{4})",
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
    # Matches: "2027-12-31" (ISO)
    ISO_DATE = re.compile(
        r"(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})"
    )

    @classmethod
    def normalize(cls, raw: str) -> Optional[str]:
        if not raw:
            return None

        # Check ISO first
        m_iso = cls.ISO_DATE.search(raw)
        if m_iso:
            y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
            try:
                dt = datetime(y, m, d)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Check textual date "31st December 2027"
        m_text = cls.TEXTUAL_DATE.search(raw)
        if m_text:
            d_str, month_str, y_str = m_text.group(1), m_text.group(2).lower(), m_text.group(3)
            if month_str in cls.MONTHS:
                m_num = cls.MONTHS[month_str]
                try:
                    dt = datetime(int(y_str), m_num, int(d_str))
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass

        # Check textual date reverse "December 31, 2027"
        m_rev = cls.TEXTUAL_DATE_REV.search(raw)
        if m_rev:
            month_str, d_str, y_str = m_rev.group(1).lower(), m_rev.group(2), m_rev.group(3)
            if month_str in cls.MONTHS:
                m_num = cls.MONTHS[month_str]
                try:
                    dt = datetime(int(y_str), m_num, int(d_str))
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass

        # Check DD/MM/YYYY
        m_num = cls.NUMERIC_DATE_IN.search(raw)
        if m_num:
            d_val, m_val, y_val = int(m_num.group(1)), int(m_num.group(2)), int(m_num.group(3))
            try:
                dt = datetime(y_val, m_val, d_val)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        return None

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
