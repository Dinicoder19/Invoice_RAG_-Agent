import re
from langchain_core.documents import Document


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_documents(documents, file_type: str):
    parsed_docs = []

    for doc in documents:
        cleaned_content = clean_text(doc.page_content)

        updated_metadata = dict(doc.metadata)
        updated_metadata["file_type"] = file_type
        updated_metadata["parsing_status"] = "cleaned"

        parsed_doc = Document(
            page_content=cleaned_content,
            metadata=updated_metadata
        )
        parsed_docs.append(parsed_doc)

    return parsed_docs