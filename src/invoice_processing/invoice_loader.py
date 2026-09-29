# from pathlib import Path

# import fitz


# def load_pdf_invoice(file_path: str) -> dict:
#     """
#     Loads a text-based PDF invoice and returns its extracted text.
#     OCR is not used in this first Stage 8 test.
#     """

#     path = Path(file_path)

#     if not path.exists():
#         raise FileNotFoundError(
#             f"Invoice PDF was not found at: {path}"
#         )

#     if path.suffix.lower() != ".pdf":
#         raise ValueError(
#             "This loader currently supports only PDF files."
#         )

#     pages_text = []

#     with fitz.open(path) as pdf_document:
#         for page_number, page in enumerate(pdf_document, start=1):
#             page_text = page.get_text("text").strip()

#             pages_text.append(
#                 f"\n--- Page {page_number} ---\n{page_text}"
#             )

#     raw_text = "\n".join(pages_text).strip()

#     if not raw_text:
#         raise ValueError(
#             "No text was extracted from this PDF. "
#             "It may be a scanned PDF and require OCR."
#         )

#     return {
#         "source_file": str(path),
#         "file_type": "pdf",
#         "extraction_method": "native_pdf_text",
#         "page_count": len(pages_text),
#         "raw_text": raw_text,
#     }


from pathlib import Path

import pymupdf


def load_pdf_invoice(pdf_path: str) -> dict:
    """
    Load one PDF invoice and extract native text from every page.

    Returns:
        A dictionary containing source metadata and extracted text.
    """

    source_path = Path(pdf_path)

    if not source_path.exists():
        raise FileNotFoundError(f"Invoice PDF not found: {source_path}")

    if source_path.suffix.lower() != ".pdf":
        raise ValueError(f"Only PDF files are supported. Received: {source_path.suffix}")

    extracted_pages = []

    document = pymupdf.open(source_path)

    try:
        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text").strip()

            extracted_pages.append(
                f"--- Page {page_number} ---\n{page_text}"
            )
    finally:
        document.close()

    raw_text = "\n\n".join(extracted_pages).strip()

    return {
        "source_file": str(source_path),
        "file_type": "pdf",
        "extraction_method": "native_pdf_text",
        "page_count": len(extracted_pages),
        "raw_text": raw_text,
    }