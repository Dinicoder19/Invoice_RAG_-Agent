from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DIRECTORY = Path("chroma_db")
COLLECTION_NAME = "ap_policy_collection"


def get_embedding_model():
    """
    Create the embedding model used for both indexing and retrieval.
    """

    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def create_vector_store(documents):
    """
    Create a Chroma vector store from policy chunks.

    This function adds documents to the current collection.
    Use rebuild_vector_store() when policy data has changed or when
    you want to remove duplicate historical chunks.
    """

    embeddings = get_embedding_model()

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIRECTORY),
    )

    return vector_store


def rebuild_vector_store(documents):
    """
    Delete the existing AP-policy collection, then build a fresh one.

    This prevents duplicate policy chunks when ingestion is run again.
    """

    embeddings = get_embedding_model()

    existing_vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIRECTORY),
    )

    try:
        existing_vector_store.delete_collection()
        print(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception as error:
        print(
            "No existing collection was deleted. "
            f"A new collection will be created. Details: {error}"
        )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIRECTORY),
    )

    print(f"Created fresh collection: {COLLECTION_NAME}")

    return vector_store


def load_vector_store():
    """
    Load the persisted AP-policy vector store for retrieval.
    """

    embeddings = get_embedding_model()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIRECTORY),
    )

    return vector_store