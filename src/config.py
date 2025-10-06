import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(BASE_DIR, "data")

RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")
VECTORSTORE_DIR = os.path.join(DATA_DIR, "vectorstores")

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

print(f" Config loaded. Base dir: {BASE_DIR}")
