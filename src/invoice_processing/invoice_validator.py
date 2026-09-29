from typing import Any


REQUIRED_FIELDS = [
    "invoice_number",
    "invoice_date",
    "vendor_name",
    "currency",
    "invoice_amount",
]


def _is_unknown(value: Any) -> bool:
    return value is None or value == "" or value == "UNKNOWN"


def validate_invoice(parsed_invoice: dict[str, Any]) -> dict[str, Any]:
    """
    Validate the normalized invoice data before classification.

    This function does not invent missing invoice facts. It reports:
    - hard validation errors: invoice cannot proceed
    - warnings: invoice may proceed but needs review or external matching
    - control-data gaps: fields needed for a PO automation decision
    """

    errors = []
    warnings = []
    missing_required_fields = []
    missing_control_fields = []

    for field_name in REQUIRED_FIELDS:
        value = parsed_invoice.get(field_name)

        if _is_unknown(value):
            missing_required_fields.append(field_name)
            errors.append(f"Missing required field: {field_name}")

    invoice_amount = parsed_invoice.get("invoice_amount")

    if invoice_amount is not None:
        if not isinstance(invoice_amount, (int, float)):
            errors.append("Invoice amount must be numeric.")

        elif invoice_amount <= 0:
            errors.append("Invoice amount must be greater than zero.")

    tax_amount = parsed_invoice.get("tax_amount")

    if tax_amount is not None:
        if not isinstance(tax_amount, (int, float)):
            warnings.append("Tax amount is not numeric.")

        elif tax_amount < 0:
            warnings.append("Tax amount cannot be negative.")

    document_type = parsed_invoice.get("document_type")
    po_number = parsed_invoice.get("po_number")
    emergency_flag = parsed_invoice.get("emergency_flag", "N")

    is_po_invoice = document_type == "PO Invoice" or po_number is not None
    is_emergency_non_po = (
        document_type == "Non-PO Invoice"
        and emergency_flag == "Y"
    )

    if is_po_invoice:
        po_control_fields = [
            "po_valid_flag",
            "vendor_match_flag",
            "within_tolerance_flag",
            "goods_receipt_flag",
            "supplier_valid_flag",
        ]

        for field_name in po_control_fields:
            if _is_unknown(parsed_invoice.get(field_name)):
                missing_control_fields.append(field_name)

        if missing_control_fields:
            warnings.append(
                "PO match controls are incomplete: "
                + ", ".join(missing_control_fields)
            )

        if parsed_invoice.get("po_valid_flag") == "N":
            errors.append("PO validation failed.")

        if parsed_invoice.get("vendor_match_flag") == "N":
            errors.append("Vendor does not match the PO.")

        if parsed_invoice.get("within_tolerance_flag") == "N":
            errors.append("Invoice amount is outside PO tolerance.")

        if parsed_invoice.get("goods_receipt_flag") == "N":
            errors.append("Goods receipt is not available.")

        if parsed_invoice.get("supplier_valid_flag") == "N":
            errors.append("Supplier verification failed.")

    if is_emergency_non_po:
        if _is_unknown(parsed_invoice.get("requested_by")):
            errors.append(
                "Emergency non-PO invoice requires a requester."
            )

        if _is_unknown(parsed_invoice.get("cost_center")):
            errors.append(
                "Emergency non-PO invoice requires a cost center."
            )

    if document_type == "Non-PO Invoice" and emergency_flag == "N":
        warnings.append(
            "Non-PO invoice is not marked as an emergency. "
            "Policy approval review is required."
        )

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "missing_required_fields": missing_required_fields,
        "missing_control_fields": missing_control_fields,
        "is_po_invoice": is_po_invoice,
        "is_emergency_non_po": is_emergency_non_po,
        "requires_human_review": (
            len(errors) > 0
            or len(missing_control_fields) > 0
            or (
                document_type == "Non-PO Invoice"
                and emergency_flag != "Y"
            )
        ),
    }