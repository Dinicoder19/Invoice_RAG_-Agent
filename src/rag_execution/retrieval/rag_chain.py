from langchain_ollama import ChatOllama
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from src.rag_execution.retrieval.retriever import get_retriever


def get_rag_chain():
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an Accounts Payable policy assistant.

Answer the question using only the supplied AP policy context.

If the answer is present in the context, provide the exact answer from the context.

If the question is about approval, explicitly include:
1. the invoice type,
2. the approval role,
3. the amount range or condition, if available.

If the answer is not present in the context, say:
'I could not find that information in the provided AP policy.'

Do not invent approval levels, amounts, or policy rules.

AP policy context:
{context}""",
            ),
            ("human", "{input}"),
        ]
    )

    document_prompt = PromptTemplate(
        input_variables=["page_content", "source"],
        template="Source: {source}\nContent:\n{page_content}",
    )

    document_chain = create_stuff_documents_chain(
        llm,
        prompt,
        document_prompt=document_prompt,
    )

    retrieval_chain = create_retrieval_chain(
        get_retriever(),
        document_chain,
    )

    return retrieval_chain