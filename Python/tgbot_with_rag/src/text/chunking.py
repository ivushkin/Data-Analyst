from typing import Iterable, List

from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Chunker:
    """Инструмент для разбиения документов на текстовые чанки."""

    def __init__(self, chunk_size: int, chunk_overlap: int):
        """Создает чанкер с заданными параметрами."""

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk_documents(self, documents: Iterable[Document]) -> List[Document]:
        """Разбивает исходные документы на последовательность чанков."""

        return self._splitter.split_documents(list(documents))

