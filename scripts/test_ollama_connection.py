from langchain_ollama import ChatOllama


def main():
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
    )

    response = llm.invoke("Say exactly: Ollama connection successful.")
    print(response.content)


if __name__ == "__main__":
    main()