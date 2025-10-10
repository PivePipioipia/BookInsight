import faiss
import os
from typing import List, Dict, Literal, Optional
import numpy as np
import pandas as pd


"""
base_retriever.py
=================
Core layer for loading and managing FAISS indexes (text or image).

Supports both plain FAISS indexes and LangChain FAISS pickles
that include InMemoryDocstore objects.
"""


class FaissStore:
    """Wrapper for a single FAISS index shard (either text or image)."""

    def __init__(self, index_path: str, meta_path: str, modality: Literal["text", "image"]):
        self.index_path = index_path
        self.meta_path = meta_path
        self.modality = modality
        self.index = None
        self.metadata = None

    # -------------------------------------------------------------------------
    # LOAD
    # -------------------------------------------------------------------------
    def load(self):
        """Load FAISS index and metadata from disk, with auto-fix for various formats."""
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"❌ Index file not found: {self.index_path}")
        if not os.path.exists(self.meta_path):
            raise FileNotFoundError(f"❌ Metadata file not found: {self.meta_path}")

        # --- Load FAISS index ---
        print(f"📦 Loading FAISS index from {self.index_path} ...")
        self.index = faiss.read_index(self.index_path)
        print(f"✅ Loaded FAISS index with {self.index.ntotal} vectors.")

        # --- Load metadata ---
        print(f"📘 Loading metadata from {self.meta_path} ...")

        if self.meta_path.endswith(".pkl"):
            self.metadata = pd.read_pickle(self.meta_path)

            # 🧩 CASE 1: LangChain FAISS tuple (InMemoryDocstore, id map, index)
            if isinstance(self.metadata, tuple):
                print("⚠️ Detected LangChain FAISS tuple — extracting InMemoryDocstore...")
                docstore = None
                for item in self.metadata:
                    if "InMemoryDocstore" in str(type(item)):
                        docstore = item
                        break
                if docstore is not None and hasattr(docstore, "_dict"):
                    try:
                        docs = [v.page_content for v in docstore._dict.values()]
                        metas = [v.metadata for v in docstore._dict.values()]
                        self.metadata = pd.DataFrame(metas)
                        self.metadata["content"] = docs
                    except Exception as e:
                        raise TypeError(f"⚠️ Could not parse InMemoryDocstore: {e}")
                else:
                    print("⚠️ No InMemoryDocstore found in tuple, keeping original object.")

            # 🧩 CASE 2: LangChain FAISS object (has .docstore attr)
            elif hasattr(self.metadata, "docstore") and hasattr(self.metadata, "index_to_docstore_id"):
                print("⚠️ Detected LangChain FAISS object — extracting documents into DataFrame...")
                try:
                    docs = [v.page_content for v in self.metadata.docstore._dict.values()]
                    metas = [v.metadata for v in self.metadata.docstore._dict.values()]
                    self.metadata = pd.DataFrame(metas)
                    self.metadata["content"] = docs
                except Exception as e:
                    raise TypeError(f"⚠️ Could not parse FAISS object: {e}")

        elif self.meta_path.endswith(".parquet"):
            self.metadata = pd.read_parquet(self.meta_path)
        else:
            raise ValueError("Unsupported metadata file type (use .pkl or .parquet).")

        # --- Validation ---
        n_index = self.index.ntotal
        n_meta = len(self.metadata) if hasattr(self.metadata, "__len__") else 0
        if n_index != n_meta:
            print(f"⚠️ WARNING: Mismatch between index ({n_index}) and metadata ({n_meta})")
        else:
            print(f"✅ Metadata rows match FAISS index: {n_meta} entries.")

        print(f"🎯 Loaded {self.modality.upper()} store successfully!")

    # -------------------------------------------------------------------------
    # SEARCH
    # -------------------------------------------------------------------------
    def search(self, vec: np.ndarray, k: int = 10) -> List[Dict]:
        """Search top-k most similar items in this FAISS index."""
        if self.index is None:
            raise RuntimeError("❌ FAISS index not loaded. Call .load() first.")
        if not isinstance(vec, np.ndarray):
            raise TypeError("❌ Query vector must be a numpy array.")
        if vec.dtype != np.float32:
            vec = vec.astype("float32")

        # --- Search in FAISS ---
        D, I = self.index.search(vec, k)
        results = []
        for rank, (idx, dist) in enumerate(zip(I[0], D[0])):
            if idx == -1:
                continue

            meta_row = {}
            if isinstance(self.metadata, pd.DataFrame):
                meta_row = self.metadata.iloc[idx].to_dict()
            elif isinstance(self.metadata, list) and len(self.metadata) > idx:
                meta_row = self.metadata[idx]

            results.append({
                "id": int(idx),
                "score": float(dist),
                "rank": rank + 1,
                "metadata": meta_row,
            })

        return results

    # -------------------------------------------------------------------------
    # INFO
    # -------------------------------------------------------------------------
    def ntotal(self) -> int:
        """Return number of vectors in the FAISS index."""
        return getattr(self.index, "ntotal", 0)

    def info(self):
        """Print basic summary info about this store."""
        print(f" FAISSStore ({self.modality})")
        print(f"• Index path : {self.index_path}")
        print(f"• Meta path  : {self.meta_path}")
        print(f"• Vectors    : {self.ntotal()}")


# -------------------------------------------------------------------------
# COMPOSITE STORE
# -------------------------------------------------------------------------
class CompositeStore:
    """Manager for multiple FAISS shards."""

    def __init__(self, modality: Literal["text", "image"]):
        self.modality = modality
        self.stores: List[FaissStore] = []

    def add_store(self, store: FaissStore):
        """Add a FAISS store (shard) to this composite."""
        self.stores.append(store)

    def search(self, vec: np.ndarray, k: int = 10) -> List[Dict]:
        """Search across all shards and merge results."""
        all_results = []
        for store in self.stores:
            part = store.search(vec, k)
            all_results.extend(part)
        all_results = sorted(all_results, key=lambda x: x["score"], reverse=True)[:k]
        return all_results

    def info(self):
        """Display info for all shards."""
        print(f" CompositeStore ({self.modality}) with {len(self.stores)} shard(s):")
        for store in self.stores:
            store.info()
