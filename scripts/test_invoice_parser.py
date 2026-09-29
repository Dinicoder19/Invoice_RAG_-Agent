# import json
# from pathlib import Path

# from src.invoice_processing.invoice_loader import load_pdf_invoice
# from src.invoice_processing.invoice_parser import parse_invoice_text


# INVOICE_DIRECTORY = Path("data/invoices")


# def main():
#     pdf_files = sorted(INVOICE_DIRECTORY.glob("*.pdf"))

#     if not pdf_files:
#         print(f"No PDF files found in: {INVOICE_DIRECTORY.resolve()}")
#         return

#     print("\n========== Stage 8B Invoice Parser Test ==========")
#     print(f"Invoice folder: {INVOICE_DIRECTORY.resolve()}")
#     print(f"PDF files found: {len(pdf_files)}")

#     for pdf_file in pdf_files:
#         print("\n" + "=" * 70)
#         print(f"Parsing PDF: {pdf_file.name}")
#         print("=" * 70)

#         try:
#             loaded_invoice = load_pdf_invoice(str(pdf_file))

#             parsed_invoice = parse_invoice_text(
#                 raw_text=loaded_invoice["raw_text"],
#                 source_file=loaded_invoice["source_file"],
#             )

#             print("\n--- Parsed Invoice JSON ---")
#             print(json.dumps(parsed_invoice, indent=4))

#         except Exception as error:
#             print("\n--- Processing Error ---")
#             print(f"{type(error).__name__}: {error}")


# if __name__ == "__main__":
#     main()

import json
from pathlib import Path

from src.invoice_processing.invoice_loader import load_pdf_invoice
from src.invoice_processing.invoice_parser import parse_invoice_text


INVOICE_DIRECTORY = Path("data/invoices")


def main():
    pdf_files = sorted(INVOICE_DIRECTORY.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {INVOICE_DIRECTORY.resolve()}")
        return

    print("\n========== Stage 8B Invoice Parser Test ==========")
    print(f"Invoice folder: {INVOICE_DIRECTORY.resolve()}")
    print(f"PDF files found: {len(pdf_files)}")

    for pdf_file in pdf_files:
        print("\n" + "=" * 70)
        print(f"Parsing PDF: {pdf_file.name}")
        print("=" * 70)

        try:
            loaded_invoice = load_pdf_invoice(str(pdf_file))

            parsed_invoice = parse_invoice_text(
                raw_text=loaded_invoice["raw_text"],
                source_file=loaded_invoice["source_file"],
            )

            print("\n--- Parsed Invoice JSON ---")
            print(json.dumps(parsed_invoice, indent=4))

        except Exception as error:
            print("\n--- Processing Error ---")
            print(f"{type(error).__name__}: {error}")


if __name__ == "__main__":
    main()