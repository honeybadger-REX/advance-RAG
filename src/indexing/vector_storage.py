import faiss
import numpy as np 
import os

def indexing(embedding):
     embeddings = np.array(embedding).astype("float32")
     dimension = embeddings.shape[1]
     index = faiss.IndexFlatL2(dimension)
     index.add(embeddings)
     return index

def save_index(index, chunks):
    """
    Save FAISS index and original chunks.
    """

    os.makedirs("vector_store", exist_ok=True)

    # Save FAISS index
    faiss.write_index(
        index,
        "vector_store/index.faiss"
    )

    # Save original chunks
    chunk_data = [
        {
            "text": chunk.page_content,
            "metadata": chunk.metadata
        }
        for chunk in chunks
    ]

    with open("vector_store/chunks.json","w", encoding="utf-8") as file:
        json.dump(
            chunk_data,
            file,
            ensure_ascii=False,
            indent=2
        )
