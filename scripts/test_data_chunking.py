from src.rag_execution.ingestion.txt_file_loading import load_single_file
from src.rag_execution.ingestion.data_parsing import parse_documents
from src.rag_execution.ingestion.data_chunking import chunk_documents


def test_chunking(file_path: str, file_type: str):
    print(f"\n{'=' * 60}")
    print(f"Testing chunking for: {file_path}")
    print(f"{'=' * 60}")

    raw_docs = load_single_file(file_path)
    parsed_docs = parse_documents(raw_docs, file_type=file_type)
    chunked_docs = chunk_documents(parsed_docs)

    print(f"Raw documents count: {len(raw_docs)}")
    print(f"Parsed documents count: {len(parsed_docs)}")
    print(f"Chunked documents count: {len(chunked_docs)}")

    if chunked_docs:
        print("\n--- First Chunk Content (first 400 chars) ---\n")
        print(chunked_docs[0].page_content[:400])

        print("\n--- First Chunk Metadata ---\n")
        print(chunked_docs[0].metadata)


def main():
    test_chunking("data/policies/ap_policy_master.txt", "txt")
    test_chunking("data/policies/ap_approval_matrix.csv", "csv")


if __name__ == "__main__":
    main()