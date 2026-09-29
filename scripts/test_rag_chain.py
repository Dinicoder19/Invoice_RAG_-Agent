from src.rag_execution.retrieval.rag_chain import get_rag_chain


def main():
    rag_chain = get_rag_chain()

    query = "What approval is required for a non-PO invoice?"

    response = rag_chain.invoke(
        {
            "input": query
        }
    )

    print("\n--- Question ---")
    print(query)

    print("\n--- Answer ---")
    print(response["answer"])

    print("\n--- Retrieved Sources ---")
    for index, document in enumerate(
        response["context"],
        start=1,
    ):
        print(f"\nSource {index}:")
        print(document.metadata)


if __name__ == "__main__":
    main()