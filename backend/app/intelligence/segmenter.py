import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class RawClauseChunk:
    clause_number: str
    title: str
    full_excerpt: str
    preview_text: str
    page_number: int


class ClauseBoundaryDetector:
    """
    Regex and layout-informed legal clause boundary detector.
    Segments continuous legal contract text into individual numbered clauses,
    articles, and schedules across document pages.
    """

    # Primary header patterns in real-estate contracts
    PATTERNS = [
        # Pattern 1: ARTICLE IV: SPECIFICATIONS & MEASUREMENTS or ARTICLE 4 - TITLE
        re.compile(
            r"^(?:ARTICLE|SECTION)\s+([IVXLCDM\d]+)[\s:\.\-–]+([^\n]+)",
            re.IGNORECASE,
        ),
        # Pattern 2: Clause 4.1: Title or Clause 8.2 (Title)
        re.compile(
            r"^Clause\s+(\d+(?:\.\d+)*)[\s:\.\-–]+([^\n]+)",
            re.IGNORECASE,
        ),
        # Pattern 3: Numbered header: 8.2. Delayed Possession Compensation: or 4.1 Title
        re.compile(
            r"^(\d+\.\d+(?:\.\d+)*)[\s:\.\-–]+([^\n]+)",
        ),
        # Pattern 4: Schedule I or Schedule A - Title
        re.compile(
            r"^(?:SCHEDULE|ANNEXURE)\s+([A-Z\d]+)[\s:\.\-–]+([^\n]+)",
            re.IGNORECASE,
        ),
    ]

    def segment_pages(self, pages: List[Tuple[int, str]]) -> List[RawClauseChunk]:
        """
        Segments a list of (page_number, text) tuples into structured clause chunks.
        """
        clauses: List[RawClauseChunk] = []
        current_num: Optional[str] = None
        current_title: Optional[str] = None
        current_page: int = 1
        current_lines: List[str] = []

        for page_num, page_text in pages:
            lines = page_text.split("\n")
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    if current_lines:
                        current_lines.append("")
                    continue

                # Check if this line is a clause boundary header
                match_info = self._match_header(stripped)
                if match_info:
                    # Save previous clause if present
                    if current_num and current_lines:
                        excerpt = "\n".join(current_lines).strip()
                        if excerpt:
                            clauses.append(
                                RawClauseChunk(
                                    clause_number=current_num,
                                    title=current_title or current_num,
                                    full_excerpt=excerpt,
                                    preview_text=self._generate_preview(excerpt),
                                    page_number=current_page,
                                )
                            )

                    # Start new clause
                    c_num, c_title = match_info
                    current_num = c_num
                    current_title = c_title
                    current_page = page_num
                    current_lines = [stripped]
                else:
                    if current_num:
                        current_lines.append(stripped)

        # Flush the final clause
        if current_num and current_lines:
            excerpt = "\n".join(current_lines).strip()
            if excerpt:
                clauses.append(
                    RawClauseChunk(
                        clause_number=current_num,
                        title=current_title or current_num,
                        full_excerpt=excerpt,
                        preview_text=self._generate_preview(excerpt),
                        page_number=current_page,
                    )
                )

        # Fallback: If no structured headers were matched (e.g. informal letter or schedule)
        if not clauses:
            for page_num, page_text in pages:
                text_clean = page_text.strip()
                if text_clean:
                    clauses.append(
                        RawClauseChunk(
                            clause_number=f"Page {page_num}",
                            title=f"General Terms — Page {page_num}",
                            full_excerpt=text_clean,
                            preview_text=self._generate_preview(text_clean),
                            page_number=page_num,
                        )
                    )

        return clauses

    def _match_header(self, line: str) -> Optional[Tuple[str, str]]:
        """Checks if a line matches any of the registered clause header patterns."""
        for pattern in self.PATTERNS:
            m = pattern.match(line)
            if m:
                groups = m.groups()
                num_part = groups[0].strip()
                title_part = groups[1].strip() if len(groups) > 1 else ""

                # Format clean clause label
                if "ARTICLE" in line.upper():
                    clause_label = f"Article {num_part}"
                elif "SCHEDULE" in line.upper() or "ANNEXURE" in line.upper():
                    clause_label = f"Schedule {num_part}"
                elif not num_part.lower().startswith("clause"):
                    clause_label = f"Clause {num_part}"
                else:
                    clause_label = num_part

                # Clean title punctuation
                clean_title = re.sub(r"^[\s:\.\-–]+", "", title_part).strip()
                if not clean_title or len(clean_title) < 3:
                    clean_title = clause_label
                elif len(clean_title) > 75:
                    truncated = clean_title[:72].rsplit(" ", 1)[0]
                    clean_title = f"{truncated}..."

                return (clause_label, clean_title)
        return None

    @staticmethod
    def _generate_preview(text: str, max_chars: int = 120) -> str:
        first_line = text.split("\n")[0].strip()
        if len(first_line) > max_chars:
            return first_line[:max_chars] + "..."
        if len(text) > len(first_line):
            rem = text[len(first_line):].strip()
            avail = max_chars - len(first_line)
            if avail > 20 and rem:
                return f"{first_line} {rem[:avail]}..."
        return first_line
