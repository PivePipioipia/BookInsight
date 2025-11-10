"""
text_image_retriever.py
=======================

Unified multimodal retriever for BookInsight:
    - Retrieve text passages via text embeddings (BGE)
    - Retrieve related images via CLIP text encoder
    - Fuse results from both modalities (RRF or weighted)

This module wraps two FaissStore instances (text + image)
and provides a clean API for multimodal retrieval.
"""

from typing import List, Dict, Literal, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from src.retriever.base_retriever import FaissStore


class TextImageRetriever:
    """
    A unified retriever that can search across text and image FAISS indexes.

    Attributes
    ----------
    text_store : FaissStore
        FAISS store containing text embeddings.
    image_store : FaissStore
        FAISS store containing image embeddings.
    text_encoder : Optional[object]
        SentenceTransformer or similar model for text embedding.
    image_text_encoder : Optional[object]
        CLIP text encoder for text→image retrieval.
    fusion_method : Literal["rrf", "weighted"]
        How to combine text and image results.

    Methods
    -------
    load_stores()
        Load both FAISS stores (text and image).
    retrieve_text(query: str, k: int = 10) -> List[Dict]
        Search books via text embeddings.
    retrieve_image_by_text(query: str, k: int = 10) -> List[Dict]
        Search related images using CLIP text encoder.
    fuse_results(results_text, results_image, method="rrf", alpha=0.7) -> List[Dict]
        Merge results into a unified ranked list.
    """

    def __init__(
        self,
        text_index_path: str,
        text_meta_path: str,
        image_index_path: str,
        image_meta_path: str,
        fusion_method: Literal["rrf", "weighted"] = "rrf",
    ):
        self.text_store = FaissStore(text_index_path, text_meta_path, modality="text")
        self.image_store = FaissStore(image_index_path, image_meta_path, modality="image")
        self.text_encoder = None
        self.image_text_encoder = None
        self.fusion_method = fusion_method


    def load_stores(self):
        """Load both text and image FAISS stores from disk."""
        print(" Loading text FAISS store...")
        self.text_store.load()
        print("\n Loading image FAISS store...")
        self.image_store.load()


    def encode_text_bge(self, query: str) -> np.ndarray:
        """
        Encode text query using BGE-small-en-v1.5 (for text FAISS index).
        """
        if self.text_encoder is None:
            print("Loading BGE encoder (BAAI/bge-small-en-v1.5)...")
            self.text_encoder = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")

        query_vec = self.text_encoder.encode([query], normalize_embeddings=True)
        return np.array(query_vec, dtype="float32")

    def encode_text_clip(self, query: str) -> np.ndarray:
        """
        Encode text query using CLIP-ViT-B-16 (for image FAISS index).
        """
        if self.image_text_encoder is None:
            print("Loading CLIP text encoder (clip-ViT-B-16)...")
            self.image_text_encoder = SentenceTransformer("clip-ViT-B-16", device="cpu")

        query_vec = self.image_text_encoder.encode([query], normalize_embeddings=True)
        return np.array(query_vec, dtype="float32")


    def retrieve_text(self, query: str, k: int = 10) -> List[Dict]:
        """
        Retrieve top-k text documents for a query string using BGE encoder.
        """
        query_vec = self.encode_text_bge(query)
        results = self.text_store.search(query_vec, k=k)
        for r in results:
            r["source"] = "text"
            try:
                meta = self.text_store.meta.iloc[r["id"]].to_dict()
                r["metadata"] = meta
            except Exception:
                r["metadata"] = {}
        return results

    def retrieve_image_by_text(self, query: str, k: int = 10) -> List[Dict]:
        """
        Retrieve top-k images using CLIP text embeddings.

        Parameters
        ----------
        query : str
            Text query to encode using CLIP text encoder.
        k : int, optional
            Number of results to return (default=10).

        Returns
        -------
        List[Dict]
            List of ranked image search results.
        """
        from sentence_transformers import SentenceTransformer
        import numpy as np

        # lazy-load CLIP text encoder
        if self.image_text_encoder is None:
            print("🧠 Loading CLIP text encoder (clip-ViT-B-16)...")
            self.image_text_encoder = SentenceTransformer("clip-ViT-B-16", device="cpu")

        # encode + normalize query
        query_vec = self.image_text_encoder.encode(
            query, convert_to_numpy=True, normalize_embeddings=True
        )
        query_vec = np.expand_dims(query_vec, axis=0)

        # search in FAISS image store
        results = self.image_store.search(query_vec, k=k)
        for r in results:
            r["source"] = "image"
            try:
                meta = self.image_store.meta.iloc[r["id"]].to_dict()
                r["metadata"] = meta
            except Exception:
                r["metadata"] = {}
        return results

    def fuse_results(
            self,
            results_text: List[Dict],
            results_image: List[Dict],
            method: Literal["rrf", "weighted"] = "rrf",
            alpha: float = 0.7,
            k: int = 10,
    ) -> List[Dict]:
        """
        Gộp kết quả text + image (RRF hoặc weighted).
        Hỗ trợ gộp trùng ID, tính điểm hợp lý, fallback title/image_url.
        """
        import numpy as np
        from collections import defaultdict

        if not results_text and not results_image:
            print("⚠️ Không có kết quả để gộp.")
            return []

        # ============ RRF Fusion ============
        rrf_k = 10  # nhỏ hơn => độ chênh điểm cao hơn
        if method == "rrf":
            for r in results_text:
                r["fused_score"] = 1.0 / (rrf_k + r.get("rank", 1000))
            for r in results_image:
                r["fused_score"] = 1.0 / (rrf_k + r.get("rank", 1000))

        # ============ Weighted Fusion ============
        elif method == "weighted":
            def normalize(arr):
                arr = np.array(arr)
                return (arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-8)

            scores_t = normalize([r["score"] for r in results_text]) if results_text else []
            scores_i = normalize([r["score"] for r in results_image]) if results_image else []
            for i, r in enumerate(results_text):
                r["fused_score"] = alpha * scores_t[i]
            for i, r in enumerate(results_image):
                r["fused_score"] = (1 - alpha) * scores_i[i]
        else:
            raise ValueError(" Fusion method phải là 'rrf' hoặc 'weighted'.")

        # ============ Gộp và loại trùng ============
        all_results = results_text + results_image
        merged = defaultdict(lambda: {"fused_score": 0, "count": 0, "sources": set(), "metadata": {}})

        for r in all_results:
            meta = r.get("metadata", {}) or {}
            uid = (
                    meta.get("unique_id")
                    or meta.get("asin")
                    or meta.get("id")
                    or meta.get("title")
                    or f"noid_{id(r)}"
            )

            merged[uid]["fused_score"] += r.get("fused_score", r.get("score", 0))
            merged[uid]["count"] += 1
            merged[uid]["sources"].add(r.get("source", "?"))

            # Nếu chưa có metadata có title thì gán
            if not merged[uid]["metadata"].get("title") and meta:
                merged[uid]["metadata"] = meta

        # Chuyển lại sang list + sắp xếp
        fused = []
        for uid, info in merged.items():
            fused.append({
                "id": uid,
                "fused_score": info["fused_score"],
                "count": info["count"],
                "sources": list(info["sources"]),
                "metadata": info["metadata"]
            })

        fused = sorted(fused, key=lambda x: (x["fused_score"], x["count"]), reverse=True)
        for rank, r in enumerate(fused, 1):
            r["rank"] = rank

        fused = fused[:k]

        # ============ In tóm tắt =============
        print(f"[INFO]  Gộp {len(fused)} kết quả cuối cùng từ {len(all_results)} kết quả gốc.")
        for r in fused:
            meta = r["metadata"]
            title = meta.get("title") or meta.get("content") or meta.get("description") or "❓(không có title)"
            img = meta.get("image_url") or meta.get("cover") or ""
            src = ",".join(r["sources"])
            print(f"[{src}] {title[:120]} | score={r['fused_score']:.4f} | count={r['count']}")
            if img:
                print(f"     🖼 {img}")

        for r in fused:
            r["source"] = ",".join(r.get("sources", [])) if isinstance(r.get("sources"), list) else r.get("sources",
                                                                                                          "?")
        return fused
