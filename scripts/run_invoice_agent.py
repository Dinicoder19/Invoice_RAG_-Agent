import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from src.agent.invoice_agent import InvoiceAgent


def configure_logging():
    """
    Configure clear console logging for agent execution.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def build_argument_parser() -> argparse.ArgumentParser:
    """
    Create command-line arguments for single-file or folder processing.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Run the AP Invoice Agent on one PDF file or all PDFs "
            "inside a directory."
        )
    )

    parser.add_argument(
        "input_path",
        help="Path to one PDF invoice or a directory containing PDF invoices.",
    )

    parser.add_argument(
        "--output-dir",
        default="output/agent_results",
        help=(
            "Directory where JSON decision artifacts are saved. "
            "Default: output/agent_results"
        ),
    )

    return parser


def get_pdf_files(input_path: Path) -> list[Path]:
    """
    Return one PDF when input_path is a PDF, or all PDFs when it is a folder.
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input path does not exist: {input_path.resolve()}"
        )

    if input_path.is_file():
        if input_path.suffix.lower() != ".pdf":
            raise ValueError(
                "Input file must be a PDF invoice."
            )

        return [input_path]

    return sorted(input_path.glob("*.pdf"))


def get_output_file_path(
    invoice_result: dict,
    source_pdf: Path,
    output_directory: Path,
) -> Path:
    """
    Generate one readable JSON artifact filename per invoice.
    """

    invoice_number = invoice_result["invoice"].get(
        "invoice_number"
    ) or source_pdf.stem

    safe_invoice_number = "".join(
        character
        if character.isalnum() or character in {"-", "_"}
        else "_"
        for character in str(invoice_number)
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return output_directory / (
        f"{safe_invoice_number}_{timestamp}_decision.json"
    )


def save_result(
    invoice_result: dict,
    source_pdf: Path,
    output_directory: Path,
) -> Path:
    """
    Write one complete agent decision package as formatted JSON.
    """

    output_file = get_output_file_path(
        invoice_result,
        source_pdf,
        output_directory,
    )

    output_file.write_text(
        json.dumps(invoice_result, indent=4),
        encoding="utf-8",
    )

    return output_file


def print_summary(
    result: dict,
    source_pdf: Path,
    output_file: Path,
):
    """
    Print a compact terminal summary while preserving full output in JSON.
    """

    invoice = result["invoice"]
    decision = result["decision"]

    print("\n" + "=" * 80)
    print(f"Invoice file: {source_pdf.name}")
    print(f"Invoice number: {invoice.get('invoice_number')}")
    print(f"Vendor: {invoice.get('vendor_name')}")
    print(f"Amount: {invoice.get('invoice_amount')} {invoice.get('currency')}")
    print(f"Classification: {decision['classification_result']['predicted_classification']}")
    print(f"Workflow route: {decision['workflow_route']}")
    print(f"Decision status: {decision['decision_status']}")
    print(f"Human review required: {decision['requires_human_review']}")
    print(f"Saved result: {output_file}")
    print("\nAI explanation:")
    print(result["ai_explanation"])
    print("=" * 80)


def main():
    configure_logging()

    parser = build_argument_parser()
    arguments = parser.parse_args()

    input_path = Path(arguments.input_path)
    output_directory = Path(arguments.output_dir)

    output_directory.mkdir(parents=True, exist_ok=True)

    try:
        pdf_files = get_pdf_files(input_path)
    except (FileNotFoundError, ValueError) as error:
        logging.error(str(error))
        return

    if not pdf_files:
        logging.warning(
            "No PDF invoices found in: %s",
            input_path.resolve(),
        )
        return

    logging.info(
        "Starting AP Invoice Agent for %s PDF file(s).",
        len(pdf_files),
    )

    agent = InvoiceAgent()

    successful_results = 0
    failed_results = 0

    for pdf_file in pdf_files:
        try:
            logging.info("Processing: %s", pdf_file.name)

            result = agent.process_invoice(pdf_file)

            output_file = save_result(
                result,
                pdf_file,
                output_directory,
            )

            print_summary(
                result,
                pdf_file,
                output_file,
            )

            successful_results += 1

        except Exception as error:
            failed_results += 1

            logging.exception(
                "Failed to process %s: %s",
                pdf_file.name,
                error,
            )

    logging.info(
        "Agent run finished. Successful: %s | Failed: %s",
        successful_results,
        failed_results,
    )


if __name__ == "__main__":
    main()