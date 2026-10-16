retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)

results = retriever.invoke(
    "How does RAG work?"
)

for doc in results:
    print(doc.page_content)

def vector_loader():
    index = faiss.read_index(
        "vector_store/index>faiss"
    )

    with open("vector_store/chunks.json", "r",encoding="utf-8") as file:
        chunks = json.load(file)

    return index, chunks 

def reviewer(querry,k=4):
    index , chunks = vector_loader()
    query_vector = embeddings_model.embed_query(querry)
    query_vector = np.array([query_vector]).astype("float32")
    distances, indices = index.search(
        query_vector,
        k
    )

    results = []

    for distance, index_id in zip(
        distances[0],
        indices[0]
    ):

        results.append({
            "text": chunks[index_id]["text"],
            "metadata": chunks[index_id]["metadata"],
            "score": float(distance)
        })

    return results