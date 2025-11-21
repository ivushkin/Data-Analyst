from typing import Iterable, Optional
import logging

from langchain.schema import Document
from langchain_chroma import Chroma

from ..config import Settings
from ..text.embedder import EmbedderFactory, OllamaHTTPEmbeddings


class VectorStore:
    """Обертка над векторным хранилищем документов."""

    def __init__(self, settings: Settings):
        """Создает векторное хранилище с использованием Chroma."""

        self._logger = logging.getLogger(__name__)
        self._settings = settings
        self._embedder = EmbedderFactory.create(settings=settings)
        collection_name = self._build_collection_name(settings)
        self._store = Chroma(
            collection_name=collection_name,
            persist_directory=settings.vector_store_path,
            embedding_function=self._embedder,
        )

    async def add_documents(self, documents: Iterable[Document]) -> None:
        """Добавляет документы в хранилище."""

        # В langchain_chroma объект Chroma автоматически использует persistent client
        # при указании persist_directory. Явный persist() отсутствует.
        # Выполняем в executor, чтобы не блокировать event loop
        import asyncio
        await asyncio.to_thread(self._store.add_documents, list(documents))

    def as_retriever(self, search_kwargs: Optional[dict] = None):
        """Возвращает объект для поиска ближайших соседей."""

        return self._store.as_retriever(search_kwargs=search_kwargs or {})

    def clear(self) -> None:
        """Полностью очищает базу векторов."""

        try:
            client = self._store._client  # type: ignore[attr-defined]
            name = self._store._collection.name  # type: ignore[attr-defined]
            try:
                client.delete_collection(name=name)
            except Exception:
                # если коллекция уже отсутствует — игнорируем
                pass
            # пересоздаём с тем же именем
            self._store = Chroma(
                collection_name=name,
                persist_directory=self._settings.vector_store_path,
                embedding_function=self._embedder,
            )
            self._logger.info("Chroma collection '%s' recreated (cleared).", name)
        except Exception:
            self._logger.exception("Критическая ошибка при очистке/пересоздании коллекции Chroma")

    def document_count(self) -> int:
        """Возвращает количество документов в базе векторов."""

        try:
            collection = self._store._collection  # type: ignore[attr-defined]
            return int(collection.count())
        except Exception:
            self._logger.exception("Ошибка при получении количества документов Chroma")
            return 0

    def file_count(self) -> int:
        """Возвращает количество уникальных файлов-источников по метаданным 'source'."""

        try:
            collection = self._store._collection  # type: ignore[attr-defined]
            data = collection.get(include=["metadatas"])  # type: ignore[no-any-return]
            metadatas = data.get("metadatas") or []
            sources = set()
            for md in metadatas:
                if isinstance(md, dict):
                    src = md.get("source")
                    if src:
                        sources.add(str(src))
            return len(sources)
        except Exception:
            self._logger.exception("Ошибка при получении количества файлов Chroma")
            return 0

    def delete_by_source(self, source: str) -> int:
        """Удаляет все документы с метаданным source. Возвращает количество удаленных ID."""

        try:
            collection = self._store._collection  # type: ignore[attr-defined]
            # Получаем все ID с данным source
            data = collection.get(where={"source": source}, include=["metadatas", "documents"])  # type: ignore[no-any-return]
            # В текущем API chroma не возвращает ids в include, поэтому удалим через where
            # (delete(where=...) пока не везде реализован; fallback: удаляем через get+ids недоступно)
            # Используем прямое удаление по where, если оно поддерживается:
            try:
                collection.delete(where={"source": source})
                # оценим количество по числу найденных метаданных
                metadatas = data.get("metadatas") or []
                return len(metadatas)
            except Exception:
                # если where не поддерживается, ничего не удалили
                pass
            return 0
        except Exception:
            self._logger.exception("Ошибка удаления документов по source в Chroma")
            return 0

    def _build_collection_name(self, settings: Settings) -> str:
        """Формирует имя коллекции с учётом модели и размерности эмбеддингов.

        Это позволяет избежать конфликта размерностей при смене модели.
        """

        provider = (getattr(settings, "embeddings_provider", "") or "").lower()
        model = getattr(settings, "embeddings_model", "") or "unknown"
        dim: int = 0
        try:
            # Пытаемся определить размерность, если поддерживается
            if isinstance(self._embedder, OllamaHTTPEmbeddings):
                dim = self._embedder.ensure_dimension()
        except Exception:
            pass
        suffix = f"{model.replace(':', '_').replace('/', '_')}"
        if dim:
            suffix = f"{suffix}_{dim}d"
        base = "documents"
        if provider:
            return f"{base}_{provider}_{suffix}"
        return f"{base}_{suffix}"

