from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunking(document):
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    add_start_index = True,
    separators=["\n\n", "\n", ". ", " ", ""]
)
    chunks = splitter.split_documents(document)

    return {
        "chunk" : chunks,
        "lenght":len(chunks)

    }


# print(len(chunks))
# print(chunks[0].page_content)
# print(chunks[0].metadata)