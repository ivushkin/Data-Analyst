import asyncio
import logging
import re
import html
from typing import Any, Dict, Set
from collections import deque
from typing import Deque, DefaultDict
import os
import requests

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command

from .config import Settings
from .services.document_ingestion import DocumentIngestionService
from .services.qa import QuestionAnsweringService
from .tooling.bot_factory import BotFactory
from .web.app import SettingsWebApp


class TelegramBotApplication:
    """Основной класс приложения телеграм-бота."""

    def __init__(self, settings: Settings):
        """Создает экземпляр приложения c зависимостями."""

        self._settings = settings
        factory = BotFactory(settings=settings)
        vector_store = factory.create_vector_store()
        ingestion_service = factory.create_document_ingestion(vector_store=vector_store)
        qa_service = factory.create_qa_service(vector_store=vector_store)
        self._bot = factory.create_bot()
        self._dispatcher = factory.create_dispatcher()
        self._services: Dict[str, Any] = {"ingestion": ingestion_service, "qa": qa_service}
        self._processing_users: Set[int] = set()
        self._user_queues: Dict[int, Deque[Message]] = {}
        self._user_workers: Set[int] = set()
        self._album_buffers: Dict[str, list[Message]] = {}
        self._album_tasks: Dict[str, asyncio.Task] = {}
        self._register_handlers()
        self._web_app = SettingsWebApp()
        self._startup_task: asyncio.Task | None = None
        # In-memory история диалога: user_id -> deque[(question, answer)]
        self._dialog_history: Dict[int, Deque[tuple[str, str]]] = {}

    def _register_handlers(self) -> None:
        """Регистрирует обработчики событий телеграм-бота."""

        dispatcher = self._dispatcher
        dispatcher.message.register(self._on_start, CommandStart())
        dispatcher.message.register(self._on_reset, Command(commands=["reset"]))
        dispatcher.callback_query.register(self._on_callback)
        dispatcher.message.register(self._on_message)

    async def _on_start(self, message: Message) -> None:
        """Обрабатывает команду /start."""

        ingestion: DocumentIngestionService = self._services["ingestion"]
        docs = ingestion.document_count()
        files = ingestion.file_count()
        size_bytes = self._dir_size_bytes(self._settings.vector_store_path)
        size_h = self._human_readable_size(size_bytes)
        from .utils.config_utils import get_public_web_url
        settings_url = get_public_web_url() or "http://localhost:8080/"
        text = (
            "Сервис бота - запущен\n"
            "Сервис векторной бд - запущен\n\n"
            f"В базе документов: {docs}. Файлов-источников: {files}.\n"
            f"Размер векторной базы на диске: {size_h}.\n"
            "Отправьте файлы для индексации. После загрузки задавайте вопросы по содержимому загруженных файлов.\n\n"
            f"Панель настроек: {settings_url}"
        )
        await message.answer(text=text, reply_markup=self._menu_markup())

    async def _on_reset(self, message: Message) -> None:
        """Очищает историю диалога пользователя."""

        user_id = message.from_user.id if message.from_user else 0
        if not self._is_user_allowed(user_id):
            return
        try:
            self._dialog_history.pop(user_id, None)
            await message.answer(text="История диалога очищена.")
        except Exception:
            await message.answer(text="Не удалось очистить историю. Попробуйте позже.")

    def _menu_markup(self) -> InlineKeyboardMarkup:
        """Создает inline-меню для управления базой."""

        kb: list[list[InlineKeyboardButton]] = []
        kb.append([InlineKeyboardButton(text="Очистить базу документов", callback_data="action:clear")])
        kb.append([InlineKeyboardButton(text="Информация о базе", callback_data="action:info")])
        return InlineKeyboardMarkup(inline_keyboard=kb)

    def _settings_markup(self) -> InlineKeyboardMarkup:
        """Клавиатура только с кнопкой на веб-панель настроек."""
        return self._menu_markup()
    
    # удалено: _public_web_url → util get_public_web_url

    async def _on_callback(self, query: CallbackQuery) -> None:
        """Обрабатывает нажатия на inline-кнопки."""

        data = (query.data or "").strip()
        if data == "action:clear":
            ingestion: DocumentIngestionService = self._services["ingestion"]
            ingestion.clear_store()
            await query.message.edit_text(
                text="База документов очищена.",
                reply_markup=self._menu_markup(),
            )
            return
        if data == "action:info":
            ingestion: DocumentIngestionService = self._services["ingestion"]
            count = ingestion.document_count()
            await query.answer()
            await query.message.answer(
                text=f"В базе документов: {count}",
                reply_markup=self._menu_markup(),
            )
            return
        await query.answer()

    async def _on_message(self, message: Message) -> None:
        """Обрабатывает входящие сообщения и документы."""

        user_id = message.from_user.id if message.from_user else 0
        # Жёсткая фильтрация по белому списку пользователей из JSON-конфига
        if not self._is_user_allowed(user_id):
            return
        # При активной обработке игнорируем текстовые сообщения, но документы ставим в очередь
        if message.media_group_id:
            await self._handle_media_group(message)
            return
        if message.document or message.photo:
            await self._enqueue_document(user_id, message)
            return
        if user_id and user_id in self._processing_users:
            return
        if not (message.text and not message.text.strip().startswith("/")):
            await message.answer(
                text="Задайте вопрос по ранее загруженным документам или отправьте файл.",
                reply_markup=self._menu_markup(),
            )
            return
        await self._handle_question(message)

    async def _handle_document(self, message: Message) -> None:
        """Обрабатывает загрузку документа пользователем."""

        user_id = message.from_user.id if message.from_user else 0
        if not self._is_user_allowed(user_id):
            return
        await self._enqueue_document(user_id, message)

    async def _handle_media_group(self, message: Message) -> None:
        """Обрабатывает пачку медиа (альбом): обрабатывает все документы в группе."""
        user_id = message.from_user.id if message.from_user else 0
        if not self._is_user_allowed(user_id):
            return
        group_id = str(message.media_group_id)
        buf = self._album_buffers.setdefault(group_id, [])
        buf.append(message)
        if group_id not in self._album_tasks:
            async def _debounced_flush() -> None:
                await asyncio.sleep(2.0)
                messages = self._album_buffers.pop(group_id, [])
                self._album_tasks.pop(group_id, None)
                if not messages:
                    return
                # Сообщаем пользователю один раз
                await messages[0].answer(text="Получен набор файлов. Начинается векторизация данных…")
                for m in messages:
                    if m.document or m.photo:
                        await self._enqueue_document(user_id, m)
                await messages[0].answer(text="Обработка набора поставлена в очередь.")

            self._album_tasks[group_id] = asyncio.create_task(_debounced_flush())

    async def _enqueue_document(self, user_id: int, message: Message) -> None:
        """Ставит документ в очередь пользователя и запускает воркер при необходимости."""

        if not user_id:
            user_id = 0
        
        ingestion_service: DocumentIngestionService = self._services["ingestion"]
        
        if message.document:
            file_size = message.document.file_size or 0
            filename = message.document.file_name or "unknown"
            estimated_time = ingestion_service.estimate_processing_time(file_size, filename)
            await message.answer(
                text=f"Файл получен: {filename}\nРазмер: {self._human_readable_size(file_size)}\nПримерное время обработки: {estimated_time}\nНачинается векторизация данных…"
            )
        elif message.photo:
            photo = message.photo[-1] if message.photo else None
            if photo:
                file_size = photo.file_size or 0
                estimated_time = ingestion_service.estimate_processing_time(file_size, "photo.jpg")
                await message.answer(
                    text=f"Фото получено\nРазмер: {self._human_readable_size(file_size)}\nПримерное время обработки: {estimated_time}\nНачинается векторизация данных…"
                )
            else:
                await message.answer(text="Фото получено. Начинается векторизация данных…")
        
        q = self._user_queues.setdefault(user_id, deque())
        q.append(message)
        await self._ensure_worker(user_id)

    async def _ensure_worker(self, user_id: int) -> None:
        """Запускает воркер обработки очереди пользователя, если он еще не запущен."""

        if user_id in self._user_workers:
            return
        self._user_workers.add(user_id)
        self._processing_users.add(user_id)

        async def _worker() -> None:
            ingestion_service: DocumentIngestionService = self._services["ingestion"]
            try:
                while True:
                    q = self._user_queues.get(user_id)
                    if not q:
                        break
                    try:
                        msg = q.popleft()
                    except IndexError:
                        break
                    try:
                        if msg.document:
                            await ingestion_service.ingest_from_message(message=msg, bot=self._bot)
                            await msg.answer(text="Обработка завершена. Можно задавать вопросы по данным.")
                        elif msg.photo:
                            await ingestion_service.ingest_photo_from_message(message=msg, bot=self._bot)
                            await msg.answer(text="Обработка фото завершена. Можно задавать вопросы по данным.")
                    except Exception:
                        await msg.answer(text="Ошибка при обработке файла. Попробуйте позже.")
                # Очистка пустых очередей
                if self._user_queues.get(user_id) and len(self._user_queues[user_id]) == 0:
                    self._user_queues.pop(user_id, None)
            finally:
                if user_id in self._processing_users:
                    self._processing_users.remove(user_id)
                self._user_workers.discard(user_id)

        asyncio.create_task(_worker())

    async def _handle_question(self, message: Message) -> None:
        """Отвечает на вопросы пользователя."""

        if not self._is_user_allowed(message.from_user.id if message.from_user else 0):
            return
        qa_service: QuestionAnsweringService = self._services["qa"]
        thinking = await message.answer(text="Думаю…")
        try:
            # Подготовим историю пользователя
            hist = self._get_history_pairs(message.from_user.id if message.from_user else 0)
            response = await asyncio.wait_for(
                qa_service.answer_question(query=message.text or "", history=hist), timeout=60
            )
        except asyncio.TimeoutError:
            await thinking.delete()
            await message.answer(text="Не удалось уложиться в 60 секунд. Попробуйте уточнить вопрос.")
            return
        except Exception:
            await thinking.delete()
            await message.answer(text="Ошибка при получении ответа. Попробуйте позже.")
            return
        await thinking.delete()
        safe = self._prepare_telegram_text(response)
        for chunk in safe:
            await message.answer(text=chunk)
        # Сохраняем ход диалога
        try:
            self._append_history(
                user_id=message.from_user.id if message.from_user else 0,
                question=message.text or "",
                answer=response or "",
            )
        except Exception:
            pass

    async def run(self) -> None:
        """Запускает процесс обработки обновлений."""

        # фоновая отправка статуса запуска пользователям из белого списка
        self._startup_task = asyncio.create_task(self._startup_notifier())
        web_task = asyncio.create_task(self._web_app.run())
        
        # фоновая калибровка модели эмбеддингов
        ingestion: DocumentIngestionService = self._services["ingestion"]
        asyncio.create_task(asyncio.to_thread(ingestion.calibrate_current_model_background))
        
        await self._dispatcher.start_polling(self._bot)
        await web_task

    def _prepare_telegram_text(self, text: str) -> list[str]:
        """Готовит текст для отправки в Telegram: экранирует и бьёт на части."""

        if not text:
            return ["Ответ не найден."]
        # сначала экранируем HTML
        sanitized = html.escape(text, quote=False)
        # затем конвертируем markdown-жирный в HTML-теги
        sanitized = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", sanitized, flags=re.DOTALL)
        sanitized = re.sub(r"__(.+?)__", r"<b>\1</b>", sanitized, flags=re.DOTALL)
        limit = 3500
        chunks = []
        start = 0
        while start < len(sanitized):
            end = min(start + limit, len(sanitized))
            chunks.append(sanitized[start:end])
            start = end
        return chunks

    def _history_limit(self) -> int:
        """Лимит пар истории из JSON (0..50), по умолчанию 10."""
        from .utils.config_utils import load_history_limit_from_store
        return load_history_limit_from_store(default=10)

    def _get_history_pairs(self, user_id: int) -> list[tuple[str, str]]:
        """Возвращает последние N пар истории для пользователя."""
        if not user_id:
            return []
        limit = self._history_limit()
        if limit <= 0:
            return []
        dq = self._dialog_history.get(user_id)
        if not dq:
            return []
        try:
            return list(dq)[-limit:]
        except Exception:
            return []

    def _append_history(self, user_id: int, question: str, answer: str) -> None:
        """Добавляет пару (вопрос, ответ) в историю пользователя с обрезкой по лимиту."""
        if not user_id:
            return
        limit = self._history_limit()
        if limit <= 0:
            return
        dq = self._dialog_history.get(user_id)
        if dq is None:
            dq = deque()
            self._dialog_history[user_id] = dq
        dq.append((question, answer))
        # Обрезаем историю, чтобы не росла бесконечно
        try:
            while len(dq) > max(limit, 1) * 2:
                dq.popleft()
        except Exception:
            pass

    def _allowed_users_list(self) -> list[int]:
        from .utils.config_utils import load_allowed_users_from_store, parse_allowed_users
        users = load_allowed_users_from_store()
        if users:
            return users
        # fallback к .env
        return parse_allowed_users(str(self._settings.allowed_users or ""))

    async def _startup_notifier(self) -> None:
        """Отправляет и обновляет статус запуска сервиса в Telegram."""
        users = self._allowed_users_list()
        if not users:
            return
        # отправляем первичное сообщение
        initial_lines = await self._collect_status_lines()
        from .utils.config_utils import get_public_web_url
        settings_url = get_public_web_url() or "http://localhost:8080/"
        text = (
            "Сервис бота - запущен\n"
            "Идет инициализация базы данных\n"
            + "\n".join(initial_lines)
            + f"\n\nПанель настроек: {settings_url}"
        )
        sent: Dict[int, int] = {}
        for uid in users:
            try:
                msg = await self._bot.send_message(chat_id=uid, text=text)
                sent[uid] = msg.message_id
            except Exception:
                continue
        # периодически обновляем до готовности
        while True:
            try:
                ready = await self._is_services_ready()
                if ready:
                    # финальное сообщение аналогично /start
                    ingestion: DocumentIngestionService = self._services["ingestion"]
                    docs = ingestion.document_count()
                    files = ingestion.file_count()
                    size_bytes = self._dir_size_bytes(self._settings.vector_store_path)
                    size_h = self._human_readable_size(size_bytes)
                    final_text = (
                        "Сервис бота - запущен\n"
                        "Сервис векторной бд - запущен\n\n"
                        f"В базе документов: {docs}. Файлов-источников: {files}.\n"
                        f"Размер векторной базы на диске: {size_h}.\n"
                        "Отправьте файлы для индексации. После загрузки задавайте вопросы по содержимому загруженных файлов.\n\n"
                        f"Панель настроек: {settings_url}"
                    )
                    for uid, mid in list(sent.items()):
                        try:
                            await self._bot.edit_message_text(chat_id=uid, message_id=mid, text=final_text, reply_markup=self._menu_markup())
                        except Exception:
                            pass
                    break
                lines = await self._collect_status_lines()
                upd_text = (
                    "Сервис бота - запущен\n"
                    "Идет инициализация базы данных\n"
                    + "\n".join(lines)
                    + f"\n\nПанель настроек: {settings_url}"
                )
                for uid, mid in list(sent.items()):
                    try:
                        await self._bot.edit_message_text(chat_id=uid, message_id=mid, text=upd_text)
                    except Exception:
                        pass
            except Exception:
                pass
            await asyncio.sleep(2.0)

    def _dir_size_bytes(self, path: str) -> int:
        """Возвращает суммарный размер файлов в директории (рекурсивно)."""
        try:
            total = 0
            if not path:
                return 0
            if not os.path.exists(path):
                return 0
            for root, _dirs, files in os.walk(path):
                for name in files:
                    fp = os.path.join(root, name)
                    try:
                        total += os.path.getsize(fp)
                    except Exception:
                        continue
            return total
        except Exception:
            return 0

    def _human_readable_size(self, size_bytes: int) -> str:
        """Форматирует размер в человекочитаемый вид (Б/КБ/МБ/ГБ)."""
        try:
            units = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
            size = float(size_bytes)
            idx = 0
            while size >= 1024.0 and idx < len(units) - 1:
                size /= 1024.0
                idx += 1
            if idx == 0:
                return f"{int(size)} {units[idx]}"
            # Округление до одного знака после запятой для МБ/ГБ/ТБ
            return f"{size:.1f} {units[idx]}"
        except Exception:
            return "0 Б"

    async def _collect_status_lines(self) -> list[str]:
        """Возвращает две строки статуса (Ollama и Chroma)."""
        lines: list[str] = []
        # Ollama status через локальный веб-эндпойнт (если есть прогресс pull)
        try:
            st = requests.get("http://localhost:8080/api/embeddings/pull_status", timeout=1).json().get("state", {})
            if st.get("running"):
                prog = int(st.get("progress") or 0)
                status = str(st.get("status") or "загрузка модели")
                lines.append(f"Ollama: {prog}% — {status}")
            else:
                ok = await asyncio.to_thread(self._probe_embeddings_once)
                lines.append("Ollama: готов" if ok else "Ollama: проверка соединения…")
        except Exception:
            ok = await asyncio.to_thread(self._probe_embeddings_once)
            lines.append("Ollama: готов" if ok else "Ollama: проверка соединения…")

        # Chroma status
        try:
            ingestion: DocumentIngestionService = self._services["ingestion"]
            docs = ingestion.document_count()
            files = ingestion.file_count()
            lines.append(f"Chroma: документов {docs}, файлов {files}")
        except Exception:
            lines.append("Chroma: инициализация…")

        # максимум 2 строки
        return lines[:2]

    def _probe_embeddings_once(self) -> bool:
        """Пробует один раз вызвать embeddings для проверки готовности Ollama."""
        try:
            settings = self._settings
            if not (settings.embeddings_endpoint and settings.embeddings_model):
                return True
            ep = settings.embeddings_endpoint.rstrip("/")
            if not ep.endswith("/api/embeddings"):
                ep = f"{ep}/api/embeddings"
            r = requests.post(ep, json={"model": settings.embeddings_model, "input": "ok"}, timeout=5)
            if r.status_code == 200:
                return True
        except Exception:
            return False
        return False

    def _is_user_allowed(self, user_id: int) -> bool:
        """Проверка пользователя по белому списку.

        Пустой список означает отсутствие ограничений.
        """
        try:
            allowed = set(self._allowed_users_list())
            return True if not allowed else (user_id in allowed)
        except Exception:
            return True


async def main() -> None:
    """Точка входа для запуска телеграм-бота."""

    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    # Загружаем настройки из JSON конфига с приоритетом над .env
    from .config_store import ConfigStore
    import os
    store_path = os.environ.get("APP_CONFIG_JSON", "/app/data/app-config.json")
    store = ConfigStore(store_path)
    json_config = store.load()
    
    # Обновляем настройки из JSON (с приоритетом JSON над .env)
    if "EMBEDDINGS_MODEL" in json_config and json_config["EMBEDDINGS_MODEL"]:
        settings.embeddings_model = json_config["EMBEDDINGS_MODEL"]
    if "OPENAI_API_KEY" in json_config and json_config["OPENAI_API_KEY"]:
        settings.openai_api_key = json_config["OPENAI_API_KEY"]
    if "OPENAI_BASE_URL" in json_config and json_config["OPENAI_BASE_URL"]:
        settings.openai_base_url = json_config["OPENAI_BASE_URL"]
    if "OPENAI_ORGANIZATION" in json_config and json_config["OPENAI_ORGANIZATION"]:
        settings.openai_organization = json_config["OPENAI_ORGANIZATION"]
    if "OPENAI_RESPONSE_MODEL" in json_config and json_config["OPENAI_RESPONSE_MODEL"]:
        settings.openai_response_model = json_config["OPENAI_RESPONSE_MODEL"]
    if "ALLOWED_USERS" in json_config and json_config["ALLOWED_USERS"]:
        settings.allowed_users = json_config["ALLOWED_USERS"]
    
    application = TelegramBotApplication(settings=settings)
    await application.run()


def run_cli() -> None:
    """Запускает бота для использования в качестве CLI-скрипта."""

    asyncio.run(main())


if __name__ == "__main__":
    run_cli()

