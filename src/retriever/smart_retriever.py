"""
smart_retriever.py
==================
Phase 3: Smart Retriever Layer for BookInsight

- Expands user queries via Mistral-7B-Instruct (local inference)
- Performs multi-query multimodal retrieval using TextImageRetriever
- Fuses results via Reciprocal Rank Fusion (RRF)

Author: BookInsight R&D
"""

from typing import List, Dict
import numpy as np
from src.retriever.text_image_retriever import TextImageRetriever

import logging
logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)


class SmartRetriever:
    """
    Smart retriever with query expansion and multimodal fusion.

    Attributes
    ----------
    retriever : TextImageRetriever
        The base multimodal retriever (text + image FAISS).
    llm : object
        Local Mistral model for query expansion (transformers pipeline).
    """

    def __init__(self, retriever: TextImageRetriever):
        self.retriever = retriever
        self.llm = self._load_local_llm()


    def _load_local_llm(self):
        """Load local Mistral-7B-Instruct (free offline paraphraser)."""
        try:
            from transformers import pipeline
            logging.info("Loading Mistral-7B-Instruct model for query expansion...")
            llm = pipeline(
                "text-generation",
                model="mistralai/Mistral-7B-Instruct-v0.2",
                torch_dtype="auto",
                device_map="auto",
                max_new_tokens=128,
            )
            return llm
        except Exception as e:
            logging.warning(f" Could not load Mistral locally: {e}")
            logging.warning("Falling back to simple rule-based paraphraser.")
            return None


    def expand_queries(self, query: str, n: int = 5) -> List[str]:
        """Generate multiple paraphrased queries using Mistral or fallback."""
        if self.llm:
            prompt = (
                f"You are a helpful AI that generates {n} paraphrases "
                f"of the user query in English.\n"
                f"User query: '{query}'\n"
                f"Return only the list of paraphrases, one per line."
            )
            output = self.llm(prompt)[0]["generated_text"]
            candidates = [
                line.strip("-•1234567890. ").strip()
                for line in output.split("\n")
                if len(line.strip()) > 10
            ]
            queries = list(dict.fromkeys(candidates))[:n]
        else:
            # fallback: simple template-based variants
            queries = [
                query,
                query.replace("children", "kids"),
                query.replace("fantasy", "adventure"),
                f"a story about {query}",
                f"{query} book for young readers",
            ][:n]

        logging.info(f"Generated {len(queries)} query variants:")
        for q in queries:
            logging.info(f"  • {q}")
        return queries

    # Multi-query multimodal search

    def search_multimodal(self, query: str, n_expand: int = 3, k: int = 10) -> List[Dict]:
        """
        Expand a query, run multimodal retrieval for each variant,
        and fuse all results via RRF.
        """
        queries = self.expand_queries(query, n_expand)
        all_text, all_image = [], []

        for q in queries:
            logging.info(f" Searching for variant: '{q}'")
            try:
                t_res = self.retriever.retrieve_text(q, k)
                i_res = self.retriever.retrieve_image_by_text(q, k)
                all_text.extend(t_res)
                all_image.extend(i_res)
            except Exception as e:
                logging.error(f"Search failed for '{q}': {e}")

        fused = self.retriever.fuse_results(all_text, all_image, method="rrf")
        logging.info(f" Fused {len(fused)} total results from {len(queries)} query variants.")
        return fused
