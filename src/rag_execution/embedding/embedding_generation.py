from langchain_huggingface import HuggingFaceEmbeddings


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def generate_document_embeddings(documents):
    embedding_model = get_embedding_model()

    texts = [document.page_content for document in documents]
    vectors = embedding_model.embed_documents(texts)

    return vectors


def generate_query_embedding(query: str):
    embedding_model = get_embedding_model()
    return embedding_model.embed_query(query)