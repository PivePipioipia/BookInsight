import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_faiss_index(
    df: pd.DataFrame,
    id_col: str,
    text_col: str,
    embed_col: str,
    save_dir: str,
):
    """Build FAISS index from DataFrame include embedding."""

    os.makedirs(save_dir, exist_ok=True)
    print(f" Building FAISS index for {len(df)} documents...")

    texts = df[text_col].tolist()
    ids = df[id_col].astype(str).tolist()
    vectors = df[embed_col].tolist()

    model_name = "BAAI/bge-small-en-v1.5"
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)

    db = FAISS.from_embeddings(
        zip(texts, vectors),
        embedding=embedding_model,
        ids=ids,
    )

    db.save_local(save_dir)
    print(f" Saved FAISS index to: {save_dir}")

    return db

def load_faiss_index(path: str):
    """
    Load FAISS index đã lưu từ local.
    Sử dụng cùng model embedding như khi build.
    """
    import os
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings

    if not os.path.exists(path):
        raise FileNotFoundError(f" Không tìm thấy thư mục index: {path}")

    print(f" Loading FAISS index from: {path}")

    model_name = "BAAI/bge-small-en-v1.5"
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)

    index = FAISS.load_local(
        path,
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )

    print("FAISS index loaded")
    return index


def test_query(index, query: str, k: int = 3):
    """
    Thử truy vấn top-k documents từ FAISS index
    Trả về list các đoạn văn bản gần nhất
    """
    print(f" Query: {query}")

    results = index.similarity_search(query, k= k)
    if not results:
        print("Không tìm thấy kết quả nào")
        return []
    print(f" Found {len(results)} results")
    return [r.page_content for r in results]

