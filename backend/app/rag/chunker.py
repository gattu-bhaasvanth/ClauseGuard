from dataclasses import dataclass
from typing import List, Optional
import re
from app.models.document import Document, DocumentPage
from app.models.clause import Clause
from app.intelligence.segmenter import ClauseBoundaryDetector


@dataclass
class ProcessedChunk:
    bundle_id: str
    document_id: str
    page_number: int
    clause_number: Optional[str]
    clause_title: Optional[str]
    chunk_type: str  # "CLAUSE" or "PAGE_SECTION"
    chunk_text: str


class ClauseCentricChunker:
    """
    Splits legal and transaction documents into provenance-preserving chunks.
    Prioritizes structured legal clauses (e.g. Clause 8.2), with fallbacks for
    unstructured page sections while maintaining exact document, page, and clause lineage.
    """

    MAX_CHUNK_WORDS = 600
    OVERLAP_WORDS = 50

    def __init__(self):
        self.boundary_detector = ClauseBoundaryDetector()

    def chunk_document(self, document: Document, clauses: Optional[List[Clause]] = None) -> List[ProcessedChunk]:
        """
        Creates chunks from a Document model instance.
        If clauses are available, chunk by clause. Otherwise, process page text.
        """
        chunks: List[ProcessedChunk] = []

        # 1. Use existing extracted clauses if available
        doc_clauses = clauses if clauses is not None else (document.clauses or [])
        if doc_clauses:
            for clause in doc_clauses:
                clause_chunks = self._chunk_clause(document.bundle_id, document.id, clause)
                chunks.extend(clause_chunks)
            if chunks:
                return chunks

        # 2. Fallback to document pages if no extracted clauses exist
        pages = document.pages or []
        for page in sorted(pages, key=lambda p: p.page_number):
            page_chunks = self._chunk_page(document.bundle_id, document.id, page)
            chunks.extend(page_chunks)

        return chunks

    def _chunk_clause(self, bundle_id: str, document_id: str, clause: Clause) -> List[ProcessedChunk]:
        """
        Chunk a single clause record, splitting oversized clauses if necessary.
        """
        body_text = (clause.full_excerpt or clause.preview_text or "").strip()
        header = f"{clause.clause_number}: {clause.title}"
        full_text = f"{header}\n{body_text}" if body_text else header

        words = full_text.split()
        if len(words) <= self.MAX_CHUNK_WORDS:
            return [
                ProcessedChunk(
                    bundle_id=bundle_id,
                    document_id=document_id,
                    page_number=clause.page_number or 1,
                    clause_number=clause.clause_number,
                    clause_title=clause.title,
                    chunk_type="CLAUSE",
                    chunk_text=full_text,
                )
            ]

        # Oversized clause: split into paragraph chunks with overlap
        chunks: List[ProcessedChunk] = []
        paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]

        current_para_text = ""
        for para in paragraphs:
            if len((current_para_text + " " + para).split()) > self.MAX_CHUNK_WORDS and current_para_text:
                chunk_content = f"{header} (Continued)\n{current_para_text}"
                chunks.append(
                    ProcessedChunk(
                        bundle_id=bundle_id,
                        document_id=document_id,
                        page_number=clause.page_number or 1,
                        clause_number=clause.clause_number,
                        clause_title=clause.title,
                        chunk_type="CLAUSE",
                        chunk_text=chunk_content,
                    )
                )
                current_para_text = para
            else:
                current_para_text = f"{current_para_text}\n{para}".strip()

        if current_para_text:
            chunk_content = f"{header} (Continued)\n{current_para_text}" if chunks else f"{header}\n{current_para_text}"
            chunks.append(
                ProcessedChunk(
                    bundle_id=bundle_id,
                    document_id=document_id,
                    page_number=clause.page_number or 1,
                    clause_number=clause.clause_number,
                    clause_title=clause.title,
                    chunk_type="CLAUSE",
                    chunk_text=chunk_content,
                )
            )

        return chunks

    def _chunk_page(self, bundle_id: str, document_id: str, page: DocumentPage) -> List[ProcessedChunk]:
        """
        Fallback chunking for document pages without pre-extracted clauses.
        Attempts boundary detection; falls back to paragraph sections.
        """
        raw_text = (page.raw_text or "").strip()
        if not raw_text:
            return []

        # Try clause boundary detector
        detected = self.boundary_detector.detect_clauses(raw_text, page_number=page.page_number)
        if detected:
            chunks: List[ProcessedChunk] = []
            for item in detected:
                header = f"{item['clause_number']}: {item['title']}"
                chunk_text = f"{header}\n{item['text']}" if item.get("text") else header
                chunks.append(
                    ProcessedChunk(
                        bundle_id=bundle_id,
                        document_id=document_id,
                        page_number=page.page_number,
                        clause_number=item.get("clause_number"),
                        clause_title=item.get("title"),
                        chunk_type="CLAUSE",
                        chunk_text=chunk_text,
                    )
                )
            return chunks

        # Fallback to paragraph splitting
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if len(p.strip()) > 30]
        if not paragraphs:
            paragraphs = [raw_text]

        chunks = []
        for i, para in enumerate(paragraphs, 1):
            chunks.append(
                ProcessedChunk(
                    bundle_id=bundle_id,
                    document_id=document_id,
                    page_number=page.page_number,
                    clause_number=None,
                    clause_title=f"Page {page.page_number} Section {i}",
                    chunk_type="PAGE_SECTION",
                    chunk_text=para,
                )
            )
        return chunks
