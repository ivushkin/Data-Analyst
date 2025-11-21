import json
import os
from typing import Any, Dict, Optional

from .config import Settings


class ResolvedSettings:
    """Эффективные настройки приложения, объединяющие .env и JSON-конфиг."""

    def __init__(
        self,
        telegram_token: str,
        vector_store_path: str,
        chunk_size: int,
        chunk_overlap: int,
        retrieval_top_k: int,
        embeddings_provider: Optional[str],
        embeddings_endpoint: Optional[str],
        embeddings_model: Optional[str],
        openai_api_key: Optional[str],
        openai_base_url: Optional[str],
        openai_organization: Optional[str],
        openai_response_model: Optional[str],
        allowed_users: Optional[str],
        history_max_pairs: int,
    ) -> None:
        self.telegram_token = telegram_token
        self.vector_store_path = vector_store_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.retrieval_top_k = retrieval_top_k
        self.embeddings_provider = embeddings_provider
        self.embeddings_endpoint = embeddings_endpoint
        self.embeddings_model = embeddings_model
        self.openai_api_key = openai_api_key
        self.openai_base_url = openai_base_url
        self.openai_organization = openai_organization
        self.openai_response_model = openai_response_model
        self.allowed_users = allowed_users or ""
        self.history_max_pairs = int(history_max_pairs)


class ConfigStore:
    """Хранилище пользовательских настроек в JSON-файле."""

    def __init__(self, path: str) -> None:
        self._path = path

    def load(self) -> Dict[str, Any]:
        """Загружает конфиг из JSON, при отсутствии возвращает пустой словарь."""

        if not os.path.exists(self._path):
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save(self, data: Dict[str, Any]) -> None:
        """Сохраняет конфиг в JSON, создавая директории при необходимости."""

        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def load_effective_settings(env_settings: Settings, store: ConfigStore) -> ResolvedSettings:
    """Формирует итоговые настройки из .env и JSON-конфига."""

    data = store.load()
    
    def prefer_json(json_val, env_val):
        """Возвращает json_val, если он задан и не пуст, иначе env_val."""
        if json_val is None:
            return env_val
        if isinstance(json_val, str) and json_val.strip() == "":
            return env_val
        return json_val

    def parse_history_limit(val: Any) -> int:
        """Парсит и валидирует лимит истории (0..50), по умолчанию 10."""
        try:
            x = int(val)
        except Exception:
            return 10
        if x < 0:
            x = 0
        if x > 50:
            x = 50
        return x
    return ResolvedSettings(
        telegram_token=env_settings.telegram_token,
        # Параметры, отсутствующие на странице настроек: только из .env
        vector_store_path=str(env_settings.vector_store_path),
        chunk_size=int(env_settings.chunk_size),
        chunk_overlap=int(env_settings.chunk_overlap),
        retrieval_top_k=int(env_settings.retrieval_top_k),
        embeddings_provider=env_settings.embeddings_provider,
        embeddings_endpoint=env_settings.embeddings_endpoint,
        # Параметры со страницы настроек: JSON приоритет иначе env
        embeddings_model=prefer_json(data.get("EMBEDDINGS_MODEL"), env_settings.embeddings_model),
        openai_api_key=prefer_json(data.get("OPENAI_API_KEY"), env_settings.openai_api_key),
        openai_base_url=prefer_json(data.get("OPENAI_BASE_URL"), env_settings.openai_base_url),
        openai_organization=prefer_json(data.get("OPENAI_ORGANIZATION"), env_settings.openai_organization),
        openai_response_model=prefer_json(data.get("OPENAI_RESPONSE_MODEL"), env_settings.openai_response_model),
        allowed_users=prefer_json(data.get("ALLOWED_USERS"), env_settings.allowed_users),
        history_max_pairs=parse_history_limit(data.get("HISTORY_MAX_PAIRS")),
    )


