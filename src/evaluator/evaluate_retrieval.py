def evaluate_retrieval(results, threshold=0.0):

    if not results:
        return "bad"

    best_score = results[0]["score"]

    if best_score >= threshold:
        return "good"

    return "bad"