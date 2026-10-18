from src.evaluator.coracttive_retrieval import corrective_retrieval
from src.retrieval.reranker import rerank


def corrective_reranking(query,index_path,chunk_path,k=5):

    results = corrective_retrieval(query,index_path,chunk_path,k=5)

    reranked = rerank(
        query,
        results,
        top_k=4
    )
    if evaluate_reranking(result,0.3) == "good":
        return reranked
    else:
        return "bad"