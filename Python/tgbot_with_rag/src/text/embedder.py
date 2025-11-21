from typing import Protocol, List, Optional
import logging
import requests
from langchain.embeddings.base import Embeddings

from ..config import Settings


class _EmbeddingsProvider(Protocol):
    """Протокол провайдера эмбеддингов."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:  # type: ignore[override]
        """Вычисляет эмбеддинги для списка документов."""

    def embed_query(self, text: str) -> List[float]:  # type: ignore[override]
        """Вычисляет эмбеддинг для одного запроса."""


class OllamaHTTPEmbeddings(Embeddings):
    """Embeddings через Ollama HTTP API (/api/embeddings)."""

    def __init__(self, endpoint: str, model: str):
        """Создает адаптер с указанием конечной точки и модели."""

        ep = endpoint.rstrip("/")
        if not ep.endswith("/api/embeddings"):
            ep = f"{ep}/api/embeddings"
        self._endpoint = ep
        self._model = model
        self._dim: Optional[int] = None
        self._logger = logging.getLogger(__name__)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Вычисляет эмбеддинги батчем."""

        vectors: List[List[float]] = []
        for text in texts:
            if not text or not text.strip():
                vectors.append(self._zero_vector())
                continue
            vec = self.embed_query(text)
            if not vec:
                vec = self._zero_vector()
            vectors.append(vec)
        return vectors

    def embed_query(self, text: str) -> List[float]:
        """Вычисляет эмбеддинг одного текста."""

        try:
            # Ollama embeddings API ожидает поле "prompt" для текста
            response = requests.post(
                self._endpoint,
                json={"model": self._model, "prompt": text},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            vector: List[float] = data.get("embedding") or []
            if vector:
                if self._dim is None:
                    self._dim = len(vector)
                return vector
            data_list = data.get("data") or []
            if isinstance(data_list, list) and data_list:
                vector = data_list[0].get("embedding") or []
                if vector and self._dim is None:
                    self._dim = len(vector)
                if vector:
                    return vector
        except Exception:
            self._logger.exception("Ошибка запроса к Ollama embeddings")
        return self._zero_vector()

    def _zero_vector(self) -> List[float]:
        """Возвращает нулевой вектор требуемой размерности."""

        dim = self._dim or 768
        return [0.0] * dim

    def ensure_dimension(self) -> int:
        """Гарантирует определение размерности эмбеддингов и возвращает её.

        Выполняет один пробный запрос к модели, если размерность ещё не определена.
        """

        if self._dim is None:
            try:
                vec = self.embed_query("dimension_probe_text")
                if vec:
                    self._dim = len(vec)
            except Exception:
                # Ошибку уже залогировали внутри embed_query
                pass
        return int(self._dim or 0)

    @property
    def dimension(self) -> Optional[int]:
        """Текущая известная размерность эмбеддингов (может быть None до прогрева)."""

        return self._dim


class EmbedderFactory:
    """Фабрика эмбеддингов для векторного хранилища."""

    @staticmethod
    def create(settings: Settings) -> Embeddings:
        """Создает провайдер эмбеддингов согласно настройкам."""

        provider = (settings.embeddings_provider or "").lower()
        if provider == "ollama" and settings.embeddings_endpoint and settings.embeddings_model:
            return OllamaHTTPEmbeddings(
                endpoint=settings.embeddings_endpoint,
                model=settings.embeddings_model,
            )

        raise RuntimeError("Не настроен провайдер эмбеддингов. Укажите EMBEDDINGS_PROVIDER=ollama и параметры EMBEDDINGS_ENDPOINT/EMBEDDINGS_MODEL.")

