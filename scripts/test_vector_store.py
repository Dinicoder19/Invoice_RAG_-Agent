from src.rag_execution.ingestion.data_chunking import chunk_documents
from src.rag_execution.ingestion.data_parsing import parse_documents
from src.rag_execution.ingestion.txt_file_loading import load_single_file
from src.rag_execution.vectorstore.chroma_store import rebuild_vector_store


def build_chunks():
    """
    Load, parse, and chunk all AP policy source files.
    """

    txt_raw_docs = load_single_file("data/policies/ap_policy_master.txt")
    txt_parsed_docs = parse_documents(txt_raw_docs, file_type="txt")
    txt_chunked_docs = chunk_documents(txt_parsed_docs)

    csv_raw_docs = load_single_file("data/policies/ap_approval_matrix.csv")
    csv_parsed_docs = parse_documents(csv_raw_docs, file_type="csv")
    csv_chunked_docs = chunk_documents(csv_parsed_docs)

    return txt_chunked_docs + csv_chunked_docs


def main():
    print("\n========== Rebuilding AP Policy Vector Store ==========")

    chunked_docs = build_chunks()

    print(f"Total policy chunks prepared: {len(chunked_docs)}")

    vector_store = rebuild_vector_store(chunked_docs)

    print("\n--- Fresh Similarity Search Test ---")

    query = "emergency non-PO invoice cost center manager approval"

    results = vector_store.similarity_search(query, k=3)

    print(f"Query: {query}")
    print(f"Retrieved results: {len(results)}")

    for index, document in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")

        print("\nContent:")
        print(document.page_content)

        print("\nMetadata:")
        print(document.metadata)


if __name__ == "__main__":
    main()