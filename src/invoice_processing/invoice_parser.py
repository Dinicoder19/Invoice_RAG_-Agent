import re
from datetime import datetime
from typing import Any


DEFAULT_FLAGS = {
    "po_valid_flag": "UNKNOWN",
    "vendor_match_flag": "UNKNOWN",
    "within_tolerance_flag": "UNKNOWN",
    "goods_receipt_flag": "UNKNOWN",
    "expense_permitted_without_po_flag": "UNKNOWN",
    "utility_flag": "UNKNOWN",
    "recurring_flag": "UNKNOWN",
    "supplier_valid_flag": "UNKNOWN",
}


def _find_first(
    patterns: list[str],
    text: str,
    flags: int = re.IGNORECASE,
) -> str | None:
    """
    Return the first captured group from the first matching regex pattern.
    """

    for pattern in patterns:
        match = re.search(pattern, text, flags)

        if match:
            return match.group(1).strip()

    return None


def _parse_amount(value: str | None) -> float | None:
    """
    Convert values such as '$2,050.00' or '750.00' to float.
    """

    if not value:
        return None

    cleaned_value = value.replace("$", "").replace(",", "").strip()

    try:
        return float(cleaned_value)
    except ValueError:
        return None


def _parse_date(value: str | None) -> str | None:
    """
    Convert supported invoice date formats to ISO format: YYYY-MM-DD.

    Example:
        'Sept 15, 2026' -> '2026-09-15'
        'Sep 23, 2026'  -> '2026-09-23'
        '2026-09-22'    -> '2026-09-22'
    """

    if not value:
        return None

    cleaned_value = re.sub(r"\s+", " ", value).strip()

    month_replacements = {
        "Sept": "Sep",
    }

    for old_month, new_month in month_replacements.items():
        cleaned_value = re.sub(
            rf"\b{old_month}\b",
            new_month,
            cleaned_value,
            flags=re.IGNORECASE,
        )

    supported_formats = [
        "%b %d, %Y",
        "%B %d, %Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]

    for date_format in supported_formats:
        try:
            return datetime.strptime(
                cleaned_value,
                date_format,
            ).date().isoformat()
        except ValueError:
            continue

    return cleaned_value


def _normalize_flag(
    value: str | None,
    default: str = "UNKNOWN",
) -> str:
    """
    Normalize Y/Yes/True and N/No/False values.
    """

    if not value:
        return default

    cleaned_value = value.strip().upper()

    if cleaned_value in {"Y", "YES", "TRUE"}:
        return "Y"

    if cleaned_value in {"N", "NO", "FALSE"}:
        return "N"

    return default


def _extract_vendor_name(text: str) -> str | None:
    """
    Extract vendor name from the supported invoice layouts.
    """

    supplier_name = _find_first(
        [
            r"SUPPLIER:\s*\n([^\n]+)",
        ],
        text,
    )

    if supplier_name:
        return supplier_name

    emergency_vendor = _find_first(
        [
            r"URGENT:\s*NON-PO INVOICE[^\n]*\n([^\n]+)",
        ],
        text,
    )

    if emergency_vendor:
        return emergency_vendor

    po_vendor = _find_first(
        [
            r"^([^\n]+)\n\d+\s+[^\n]+\n[A-Za-z .]+,\s*[A-Z]{2}\s+\d{5}\nINVOICE",
        ],
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    return po_vendor


def _extract_po_number(text: str) -> str | None:
    """
    Extract and normalize a PO number.
    Returns None when the invoice explicitly states NONE, N/A, or similar.
    """

    po_value = _find_first(
        [
            r"PO Number:\s*([^\n]+)",
        ],
        text,
    )

    if not po_value:
        return None

    if re.search(
        r"\b(NONE|N/A|NA|NOT APPLICABLE)\b",
        po_value,
        re.IGNORECASE,
    ):
        return None

    po_match = re.search(r"\bPO[-\s]?\d+\b", po_value, re.IGNORECASE)

    if po_match:
        return po_match.group(0).upper().replace(" ", "-")

    return po_value.strip()


def _extract_document_type(
    text: str,
    po_number: str | None,
) -> str:
    """
    Determine a document category using explicit labels first,
    then use the presence of a PO number as fallback logic.
    """

    explicit_type = _find_first(
        [
            r"Document Type:\s*([^\n]+)",
        ],
        text,
    )

    if explicit_type:
        return explicit_type

    if re.search(r"NON-PO\s+INVOICE", text, re.IGNORECASE):
        return "Non-PO Invoice"

    if po_number:
        return "PO Invoice"

    return "Invoice"


def _extract_currency(text: str) -> str | None:
    """
    Extract an explicit currency code where present.
    Otherwise, infer USD only when dollar symbols occur in the invoice.

    The function deliberately does not read arbitrary text after
    'Balance Due', preventing errors such as extracting 'Pay' from
    'Payment Terms'.
    """

    currency = _find_first(
        [
            r"Total Amount:\s*\$?\s*[\d,]+\.\d{2}\s*\b([A-Z]{3})\b",
            r"TOTAL DUE\s*\(\s*([A-Z]{3})\s*\)",
            r"\bCurrency:\s*([A-Z]{3})\b",
        ],
        text,
    )

    if currency:
        return currency.upper()

    if "$" in text:
        return "USD"

    return None


def parse_invoice_text(
    raw_text: str,
    source_file: str | None = None,
) -> dict[str, Any]:
    """
    Convert raw PDF invoice text into normalized structured invoice data.

    Missing factual invoice fields are returned as None.
    Missing AP control fields are returned as 'UNKNOWN'.
    """

    invoice_number = _find_first(
        [
            r"Invoice\s*#:\s*([^\n]+)",
            r"Invoice\s+No:\s*([^\n]+)",
            r"Invoice\s+([A-Z]{2,}[-\d]+)\s*$",
        ],
        raw_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    invoice_date_text = _find_first(
        [
            r"^Date:\s*([^\n]+)",
        ],
        raw_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    invoice_date = _parse_date(invoice_date_text)

    po_number = _extract_po_number(raw_text)

    tax_amount = _parse_amount(
        _find_first(
            [
                r"Tax\s*\([^)]*\):\s*\$?\s*([\d,]+\.\d{2})",
                r"Tax:\s*\$?\s*([\d,]+\.\d{2})",
            ],
            raw_text,
        )
    )

    invoice_amount = _parse_amount(
        _find_first(
            [
                r"Total Amount:\s*\$?\s*([\d,]+\.\d{2})\s*(?:USD)?",
                r"TOTAL DUE\s*\(USD\):\s*\$?\s*([\d,]+\.\d{2})",
                r"Balance Due:\s*\$?\s*([\d,]+\.\d{2})",
                r"Total Due:\s*\$?\s*([\d,]+\.\d{2})",
            ],
            raw_text,
        )
    )

    confidence_score = _parse_amount(
        _find_first(
            [
                r"Confidence Score:\s*([01](?:\.\d+)?)",
            ],
            raw_text,
        )
    )

    requested_by = _find_first(
        [
            r"Requested By:\s*([^\n(]+)",
        ],
        raw_text,
    )

    cost_center = _find_first(
        [
            r"Cost Center\s*(\d+)",
        ],
        raw_text,
    )

    parsed_invoice = {
        "source_file": source_file,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "vendor_name": _extract_vendor_name(raw_text),
        "po_number": po_number,
        "currency": _extract_currency(raw_text),
        "invoice_amount": invoice_amount,
        "tax_amount": tax_amount,
        "document_type": _extract_document_type(raw_text, po_number),
        "emergency_flag": (
            "Y"
            if re.search(
                r"\bEMERGENCY\b|\bURGENT\b",
                raw_text,
                re.IGNORECASE,
            )
            else "N"
        ),
        "requested_by": requested_by,
        "cost_center": cost_center,
        "po_valid_flag": _normalize_flag(
            _find_first(
                [
                    r"PO Valid:\s*([YN])",
                ],
                raw_text,
            )
        ),
        "vendor_match_flag": _normalize_flag(
            _find_first(
                [
                    r"Vendor Match:\s*([YN])",
                ],
                raw_text,
            )
        ),
        "within_tolerance_flag": _normalize_flag(
            _find_first(
                [
                    r"Within Tolerance:\s*([YN])",
                ],
                raw_text,
            )
        ),
        "goods_receipt_flag": _normalize_flag(
            _find_first(
                [
                    r"Goods Receipt:\s*([YN])",
                ],
                raw_text,
            )
        ),
        "expense_permitted_without_po_flag": _normalize_flag(
            _find_first(
                [
                    r"Expense PO:\s*([YN])",
                ],
                raw_text,
            )
        ),
        "utility_flag": _normalize_flag(
            _find_first(
                [
                    r"Utility:\s*([YN])",
                ],
                raw_text,
            )
        ),
        "recurring_flag": _normalize_flag(
            _find_first(
                [
                    r"Recurring:\s*([YN])",
                ],
                raw_text,
            )
        ),
        "supplier_valid_flag": _normalize_flag(
            _find_first(
                [
                    r"Supplier Verified:\s*([YN])",
                ],
                raw_text,
            )
        ),
        "confidence_score": confidence_score,
    }

    for field_name, default_value in DEFAULT_FLAGS.items():
        if parsed_invoice.get(field_name) is None:
            parsed_invoice[field_name] = default_value

    return parsed_invoice