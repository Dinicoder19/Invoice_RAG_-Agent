from src.rag_execution.ingestion.txt_file_loading import load_single_file
from src.rag_execution.ingestion.data_parsing import parse_documents
from src.rag_execution.ingestion.data_chunking import chunk_documents
from src.rag_execution.embedding.embedding_generation import (
    generate_document_embeddings,
    generate_query_embedding,
)


def main():
    txt_raw_docs = load_single_file("data/policies/ap_policy_master.txt")
    txt_parsed_docs = parse_documents(txt_raw_docs, file_type="txt")
    txt_chunked_docs = chunk_documents(txt_parsed_docs)

    csv_raw_docs = load_single_file("data/policies/ap_approval_matrix.csv")
    csv_parsed_docs = parse_documents(csv_raw_docs, file_type="csv")
    csv_chunked_docs = chunk_documents(csv_parsed_docs)

    all_chunked_docs = txt_chunked_docs + csv_chunked_docs

    document_vectors = generate_document_embeddings(all_chunked_docs)

    query = "What approval is required for a non-PO invoice?"
    query_vector = generate_query_embedding(query)

    print(f"TXT chunks: {len(txt_chunked_docs)}")
    print(f"CSV chunks: {len(csv_chunked_docs)}")
    print(f"Total chunks: {len(all_chunked_docs)}")
    print(f"Total document vectors: {len(document_vectors)}")
    print(f"Document vector dimension: {len(document_vectors[0])}")
    print(f"Query vector dimension: {len(query_vector)}")

    print("\nFirst chunk metadata:")
    print(all_chunked_docs[0].metadata)

    print("\nFirst vector preview:")
    print(document_vectors[0][:10])

    print("\nQuery vector preview:")
    print(query_vector[:10])


if __name__ == "__main__":
    main()