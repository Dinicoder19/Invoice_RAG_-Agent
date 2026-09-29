from src.rag_execution.vectorstore.chroma_store import (
    load_vector_store,
)


def get_retriever():
    vector_store = load_vector_store()

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )

    return retriever


def retrieve_documents(query: str):
    retriever = get_retriever()
    documents = retriever.invoke(query)

    return documents