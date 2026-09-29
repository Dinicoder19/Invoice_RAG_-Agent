import csv
from collections import Counter

from src.rag_execution.classification.classifier import classify_invoice


CSV_FILE_PATH = "data/evaluation/invoices_master_50.csv"


def load_invoices(csv_file_path: str) -> list[dict]:
    with open(csv_file_path, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def main():
    invoices = load_invoices(CSV_FILE_PATH)

    total_invoices = len(invoices)
    classification_matches = 0
    route_matches = 0
    full_matches = 0

    predicted_class_counter = Counter()
    predicted_route_counter = Counter()

    mismatches = []

    for invoice in invoices:
        result = classify_invoice(invoice)

        expected_classification = str(
            invoice.get("expected_classification", "")
        ).strip()
        expected_route = str(invoice.get("expected_route", "")).strip()

        predicted_classification = result["predicted_classification"]
        predicted_route = result["predicted_route"]

        predicted_class_counter[predicted_classification] += 1
        predicted_route_counter[predicted_route] += 1

        class_match = predicted_classification == expected_classification
        route_match = predicted_route == expected_route

        if class_match:
            classification_matches += 1

        if route_match:
            route_matches += 1

        if class_match and route_match:
            full_matches += 1
        else:
            mismatches.append(
                {
                    "invoice_id": invoice.get("invoice_id", "").strip(),
                    "expected_classification": expected_classification,
                    "predicted_classification": predicted_classification,
                    "expected_route": expected_route,
                    "predicted_route": predicted_route,
                    "reason": result["reason"],
                }
            )

    classification_accuracy = (
        classification_matches / total_invoices * 100 if total_invoices else 0
    )
    route_accuracy = route_matches / total_invoices * 100 if total_invoices else 0
    overall_accuracy = full_matches / total_invoices * 100 if total_invoices else 0

    print("\n========== Stage 7 Batch Test Results ==========")
    print(f"Total invoices tested: {total_invoices}")
    print(
        f"Classification accuracy: {classification_matches}/{total_invoices} "
        f"({classification_accuracy:.2f}%)"
    )
    print(
        f"Route accuracy: {route_matches}/{total_invoices} "
        f"({route_accuracy:.2f}%)"
    )
    print(
        f"Overall exact match accuracy: {full_matches}/{total_invoices} "
        f"({overall_accuracy:.2f}%)"
    )

    print("\n--- Predicted Classification Counts ---")
    for label, count in predicted_class_counter.items():
        print(f"{label}: {count}")

    print("\n--- Predicted Route Counts ---")
    for route, count in predicted_route_counter.items():
        print(f"{route}: {count}")

    print("\n--- Mismatches ---")
    if not mismatches:
        print("No mismatches found. All invoices matched expected results.")
    else:
        for mismatch in mismatches:
            print("\n-----------------------------")
            print(f"Invoice ID: {mismatch['invoice_id']}")
            print(
                f"Expected Classification: "
                f"{mismatch['expected_classification']}"
            )
            print(
                f"Predicted Classification: "
                f"{mismatch['predicted_classification']}"
            )
            print(f"Expected Route: {mismatch['expected_route']}")
            print(f"Predicted Route: {mismatch['predicted_route']}")
            print(f"Reason: {mismatch['reason']}")


if __name__ == "__main__":
    main()