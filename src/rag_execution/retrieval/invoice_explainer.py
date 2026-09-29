import json

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


MODEL_NAME = "llama3.2"


def _format_policy_evidence(policy_evidence: list[dict]) -> str:
    """
    Convert retrieved policy evidence into readable prompt context.
    """

    if not policy_evidence:
        return "No policy evidence was retrieved."

    sections = []

    for item in policy_evidence:
        source = item.get("source", "Unknown source")
        rank = item.get("rank", "Unknown")
        content = item.get("content", "")

        sections.append(
            f"Policy evidence {rank}\n"
            f"Source: {source}\n"
            f"Content:\n{content}"
        )

    return "\n\n---\n\n".join(sections)


def explain_invoice_decision(
    parsed_invoice: dict,
    validation_result: dict,
    workflow_result: dict,
    policy_evidence: list[dict],
) -> str:
    """
    Generate a concise explanation for the authoritative workflow result.

    The workflow route and status are authoritative. The nested classifier
    output is background only and must not override the workflow result.
    """

    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an Accounts Payable decision-explanation assistant.

Explain the authoritative workflow decision using only the supplied
invoice facts, validation result, workflow decision, and policy evidence.

Priority rules:
1. The authoritative outcome is workflow_route, decision_status,
   requires_human_review, and workflow_reason.
2. Start with the authoritative workflow_route and explain the
   authoritative workflow_reason.
3. The nested classification_result is background only. Do not present
   its predicted route or classification as the final result if it differs
   from workflow_route.
4. Do not invent, infer, or add missing fields, controls, policy rules,
   approval levels, amounts, or facts.
5. Mention missing PO-match controls only if they are explicitly listed
   in validation_result.missing_control_fields.
6. For an emergency non-PO invoice, explain that human approval is
   required because the authoritative route is Cost Center Manager Approval.
   Do not claim that PO controls are missing unless
   validation_result.missing_control_fields is non-empty.
7. Treat UNKNOWN values as requiring validation only when the supplied
   policy evidence and validation result explicitly apply them to the
   current invoice scenario.
8. Use only policy statements directly present in the supplied evidence.
9. Write one concise paragraph of 70 to 120 words.
10. Do not use Markdown headings, bullets, JSON, field names such as
    workflow_route or decision_status, or a preamble.

The deterministic workflow decision is authoritative.""",
            ),
            (
                "human",
                """Invoice facts:
{invoice_facts}

Validation result:
{validation_result}

Authoritative workflow decision:
{workflow_decision}

Retrieved AP policy evidence:
{policy_evidence}

Write the explanation now.""",
            ),
        ]
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "invoice_facts": json.dumps(parsed_invoice, indent=2),
            "validation_result": json.dumps(validation_result, indent=2),
            "workflow_decision": json.dumps(workflow_result, indent=2),
            "policy_evidence": _format_policy_evidence(policy_evidence),
        }
    )

    return response.content.strip()