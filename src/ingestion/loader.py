from langchain_community.document_loaders import PyPDFLoader


def loader(FILE_PATH):
    loader = PyPDFLoader(FILE_PATH)
    document = loader.load()
    return {
        "document" :document,
        "lenght": len(document)
    }

