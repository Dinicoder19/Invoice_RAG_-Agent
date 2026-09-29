from src.rag_execution.retrieval.retriever import retrieve_documents


QUERIES = [
    (
        "PO invoice valid purchase order vendor match goods receipt "
        "within tolerance automated AP workflow"
    ),
    (
        "emergency non-PO invoice cost center manager approval"
    ),
    (
        "PO invoice missing vendor match goods receipt tolerance "
        "manual review exception"
    ),
]


def main():
    print("\n========== AP Policy Retrieval Test ==========")
    print(f"Queries to test: {len(QUERIES)}")

    for query_number, query in enumerate(QUERIES, start=1):
        print("\n" + "=" * 80)
        print(f"Query {query_number}: {query}")
        print("=" * 80)

        try:
            documents = retrieve_documents(query)

            print(f"\nRetrieved documents: {len(documents)}")

            if not documents:
                print("No policy documents were retrieved.")
                continue

            for index, document in enumerate(documents, start=1):
                print(f"\n--- Result {index} ---")

                print("\nPolicy Content:")
                print(document.page_content)

                print("\nMetadata:")
                print(document.metadata)

        except Exception as error:
            print("\n--- Retrieval Error ---")
            print(f"{type(error).__name__}: {error}")


if __name__ == "__main__":
    main()