from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from ..config import Settings
from ..services.document_ingestion import DocumentIngestionService
from ..services.qa import QuestionAnsweringService
from ..storage.vector import VectorStore


class BotFactory:
    """Фабрика компонентов телеграм-бота."""

    def __init__(self, settings: Settings):
        """Создает фабрику с заданными настройками."""

        self._settings = settings

    def create_bot(self) -> Bot:
        """Создает экземпляр бота."""

        return Bot(
            token=self._settings.telegram_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    def create_dispatcher(self) -> Dispatcher:
        """Создает диспетчер для обработки обновлений."""

        return Dispatcher(storage=MemoryStorage())

    def create_vector_store(self) -> VectorStore:
        """Создает векторное хранилище."""

        return VectorStore(settings=self._settings)

    def create_document_ingestion(self, vector_store: VectorStore) -> DocumentIngestionService:
        """Создает сервис загрузки документов."""

        return DocumentIngestionService(settings=self._settings, vector_store=vector_store)

    def create_qa_service(self, vector_store: VectorStore) -> QuestionAnsweringService:
        """Создает сервис ответов на вопросы."""

        return QuestionAnsweringService(settings=self._settings, vector_store=vector_store)

