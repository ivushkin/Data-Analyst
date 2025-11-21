from __future__ import annotations

import os
from typing import Any, Dict, List

from ..config_store import ConfigStore


def get_public_web_url() -> str | None:
    """Возвращает публичный URL веб-панели или None, если он невалиден.

    Источники:
    1) env WEB_APP_PUBLIC_URL
    2) JSON APP_CONFIG_JSON -> WEB_APP_PUBLIC_URL
    """
    try:
        url = os.environ.get("WEB_APP_PUBLIC_URL", "").strip()
        if not url:
            store_path = os.environ.get("APP_CONFIG_JSON", "/app/data/app-config.json")
            cfg = ConfigStore(store_path).load()
            url = str(cfg.get("WEB_APP_PUBLIC_URL", "") or "").strip()
        if not url:
            return None
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return None
        if not parsed.netloc:
            return None
        return url
    except Exception:
        return None


def parse_allowed_users(raw: str | None) -> List[int]:
    """Парсит список разрешенных пользователей из строки с ID через запятую."""
    if not raw:
        return []
    result: List[int] = []
    for part in raw.split(","):
        p = (part or "").strip()
        if not p:
            continue
        try:
            result.append(int(p))
        except Exception:
            continue
    return result


def load_allowed_users_from_store() -> List[int]:
    """Загружает белый список пользователей из JSON-конфига."""
    try:
        store_path = os.environ.get("APP_CONFIG_JSON", "/app/data/app-config.json")
        cfg: Dict[str, Any] = ConfigStore(store_path).load()
        return parse_allowed_users(str(cfg.get("ALLOWED_USERS", "") or ""))
    except Exception:
        return []


def parse_history_limit(val: Any) -> int:
    """Парсит лимит истории из произвольного значения (0..50)."""
    try:
        x = int(val)
    except Exception:
        return 10
    if x < 0:
        x = 0
    if x > 50:
        x = 50
    return x


def load_history_limit_from_store(default: int = 10) -> int:
    """Загружает лимит истории из JSON-конфига с валидацией."""
    try:
        store_path = os.environ.get("APP_CONFIG_JSON", "/app/data/app-config.json")
        cfg: Dict[str, Any] = ConfigStore(store_path).load()
        if "HISTORY_MAX_PAIRS" not in cfg:
            return default
        return parse_history_limit(cfg.get("HISTORY_MAX_PAIRS"))
    except Exception:
        return default


