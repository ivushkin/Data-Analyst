from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import logging
import os

from ..config import Settings
from ..storage.vector import VectorStore
from ..config_store import ConfigStore


class QuestionAnsweringService:
    """Сервис для ответов на вопросы на основе векторного индекса."""

    def __init__(self, settings: Settings, vector_store: VectorStore):
        """Создает сервис с клиентом OpenAI и хранилищем."""

        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._vector_store = vector_store
        # Ретривер не кешируем: создаем свежий на каждый запрос, чтобы
        # избежать обращения к удаленной/переинициализированной коллекции Chroma
        
        # ConfigStore для динамической загрузки настроек
        store_path = os.environ.get("APP_CONFIG_JSON", "/app/data/app-config.json")
        self._config_store = ConfigStore(store_path)

    async def answer_question(self, query: str, history: list[tuple[str, str]] | None = None) -> str:
        """Формирует ответ на вопрос, используя Retrieval QA и краткую историю диалога.

        history: список пар (user_question, assistant_answer). Берутся последние N пар.
        """
        if not query or not query.strip() or query.strip().startswith("/"):
            return "Задайте осмысленный вопрос по загруженным документам."
        # Создаем retriever на каждый запрос, чтобы не держать ссылку на старую коллекцию
        retriever = self._vector_store.as_retriever(
            search_kwargs={"k": self._settings.retrieval_top_k}
        )
        try:
            documents = retriever.invoke(query)
        except Exception:
            self._logger.exception("Ошибка ретривера при поиске релевантных документов")
            return "Нет данных для ответа, загрузите документы."
        if not documents:
            return "Недостаточно данных в загруженных документах."
        # Подготавливаем строку истории (не более ~ 8-10 реплик, уже ограничено вызывающей стороной)
        history_text = ""
        if history:
            try:
                parts: list[str] = []
                for q, a in history:
                    q = (q or "").strip()
                    a = (a or "").strip()
                    if q:
                        parts.append(f"Пользователь: {q}")
                    if a:
                        parts.append(f"Ассистент: {a}")
                if parts:
                    history_text = "\n".join(parts)
            except Exception:
                history_text = ""
        base_prompt = PromptTemplate(
            template=(
                "Ты отвечаешь строго и только на основе предоставленного контекста. "
                "Если ответа в контексте нет, ответь: 'Недостаточно данных в загруженных документах.'\n\n"
                "История диалога (если есть):\n{chat_history}\n\n"
                "Требования к формату ответа:\n"
                "- простой текст, без Markdown и без HTML-тегов;\n"
                "- переносы строк только символом \\n;\n"
                "- не более 3500 символов;\n"
                "- не включай кодовые блоки и специальные разметки.\n\n"
                "Контекст:\n{context}\n\n"
                "Вопрос: {question}"
            ),
            input_variables=["context", "question", "chat_history"],
        )
        prompt = base_prompt.partial(chat_history=history_text)
        chain = RetrievalQA.from_chain_type(
            llm=self._create_llm(),
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
        )
        result = chain.invoke({"query": query})
        return result.get("result", "Ответ не найден.")

    def _create_llm(self):
        """Создает интерфейс для LLM с использованием клиента OpenAI с актуальными настройками."""

        from langchain_openai import ChatOpenAI
        
        # Загружаем актуальные настройки из JSON с приоритетом над начальными
        json_config = self._config_store.load()
        
        api_key = json_config.get("OPENAI_API_KEY") or self._settings.openai_api_key
        base_url = json_config.get("OPENAI_BASE_URL") or self._settings.openai_base_url
        organization = json_config.get("OPENAI_ORGANIZATION") or self._settings.openai_organization
        model = json_config.get("OPENAI_RESPONSE_MODEL") or self._settings.openai_response_model
        
        # Автоопределение правильного base_url (с /v1 или без)
        # LangChain автоматически добавляет /chat/completions к base_url
        base_url = self._detect_correct_base_url(base_url, api_key)
        
        self._logger.info(f"Создание LLM клиента с моделью: {model}, base_url: {base_url}")

        return ChatOpenAI(
            openai_api_key=api_key,
            openai_organization=organization,
            base_url=base_url,
            model=model,
        )
    
    def _detect_correct_base_url(self, base_url: str, api_key: str) -> str:
        """Определяет правильный base_url для LLM API (с /v1 или без)."""
        import requests
        
        if not base_url:
            return base_url
        
        base_url = base_url.rstrip("/")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        
        # Варианты для проверки
        variants = []
        if base_url.endswith("/v1"):
            # Если уже есть /v1, проверяем также вариант без него
            variants.append(base_url)
            variants.append(base_url[:-3])
        else:
            # Если нет /v1, проверяем оба варианта
            variants.append(base_url)
            variants.append(f"{base_url}/v1")
        
        # Проверяем какой вариант работает через models endpoint
        for variant in variants:
            try:
                models_url = f"{variant}/models"
                resp = requests.get(models_url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    self._logger.info(f"Определен рабочий base_url: {variant}")
                    return variant
            except Exception:
                continue
        
        # Если ни один не работает, возвращаем исходный
        self._logger.warning(f"Не удалось определить рабочий base_url, используется: {base_url}")
        return base_url


