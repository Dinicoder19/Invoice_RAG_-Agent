# from src.invoice_processing.invoice_loader import load_pdf_invoice


# INVOICE_FILE_PATH = "data/invoices/Invoice_PO-7001.pdf"


# def main():
#     loaded_invoice = load_pdf_invoice(INVOICE_FILE_PATH)

#     print("\n--- Source File ---")
#     print(loaded_invoice["source_file"])

#     print("\n--- File Type ---")
#     print(loaded_invoice["file_type"])

#     print("\n--- Extraction Method ---")
#     print(loaded_invoice["extraction_method"])

#     print("\n--- Page Count ---")
#     print(loaded_invoice["page_count"])

#     print("\n--- Extracted Raw Text ---")
#     print(loaded_invoice["raw_text"])


# if __name__ == "__main__":
#     main()

from pathlib import Path

from src.invoice_processing.invoice_loader import load_pdf_invoice


INVOICE_DIRECTORY = Path("data/invoices")


def main():
    pdf_files = sorted(INVOICE_DIRECTORY.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {INVOICE_DIRECTORY.resolve()}")
        return

    print("\n========== Stage 8 Invoice Loader Test ==========")
    print(f"Invoice folder: {INVOICE_DIRECTORY.resolve()}")
    print(f"PDF files found: {len(pdf_files)}")

    for pdf_file in pdf_files:
        print("\n" + "=" * 70)
        print(f"Processing PDF: {pdf_file.name}")
        print("=" * 70)

        try:
            loaded_invoice = load_pdf_invoice(str(pdf_file))

            print("\n--- Source File ---")
            print(loaded_invoice["source_file"])

            print("\n--- File Type ---")
            print(loaded_invoice["file_type"])

            print("\n--- Extraction Method ---")
            print(loaded_invoice["extraction_method"])

            print("\n--- Page Count ---")
            print(loaded_invoice["page_count"])

            print("\n--- Extracted Raw Text ---")
            print(loaded_invoice["raw_text"])

        except Exception as error:
            print("\n--- Processing Error ---")
            print(f"{type(error).__name__}: {error}")


if __name__ == "__main__":
    main()