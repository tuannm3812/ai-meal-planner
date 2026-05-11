import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmbeddingSearchResult:
    corpus_index: int
    score: float


class LocalEmbeddingIndex:
    backend_name = "sentence_transformers_faiss_v0.1"

    def __init__(
        self,
        documents: list[str],
        cache_dir: Path,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.documents = documents
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._faiss = self._import_faiss()
        self.model = self._load_model()
        self.embeddings = self._load_or_create_embeddings()
        self.index = self._build_faiss_index(self.embeddings)

    @property
    def available(self) -> bool:
        return self.model is not None and self.index is not None

    def search(self, query: str, top_k: int) -> list[EmbeddingSearchResult]:
        if not self.available:
            return []
        query_embedding = self._encode([query])
        if query_embedding.size == 0:
            return []
        scores, indices = self.index.search(query_embedding, top_k)
        return [
            EmbeddingSearchResult(corpus_index=int(index), score=round(float(score), 4))
            for index, score in zip(indices[0], scores[0], strict=False)
            if index >= 0
        ]

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            logger.info("sentence-transformers is not installed; using TF-IDF retriever.")
            return None

        try:
            return SentenceTransformer(self.model_name)
        except Exception as exc:
            logger.warning("Sentence embedding model failed to load: %s", exc)
            return None

    @staticmethod
    def _import_faiss():
        try:
            import faiss
        except ImportError:
            logger.info("faiss-cpu is not installed; using TF-IDF retriever.")
            return None
        return faiss

    def _build_faiss_index(self, embeddings: np.ndarray):
        if self._faiss is None or embeddings.size == 0:
            return None
        index = self._faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        return index

    def _load_or_create_embeddings(self) -> np.ndarray:
        cache_path = self.cache_dir / f"{self._cache_key()}.npy"
        if cache_path.exists():
            return np.load(cache_path).astype("float32")

        embeddings = self._encode(self.documents)
        if embeddings.size:
            np.save(cache_path, embeddings)
        return embeddings

    def _encode(self, texts: list[str]) -> np.ndarray:
        if self.model is None:
            return np.empty((0, 0), dtype="float32")
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype="float32")

    def _cache_key(self) -> str:
        payload = {
            "model_name": self.model_name,
            "documents": self.documents,
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
