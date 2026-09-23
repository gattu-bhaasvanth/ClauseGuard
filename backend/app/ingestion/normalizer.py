import re
from typing import List


class DocumentNormalizer:
    """
    Normalizes extracted legal contract text:
    - Removes common repeating running header/footer artifacts
    - De-hyphenates words broken across line wraps (e.g., 'conve-\nyance' -> 'conveyance')
    - Cleans non-standard unicode characters, spaces, and punctuation
    - Preserves clause numbers and tabular milestones
    """

    # Common running header/footer patterns in legal deeds
    HEADER_FOOTER_PATTERNS = [
        re.compile(r"^\s*Page\s+\d+\s+(?:of|\/)\s+\d+\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*-\s*\d+\s*-\s*$", re.MULTILINE),
        re.compile(r"^\s*Draft\s+Agreement\s+for\s+Discussion\s+Purposes\s+Only\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Confidential\s*$", re.IGNORECASE | re.MULTILINE),
    ]

    # Dehyphenation pattern
    HYPHENATION_PATTERN = re.compile(r"(\b[a-zA-Z]{2,})-\n([a-zA-Z]{2,}\b)")

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""

        # 1. Normalize unicode characters (smart quotes, non-breaking spaces, em-dashes)
        normalized = text.replace("\u00a0", " ")
        normalized = normalized.replace("\u2018", "'").replace("\u2019", "'")
        normalized = normalized.replace("\u201c", '"').replace("\u201d", '"')
        normalized = normalized.replace("\u2013", "-").replace("\u2014", " - ")

        # 2. Strip running headers & footers
        for pattern in self.HEADER_FOOTER_PATTERNS:
            normalized = pattern.sub("", normalized)

        # 3. De-hyphenate broken words across line breaks
        normalized = self.HYPHENATION_PATTERN.sub(r"\1\2", normalized)

        # 4. Collapse excessive blank lines (more than 2 consecutive newlines into 2)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)

        # 5. Clean trailing whitespace per line
        lines = [line.strip() for line in normalized.split("\n")]
        return "\n".join(lines).strip()

    def clean_table_row(self, row_text: str) -> str:
        """Standardizes spacing in milestone tables."""
        return re.sub(r"\s{2,}", " | ", row_text.strip())
