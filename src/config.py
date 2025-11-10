import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SQL_DB_PATH = os.path.join(DATA_DIR, "database", "books.db")

VS_DIR = os.path.join(DATA_DIR, "vectorstores")
FAISS_INDEX_PATH = os.path.join(VS_DIR, "index.faiss")
EMBEDDINGS_PATH = os.path.join(VS_DIR, "embeddings.npy")
META_PATH = os.path.join(VS_DIR, "unique_ids.pkl")

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "gpt-3.5-turbo"
RRF_K = 60
