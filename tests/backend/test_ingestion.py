from pathlib import Path
import pytest
from httpx import AsyncClient
import fitz

from app.ingestion.extractors.density_checker import PageDensityChecker
from app.ingestion.extractors.digital_pdf import DigitalPDFExtractor
from app.ingestion.ocr.mock_engine import MockOCREngine
from app.ingestion.normalizer import DocumentNormalizer
from app.ingestion.pipeline import IngestionPipeline


@pytest.fixture
def samples_dir():
    return Path(__file__).resolve().parent.parent.parent / "data" / "samples"


def test_normalizer():
    normalizer = DocumentNormalizer()
    raw = (
        "Page 12 of 38\n"
        "The Allottee agrees to make regular pay-\n"
        "ments in accordance with the “Schedule of Payments”.\n"
        "- 12 -\n"
    )
    cleaned = normalizer.normalize_text(raw)
    # Check dehyphenation
    assert "payments" in cleaned
    assert "pay-\nments" not in cleaned
    # Check running header/footer stripped
    assert "Page 12 of 38" not in cleaned
    assert "- 12 -" not in cleaned
    # Check smart quotes normalized
    assert '"Schedule of Payments"' in cleaned


def test_density_checker(samples_dir: Path):
    checker = PageDensityChecker()

    # 1. Test digital document
    doc_digital = fitz.open(str(samples_dir / "sample_digital_agreement.pdf"))
    assessment_digital = checker.assess_page(doc_digital[0])
    doc_digital.close()
    assert assessment_digital.is_scanned is False
    assert assessment_digital.char_count > 100

    # 2. Test scanned deed
    doc_scanned = fitz.open(str(samples_dir / "sample_scanned_deed.pdf"))
    assessment_scanned = checker.assess_page(doc_scanned[0])
    doc_scanned.close()
    assert assessment_scanned.is_scanned is True
    assert assessment_scanned.image_count > 0


def test_digital_pdf_extractor(samples_dir: Path):
    extractor = DigitalPDFExtractor()
    result = extractor.extract_document(samples_dir / "sample_digital_agreement.pdf")

    assert result.total_pages == 2
    assert result.scanned_pages_count == 0
    assert len(result.pages) == 2

    page2 = result.pages[1]
    assert "Clause 4.1" in page2.normalized_text
    assert "1,380 sq. ft." in page2.normalized_text
    assert len(page2.layout_boxes) > 0
    first_box = page2.layout_boxes[0]
    assert "x0" in first_box and "y0" in first_box
    assert "text" in first_box


def test_ocr_fallback_pipeline(samples_dir: Path):
    mock_ocr = MockOCREngine(simulated_text="REPUBLIC OF INDIA - STAMPED AGREEMENT FOR SALE")
    extractor = DigitalPDFExtractor(ocr_engine=mock_ocr)
    result = extractor.extract_document(samples_dir / "sample_scanned_deed.pdf")

    assert result.total_pages == 1
    assert result.scanned_pages_count == 1
    assert result.pages[0].ocr_applied is True
    assert "STAMPED AGREEMENT FOR SALE" in result.pages[0].normalized_text
    assert len(result.pages[0].layout_boxes) > 0


@pytest.mark.asyncio
async def test_upload_and_pages_api(client: AsyncClient, samples_dir: Path):
    pdf_path = samples_dir / "sample_digital_agreement.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # Upload document
    files = {"file": ("Uploaded_Digital_Agreement.pdf", file_bytes, "application/pdf")}
    data = {"document_type": "BUILDER_BUYER_AGREEMENT"}

    response = await client.post(
        "/api/v1/transactions/skyview-a1204/documents/upload",
        files=files,
        data=data,
    )
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["fileName"] == "Uploaded_Digital_Agreement.pdf"
    assert res_data["pageCount"] == 2
    assert res_data["ocrStatus"] == "NOT_REQUIRED"
    doc_id = res_data["documentId"]

    # Fetch parsed pages
    pages_res = await client.get(
        f"/api/v1/transactions/skyview-a1204/documents/{doc_id}/pages"
    )
    assert pages_res.status_code == 200
    pages = pages_res.json()
    assert len(pages) == 2
    assert pages[0]["pageNumber"] == 1
    assert pages[1]["pageNumber"] == 2
    assert "Clause 4.1" in pages[1]["rawText"]
    assert len(pages[1]["layoutBoxes"]) > 0
