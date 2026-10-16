from sentence_transformers import SentenceTransformer


def embedding(MODEL,chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)
    return{"embedding":embeddings,
           "shape":embeddings.shape}