import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import config

class BookVectorStore:
    def __init__(self, device='cpu'):
        print(f"[VectorStore] Đang khởi tạo...")
        print(f"[VectorStore] Đang tải Model Embedding: {config.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(config.EMBEDDING_MODEL, device=device)

        print(f"[VectorStore] Đang tải FAISS index từ: {config.FAISS_INDEX_PATH}")
        self.index = faiss.read_index(config.FAISS_INDEX_PATH)

        print(f"[VectorStore] Đang tải metadata từ: {config.META_PATH}")
        with open(config.META_PATH, 'rb') as f:
            self.unique_ids_list = pickle.load(f)

        print(f" [VectorStore] Khởi tạo hoàn tất. Sẵn sàng tìm kiếm.")

    def search(self, query_text, k=5):
        """
        Thực hiện tìm kiếm vector cơ bản.
        Trả về: (list_of_unique_ids, list_of_positions, list_of_distances)
        """
        # Model BGE cần instruction "query: "
        query_with_instruction = f"query: {query_text}"

        query_vector = self.model.encode([query_with_instruction], normalize_embeddings=True)
        query_vector = np.array(query_vector).astype('float32')

        D, I = self.index.search(query_vector, k)

        retrieved_indices = I[0]
        retrieved_distances = D[0]

        retrieved_unique_ids = [self.unique_ids_list[i] for i in retrieved_indices]

        return retrieved_unique_ids, retrieved_indices, retrieved_distances