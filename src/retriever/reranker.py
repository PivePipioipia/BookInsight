from sentence_transformers import CrossEncoder

class Reranker:
    """
    Reranker dựa trên cross-encoder (MS-MARCO MiniLM).
    Dùng để rerank các kết quả retrieve theo độ liên quan thực tế.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        print(f"Loading CrossEncoder model: {model_name}")
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: list, top_k: int = 5):
        """
        Rerank các tài liệu dựa trên độ tương quan query-doc.
        Args:
            query: truy vấn đầu vào
            docs: list các dict kết quả retrieve (có key: metadata["content"])
            top_k: số lượng kết quả trả về
        """
        pairs = []
        valid_docs = []

        for d in docs:
            text = d["metadata"].get("content") or d["metadata"].get("title")
            if text:
                pairs.append((query, text))
                valid_docs.append(d)

        if not pairs:
            print("Không có tài liệu hợp lệ để rerank.")
            return docs

        scores = self.model.predict(pairs)
        for doc, score in zip(valid_docs, scores):
            doc["rerank_score"] = float(score)

        reranked = sorted(valid_docs, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]
