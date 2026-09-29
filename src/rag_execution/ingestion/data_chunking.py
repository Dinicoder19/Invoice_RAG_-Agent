from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=800,
        chunk_overlap=120,
        length_function=len,
        is_separator_regex=False,
    )


def chunk_documents(documents):
    text_splitter = get_text_splitter()
    chunked_docs = text_splitter.split_documents(documents)

    for index, chunk in enumerate(chunked_docs):
        chunk.metadata["chunk_index"] = index
        chunk.metadata["chunking_status"] = "completed"

    return chunked_docs
