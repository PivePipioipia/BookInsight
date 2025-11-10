from config import RRF_K
from vectorstore import BookVectorStore
from sql_database import SQLDatabase
from retriever.query_expander import OpenAIQueryExpander

print("t")
class SmartRetriever:
    """
    Class "điều phối" (orchestrator) chính, kết hợp tất cả các thành phần:
    1. Query Expander (OpenAI)
    2. Vector Store (FAISS + BGE)
    3. RRF (Logic hợp nhất)
    4. SQL Database (Lấy chi tiết)
    """
    def __init__(self, device='cpu'):
        print("[SmartRetriever] Đang khởi tạo các thành phần...")
        self.vector_store = BookVectorStore(device=device)
        self.sql_db = SQLDatabase()
        self.query_expander = OpenAIQueryExpander()
        self.rrf_k = RRF_K
        print("[SmartRetriever] Khởi tạo hoàn tất.")

    def _reciprocal_rank_fusion(self, search_results_list, k=60):
        """
        Logic RRF (lấy từ notebook cell 10).
        Đây là một phương thức "private".
        """
        scores = {}
        for results in search_results_list:
            for rank, pos in enumerate(results):
                doc_score = 1.0 / (k + (rank + 1))
                if pos not in scores:
                    scores[pos] = 0.0
                scores[pos] += doc_score

        return sorted(scores.items(), key=lambda item: item[1], reverse=True)

    def retrieve(self, query, top_k=5):
        """
        Phương thức "công khai" (public) để thực hiện toàn bộ pipeline.
        """
        print(f"\n[SmartRetriever] Bắt đầu truy vấn cho: '{query}'")
        
        SEARCH_DEPTH_K = 20

        all_queries = self.query_expander.expand_query(query)
        
        all_search_results = []
        print("[SmartRetriever] Đang thực hiện tìm kiếm song song...")
        for q in all_queries:
            
            _, positions, _ = self.vector_store.search(q, k=SEARCH_DEPTH_K)
            all_search_results.append(positions)
            
        print("[SmartRetriever] Đang hợp nhất kết quả với RRF...")
        fused_results_with_scores = self._reciprocal_rank_fusion(all_search_results, self.rrf_k)
        
        final_results = fused_results_with_scores[:top_k]
        final_positions = [pos for pos, score in final_results]
        
        final_unique_ids = [self.vector_store.unique_ids_list[i] for i in final_positions]
        
        book_details_list = self.sql_db.get_details_by_ids(final_unique_ids)
        
        final_books_with_scores = []
        for i, book in enumerate(book_details_list):
            book['rrf_score'] = final_results[i][1] # Gắn điểm RRF
            final_books_with_scores.append(book)
            
        print("[SmartRetriever] Truy vấn RAG-Fusion hoàn tất.")
        return final_books_with_scores

    def close(self):
        """Đóng kết nối SQL khi hoàn tất."""
        self.sql_db.close()