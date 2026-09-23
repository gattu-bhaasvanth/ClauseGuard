import fitz  # PyMuPDF
from pathlib import Path


def create_sample_digital_pdf(output_path: Path):
    doc = fitz.open()

    # Page 1: Title and Parties
    page1 = doc.new_page(width=595, height=842)  # A4 size
    page1.insert_text(
        (50, 70),
        "AGREEMENT FOR SALE OF APARTMENT\n"
        "SKYVIEW RESIDENCY — TOWER A, UNIT A-1204\n"
        "HARERA REGISTRATION NO: HRERA-PKL-GGM-1248-2023",
        fontsize=12,
        fontname="helv",
    )
    page1.insert_text(
        (50, 140),
        "This Agreement for Sale is executed on this 18th day of September 2026 by and between:\n\n"
        "1. SKYLINE URBAN DEVELOPERS PVT. LTD. (hereinafter referred to as the 'Promoter/Developer')\n"
        "AND\n"
        "2. ALLOTTEE PURCHASER (hereinafter referred to as the 'Allottee').\n\n"
        "WHEREAS the Developer is developing a residential group housing colony named 'SkyView Residency'.",
        fontsize=10,
        fontname="helv",
    )

    # Page 2: Clauses & Specs
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text(
        (50, 70),
        "ARTICLE IV: MEASUREMENT & SPECIFICATIONS\n\n"
        "Clause 4.1: The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft.\n"
        "(128.20 sq. m.). The Promoter reserves the right to make variations of up to +-3% in carpet\n"
        "area without adjustment in the agreed Total Consideration.\n\n"
        "ARTICLE V: PAYMENT TERMS & DEFAULT\n\n"
        "Clause 5.3: If the Allottee fails to pay any installment on or before the due date, the Allottee\n"
        "shall be liable to pay interest on delayed payment at the rate of 18% per annum compounded monthly.\n\n"
        "ARTICLE VIII: POSSESSION & CONVEYANCE\n\n"
        "Clause 8.2: In the event of delay in offering possession of the Apartment beyond the agreed date\n"
        "and grace period of 180 days, the Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft.\n"
        "of super area per month for the period of delay.",
        fontsize=10,
        fontname="helv",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    doc.close()
    print(f"Created sample digital PDF at: {output_path}")


def create_sample_scanned_pdf(output_path: Path):
    """Creates a PDF containing an image layer with low native text to test scan detection & OCR."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # Draw simulated stamped paper background / borders
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 400, 300), 1)
    pix.clear_with(240)  # Off-white vintage deed color
    page.insert_image(fitz.Rect(50, 50, 500, 400), pixmap=pix)

    # Only insert minimal/sparse text so text density < threshold
    page.insert_text((70, 70), "STAMPED LEGAL DEED", fontsize=8, fontname="helv")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    doc.close()
    print(f"Created sample scanned PDF at: {output_path}")


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    samples_dir = root_dir / "data" / "samples"
    create_sample_digital_pdf(samples_dir / "sample_digital_agreement.pdf")
    create_sample_scanned_pdf(samples_dir / "sample_scanned_deed.pdf")
