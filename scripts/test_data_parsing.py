from src.rag_execution.ingestion.txt_file_loading import load_single_file
from src.rag_execution.ingestion.data_parsing import parse_documents


def test_parsing(file_path: str, file_type: str):
    print(f"\n{'=' * 50}")
    print(f"Testing parsing for: {file_path}")
    print(f"{'=' * 50}")

    docs = load_single_file(file_path)
    parsed_docs = parse_documents(docs, file_type=file_type)

    print(f"Raw documents count: {len(docs)}")
    print(f"Parsed documents count: {len(parsed_docs)}")

    if parsed_docs:
        print("\n--- Parsed Content (first 1000 chars) ---\n")
        print(parsed_docs[0].page_content[:1000])

        print("\n--- Parsed Metadata ---\n")
        print(parsed_docs[0].metadata)


def main():
    test_parsing("data/policies/ap_policy_master.txt", "txt")
    test_parsing("data/policies/ap_approval_matrix.csv", "csv")


if __name__ == "__main__":
    main()