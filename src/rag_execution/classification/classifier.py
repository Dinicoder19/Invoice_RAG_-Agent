from dataclasses import asdict, dataclass


AUTO_ROUTE_CONFIDENCE_THRESHOLD = 0.90


@dataclass
class ClassificationResult:
    invoice_id: str
    predicted_classification: str
    predicted_route: str
    reason: str
    review_required: bool


def _normalize_value(value) -> str:
    """
    Convert a value into a trimmed uppercase string.
    """

    if value is None:
        return ""

    return str(value).strip().upper()


def _is_yes(value) -> bool:
    """
    Return True only when the value is Y.
    """

    return _normalize_value(value) == "Y"


def _is_no(value) -> bool:
    """
    Return True only when the value is N.

    Important:
    UNKNOWN is not treated as N.
    """

    return _normalize_value(value) == "N"


def _has_value(value) -> bool:
    """
    Return True only for meaningful values.

    Values such as None, empty text, NONE, N/A, NA, and UNKNOWN
    are treated as missing.
    """

    normalized_value = _normalize_value(value)

    return normalized_value not in {
        "",
        "NONE",
        "N/A",
        "NA",
        "UNKNOWN",
        "NULL",
    }


def _to_float(value) -> float:
    """
    Safely convert an amount or confidence score to float.
    """

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def classify_invoice(invoice: dict) -> dict:
    """
    Classify an invoice and determine its initial processing route.

    Stage 9 workflow validation can later override this route when:
    - essential validation fails,
    - required PO-match evidence is unavailable,
    - an emergency non-PO invoice needs manager approval,
    - external ERP / PO / goods-receipt verification is needed.
    """

    invoice_id = str(invoice.get("invoice_id", "")).strip()
    document_type = str(invoice.get("document_type", "")).strip()
    po_number = invoice.get("po_number")
    confidence_score = _to_float(invoice.get("confidence_score", 0))
    invoice_amount = _to_float(invoice.get("invoice_amount", 0))

    po_valid_flag = _is_yes(invoice.get("po_valid_flag"))
    vendor_match_flag = _is_yes(invoice.get("vendor_match_flag"))
    within_tolerance_flag = _is_yes(invoice.get("within_tolerance_flag"))
    goods_receipt_flag = _is_yes(invoice.get("goods_receipt_flag"))
    expense_permitted_without_po_flag = _is_yes(
        invoice.get("expense_permitted_without_po_flag")
    )
    utility_flag = _is_yes(invoice.get("utility_flag"))
    recurring_flag = _is_yes(invoice.get("recurring_flag"))
    duplicate_flag = _is_yes(invoice.get("duplicate_flag"))
    mandatory_fields_missing_flag = _is_yes(
        invoice.get("mandatory_fields_missing_flag")
    )
    supplier_valid_flag = _is_yes(invoice.get("supplier_valid_flag"))

    predicted_classification = "Exception Invoice"
    predicted_route = "Human Validation"
    reason = "Invoice did not match an automated classification rule."

    if document_type.lower() == "credit note" or invoice_amount < 0:
        predicted_classification = "Credit Note"
        predicted_route = "Credit Note Processing"
        reason = (
            "Document type is Credit Note or invoice amount is negative, "
            "so it should be processed as a vendor credit."
        )

    elif duplicate_flag:
        predicted_classification = "Duplicate-Suspected Invoice"
        predicted_route = "Human Validation"
        reason = (
            "Duplicate flag is set, so the invoice must be held for human review."
        )

    elif mandatory_fields_missing_flag:
        predicted_classification = "Exception Invoice"
        predicted_route = "Human Validation"
        reason = (
            "Mandatory invoice fields are missing, so the invoice cannot be "
            "processed automatically."
        )

    elif _has_value(po_number) and _is_no(
        invoice.get("within_tolerance_flag")
    ):
        predicted_classification = "Exception Invoice"
        predicted_route = "Human Validation"
        reason = (
            "Invoice is PO-backed and exceeds tolerance, so it requires "
            "manual review."
        )

    elif (
        _has_value(po_number)
        and po_valid_flag
        and vendor_match_flag
        and within_tolerance_flag
        and goods_receipt_flag
        and not duplicate_flag
        and not mandatory_fields_missing_flag
        and supplier_valid_flag
    ):
        predicted_classification = "PO Invoice"
        predicted_route = "Automated AP Workflow / Applicable Approval"
        reason = (
            "PO exists and PO, vendor, tolerance, goods receipt, and supplier "
            "checks all passed."
        )

    elif (
        not _has_value(po_number)
        and utility_flag
        and not duplicate_flag
        and not mandatory_fields_missing_flag
        and supplier_valid_flag
    ):
        predicted_classification = "Utility Invoice"
        predicted_route = "Automated AP Workflow / Applicable Approval"
        reason = (
            "No PO is present, but the invoice is marked as a utility invoice "
            "and passed validation checks."
        )

    elif (
        not _has_value(po_number)
        and recurring_flag
        and not duplicate_flag
        and not mandatory_fields_missing_flag
        and supplier_valid_flag
    ):
        predicted_classification = "Recurring Invoice"
        predicted_route = "Automated AP Workflow / Applicable Approval"
        reason = (
            "No PO is present, but the invoice is marked as recurring and "
            "passed validation checks."
        )

    elif (
        not _has_value(po_number)
        and expense_permitted_without_po_flag
        and not duplicate_flag
        and not mandatory_fields_missing_flag
        and supplier_valid_flag
    ):
        predicted_classification = "Non-PO Invoice"
        predicted_route = "Automated AP Workflow / Applicable Approval"
        reason = (
            "No PO is present, expense without PO is permitted, and the "
            "invoice passed validation checks."
        )

    if (
        predicted_route == "Automated AP Workflow / Applicable Approval"
        and confidence_score < AUTO_ROUTE_CONFIDENCE_THRESHOLD
    ):
        predicted_route = "Human Validation"
        reason += (
            f" Confidence score {confidence_score:.2f} is below the "
            f"auto-route threshold of {AUTO_ROUTE_CONFIDENCE_THRESHOLD:.2f}."
        )

    result = ClassificationResult(
        invoice_id=invoice_id,
        predicted_classification=predicted_classification,
        predicted_route=predicted_route,
        reason=reason,
        review_required=(predicted_route == "Human Validation"),
    )

    return asdict(result)