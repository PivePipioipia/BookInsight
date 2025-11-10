def recall_at_k(relevant, retrieved, k=5):
    return len(set(relevant) & set(retrieved[:k])) / len(relevant)

def mrr(relevant, retrieved):
    for i, r in enumerate(retrieved):
        if r in relevant:
            return 1 / (i + 1)
    return 0.0
