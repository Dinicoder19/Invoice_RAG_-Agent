from src.rag_execution.ingestion.data_chunking import chunk_documents
from src.rag_execution.ingestion.data_parsing import parse_documents
from src.rag_execution.ingestion.txt_file_loading import load_single_file


POLICY_FILE = "data/policies/ap_policy_master.txt"


def main():
    raw_documents = load_single_file(POLICY_FILE)

    parsed_documents = parse_documents(
        raw_documents,
        file_type="txt",
    )

    chunked_documents = chunk_documents(parsed_documents)

    print("\n========== AP Policy Chunk Inspection ==========")
    print(f"Policy file: {POLICY_FILE}")
    print(f"Total chunks: {len(chunked_documents)}")

    for index, document in enumerate(chunked_documents, start=1):
        print("\n" + "=" * 80)
        print(f"Chunk {index}")
        print("=" * 80)

        print("\nContent:")
        print(document.page_content)

        print("\nMetadata:")
        print(document.metadata)


if __name__ == "__main__":
    main()