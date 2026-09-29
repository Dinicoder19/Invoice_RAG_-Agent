from datetime import datetime
from pathlib import Path

from src.rag_execution.classification.classifier import classify_invoice
from src.invoice_processing.invoice_loader import load_pdf_invoice
from src.invoice_processing.invoice_parser import parse_invoice_text
from src.invoice_processing.invoice_validator import validate_invoice
from src.rag_execution.retrieval.invoice_explainer import (
    explain_invoice_decision,
)
from src.rag_execution.retrieval.retriever import retrieve_documents


def prepare_classifier_input(
    parsed_invoice: dict,
    validation_result: dict,
) -> dict:
    """
    Adapt parsed invoice data to the existing classifier schema.
    """

    classifier_input = parsed_invoice.copy()

    classifier_input["invoice_id"] = parsed_invoice.get(
        "invoice_number",
        "",
    )

    classifier_input["mandatory_fields_missing_flag"] = (
        "Y"
        if validation_result["missing_required_fields"]
        else "N"
    )

    # ERP/history-backed duplicate checking is not implemented yet.
    classifier_input["duplicate_flag"] = "N"

    return classifier_input


def build_policy_query(
    parsed_invoice: dict,
    validation_result: dict,
) -> str:
    """
    Build a focused AP-policy query for the invoice scenario.
    """

    if validation_result["is_emergency_non_po"]:
        return (
            "Emergency Non-PO Invoice emergency_flag Y po_number blank "
            "requester cost center vendor invoice amount "
            "Cost Center Manager Approval"
        )

    if (
        validation_result["is_po_invoice"]
        and validation_result["missing_control_fields"]
    ):
        return (
            "PO Match Evidence Policy PO Invoice "
            "po_number present control fields UNKNOWN or missing "
            "po_valid_flag vendor_match_flag within_tolerance_flag "
            "goods_receipt_flag supplier_valid_flag "
            "AP Validation Queue"
        )

    if validation_result["is_po_invoice"]:
        return (
            "PO Invoice po_number present "
            "po_valid_flag Y vendor_match_flag Y "
            "within_tolerance_flag Y goods_receipt_flag Y "
            "supplier_valid_flag Y automated AP workflow"
        )

    return (
        "Accounts Payable policy invoice review "
        f"document type {parsed_invoice.get('document_type')}"
    )


def retrieve_policy_evidence(
    policy_query: str,
    parsed_invoice: dict,
    validation_result: dict,
) -> list[dict]:
    """
    Retrieve policy candidates and retain scenario-relevant evidence.

    This function filters policy evidence only. It never changes the
    deterministic classification or workflow decision.
    """

    documents = retrieve_documents(policy_query)

    if validation_result["is_emergency_non_po"]:
        required_keywords = [
            "emergency non-po",
            "cost center manager",
            "emergency justification",
            "responsible cost center",
        ]
    elif (
        validation_result["is_po_invoice"]
        and validation_result["missing_control_fields"]
    ):
        required_keywords = [
            "po match evidence",
            "ap validation queue",
            "unknown control",
            "required po-match controls",
        ]
    elif validation_result["is_po_invoice"]:
        required_keywords = [
            "po invoice",
            "po_valid_flag",
            "vendor_match_flag",
            "within_tolerance_flag",
            "goods_receipt_flag",
        ]
    else:
        required_keywords = [
            "accounts payable",
            "invoice",
        ]

    relevant_documents = []

    for document in documents:
        content_lower = document.page_content.lower()

        if any(keyword in content_lower for keyword in required_keywords):
            relevant_documents.append(document)

    if not relevant_documents:
        relevant_documents = documents

    policy_evidence = []

    for rank, document in enumerate(relevant_documents[:2], start=1):
        policy_evidence.append(
            {
                "rank": rank,
                "source": document.metadata.get(
                    "source",
                    "Unknown source",
                ),
                "metadata": document.metadata,
                "content": document.page_content,
            }
        )

    return policy_evidence


def determine_workflow(
    parsed_invoice: dict,
    validation_result: dict,
) -> dict:
    """
    Apply deterministic AP workflow controls around the classifier.
    """

    classifier_input = prepare_classifier_input(
        parsed_invoice,
        validation_result,
    )

    classification_result = classify_invoice(classifier_input)

    if validation_result["errors"]:
        return {
            "classification_result": classification_result,
            "workflow_route": "AP Exception Review",
            "decision_status": "BLOCKED",
            "requires_human_review": True,
            "workflow_reason": (
                "The invoice has validation errors and cannot proceed "
                "to automated AP processing."
            ),
        }

    if validation_result["is_emergency_non_po"]:
        return {
            "classification_result": classification_result,
            "workflow_route": "Cost Center Manager Approval",
            "decision_status": "PENDING_APPROVAL",
            "requires_human_review": True,
            "workflow_reason": (
                "The invoice is an emergency non-PO invoice. The requester "
                "and cost center are present, but manager approval is "
                "required before AP processing."
            ),
        }

    if validation_result["is_po_invoice"]:
        if validation_result["missing_control_fields"]:
            return {
                "classification_result": classification_result,
                "workflow_route": "AP Validation Queue",
                "decision_status": "PENDING_VALIDATION",
                "requires_human_review": True,
                "workflow_reason": (
                    "The invoice has a PO, but required PO-match control "
                    "data is unavailable. Validate against ERP, PO, and "
                    "goods-receipt records."
                ),
            }

        if validation_result["is_valid"]:
            return {
                "classification_result": classification_result,
                "workflow_route": (
                    "Automated AP Workflow / Applicable Approval"
                ),
                "decision_status": "READY_FOR_AP_PROCESSING",
                "requires_human_review": False,
                "workflow_reason": (
                    "Required PO validation, vendor matching, tolerance, "
                    "goods receipt, and supplier verification controls passed."
                ),
            }

    return {
        "classification_result": classification_result,
        "workflow_route": "AP Review Queue",
        "decision_status": "PENDING_REVIEW",
        "requires_human_review": True,
        "workflow_reason": (
            "The invoice does not meet a fully automated workflow condition."
        ),
    }


class InvoiceAgent:
    """
    End-to-end AP invoice policy agent.

    It loads an invoice, extracts structured facts, validates controls,
    retrieves AP policy evidence, determines the workflow route, and
    creates an LLM policy-grounded explanation.
    """

    def process_invoice(
        self,
        pdf_path: str | Path,
    ) -> dict:
        """
        Process one PDF invoice and return a complete decision package.
        """

        pdf_path = Path(pdf_path)

        loaded_invoice = load_pdf_invoice(str(pdf_path))

        parsed_invoice = parse_invoice_text(
            raw_text=loaded_invoice["raw_text"],
            source_file=loaded_invoice["source_file"],
        )

        validation_result = validate_invoice(parsed_invoice)

        policy_query = build_policy_query(
            parsed_invoice,
            validation_result,
        )

        policy_evidence = retrieve_policy_evidence(
            policy_query,
            parsed_invoice,
            validation_result,
        )

        workflow_result = determine_workflow(
            parsed_invoice,
            validation_result,
        )

        ai_explanation = explain_invoice_decision(
            parsed_invoice=parsed_invoice,
            validation_result=validation_result,
            workflow_result=workflow_result,
            policy_evidence=policy_evidence,
        )

        return {
            "processed_at": datetime.now().isoformat(timespec="seconds"),
            "invoice": parsed_invoice,
            "validation": validation_result,
            "policy_query": policy_query,
            "policy_evidence": policy_evidence,
            "decision": workflow_result,
            "ai_explanation": ai_explanation,
        }