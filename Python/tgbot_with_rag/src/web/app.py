import asyncio
import os
from typing import Any, Dict, List, Optional
import requests
import docker

from aiohttp import web

from ..config import Settings
from ..config_store import ConfigStore, load_effective_settings


class SettingsWebApp:
    """Простой веб-сервер для управления настройками."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        self._host = host
        self._port = port
        self._app = web.Application()
        self._store_path = os.environ.get("APP_CONFIG_JSON", "/app/data/app-config.json")
        self._store = ConfigStore(self._store_path)
        # Предзагрузка статических пресетов эмбеддингов
        self._embed_presets: List[Dict[str, Any]] = []
        self._load_embed_presets()
        # Состояние загрузки модели эмбеддингов
        self._pull_state: Dict[str, Any] = {
            "running": False,
            "progress": 0,
            "status": "",
            "error": None,
            "model": None,
        }
        self._routes()

    def _routes(self) -> None:
        self._app.router.add_get("/", self._index)
        self._app.router.add_get("/api/config", self._get_config)
        self._app.router.add_post("/api/config", self._set_config)
        self._app.router.add_post("/api/restart", self._restart)
        self._app.router.add_get("/api/llm_models", self._llm_models)
        self._app.router.add_get("/api/embedding_presets", self._embedding_presets)
        self._app.router.add_get("/static/{path:.*}", self._static)
        # Управление загрузкой эмбеддинг-модели (Ollama)
        self._app.router.add_post("/api/embeddings/pull", self._embeddings_pull)
        self._app.router.add_get("/api/embeddings/pull_status", self._embeddings_pull_status)
        # Стриминг логов Docker
        self._app.router.add_get("/api/docker/logs", self._docker_logs)

    async def _index(self, request: web.Request) -> web.Response:
        settings = Settings()
        eff = load_effective_settings(settings, self._store)
        html = self._render_index(eff)
        return web.Response(text=html, content_type="text/html")

    async def _get_config(self, request: web.Request) -> web.Response:
        data = self._store.load()
        return web.json_response(data)

    async def _set_config(self, request: web.Request) -> web.Response:
        body = await request.json()
        assert isinstance(body, dict)
        # Подготовим данные для сравнения и уведомления
        before = self._store.load()
        self._store.save(body)
        try:
            await self._notify_config_changes(before, body)
        except Exception:
            pass
        return web.json_response({"ok": True})

    async def _restart(self, request: web.Request) -> web.Response:
        try:
            cfg = self._store.load()
            model = cfg.get("EMBEDDINGS_MODEL") or ""
            endpoint = cfg.get("EMBEDDINGS_ENDPOINT") or "http://ollama:11434/api/embeddings"
            if model:
                base = endpoint.rstrip("/")
                # Убираем /api/embeddings или /embeddings, чтобы получить базовый URL
                if base.endswith("/api/embeddings"):
                    base = base[: -len("/api/embeddings")]
                elif base.endswith("/embeddings"):
                    base = base[: -len("/embeddings")]
                try:
                    requests.post(f"{base}/api/pull", json={"name": model}, timeout=8)
                except Exception:
                    pass
        finally:
            asyncio.get_event_loop().call_later(0.5, lambda: os._exit(0))
        return web.json_response({"ok": True, "message": "Перезапуск..."})

    async def _llm_models(self, request: web.Request) -> web.Response:
        settings = Settings()
        eff = load_effective_settings(settings, self._store)
        base_url = (eff.openai_base_url or "").rstrip("/")
        api_key = eff.openai_api_key or ""
        if not base_url:
            return web.json_response({"ok": False, "error": "OPENAI_BASE_URL пуст"}, status=400)
        
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        
        # Пробуем разные варианты endpoints для автоопределения протокола
        endpoints_to_try = []
        
        if base_url.endswith("/v1"):
            endpoints_to_try.append(f"{base_url}/models")
        else:
            endpoints_to_try.append(f"{base_url}/v1/models")
            endpoints_to_try.append(f"{base_url}/models")
        
        last_error = None
        for url in endpoints_to_try:
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    return web.json_response({"ok": True, "data": data})
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
            except Exception as e:
                last_error = str(e)
                continue
        
        return web.json_response({"ok": False, "error": last_error or "Не удалось получить список моделей"}, status=500)

    

    async def _static(self, request: web.Request) -> web.Response:
        path = request.match_info.get("path", "")
        file_path = os.path.join("/app/web", path)
        if not os.path.isfile(file_path):
            raise web.HTTPNotFound()
        return web.FileResponse(file_path)

    def _render_index(self, eff) -> str:
        template_path = "/app/web/template.html"
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                tpl = f.read()
        except Exception:
            return "Шаблон не найден"

        def _val(x: Any) -> str:
            return str(x or "")

        def _mask_token(token: str) -> str:
            token = token or ""
            n = len(token)
            if n <= 12:
                return "*" * n
            return token[:6] + ("*" * (n - 12)) + token[-6:]

        replacements = {
            "__OPENAI_BASE_URL__": _val(eff.openai_base_url),
            "__OPENAI_API_KEY__": _val(eff.openai_api_key),
            "__OPENAI_API_KEY_MASKED__": _mask_token(_val(eff.openai_api_key)),
            "__OPENAI_ORGANIZATION__": _val(eff.openai_organization),
            "__OPENAI_RESPONSE_MODEL__": _val(eff.openai_response_model),
            "__EMBEDDINGS_MODEL__": _val(eff.embeddings_model),
            "__EMBEDDINGS_ENDPOINT__": _val(eff.embeddings_endpoint),
            "__VECTOR_STORE_PATH__": _val(eff.vector_store_path),
            "__CHUNK_SIZE__": _val(eff.chunk_size),
            "__CHUNK_OVERLAP__": _val(eff.chunk_overlap),
            "__RETRIEVAL_TOP_K__": _val(eff.retrieval_top_k),
            "__ALLOWED_USERS__": _val(getattr(eff, "allowed_users", "")),
            "__HISTORY_MAX_PAIRS__": _val(getattr(eff, "history_max_pairs", 10)),
        }
        for k, v in replacements.items():
            tpl = tpl.replace(k, v)
        return tpl

    async def _embedding_presets(self, request: web.Request) -> web.Response:
        return web.json_response({"ok": True, "presets": self._embed_presets})

    def _load_embed_presets(self) -> None:
        path = os.environ.get("EMBED_PRESETS_JSON", "/app/web/embed_presets.json")
        try:
            import json as _json
            with open(path, "r", encoding="utf-8") as f:
                data = _json.load(f)
            self._embed_presets = data if isinstance(data, list) else []
        except Exception:
            self._embed_presets = []

    async def _embeddings_pull(self, request: web.Request) -> web.Response:
        """Старт скачивания модели эмбеддингов в Ollama с отслеживанием прогресса.

        Тело запроса: {"name": "qwen3-embedding:0.6b"}
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if self._pull_state.get("running"):
            logger.warning("Попытка запустить загрузку, но она уже выполняется")
            return web.json_response({"ok": False, "error": "Загрузка уже выполняется"}, status=409)
        try:
            body = await request.json()
            assert isinstance(body, dict)
            model: str = str(body.get("name") or "").strip()
            if not model:
                logger.error("Не указана модель для загрузки")
                return web.json_response({"ok": False, "error": "Не указана модель"}, status=400)

            logger.info(f"Запуск загрузки модели эмбеддингов: {model}")

            # Вычисляем базовый URL Ollama из настроек
            cfg = self._store.load()
            endpoint = cfg.get("EMBEDDINGS_ENDPOINT") or "http://ollama:11434/api/embeddings"
            base = (endpoint or "").rstrip("/")
            
            # Убираем /api/embeddings или /embeddings, чтобы получить базовый URL
            if base.endswith("/api/embeddings"):
                base = base[: -len("/api/embeddings")]
            elif base.endswith("/embeddings"):
                base = base[: -len("/embeddings")]
            
            logger.info(f"Базовый URL Ollama: {base}")

            # Сохраняем модель в конфиг сразу, чтобы использовать её для будущей индексации
            cfg["EMBEDDINGS_MODEL"] = model
            self._store.save(cfg)

            # Обновляем состояние и запускаем фоновую задачу скачивания
            self._pull_state.update({
                "running": True,
                "progress": 0,
                "status": "Старт загрузки",
                "error": None,
                "model": model,
            })

            async def _task() -> None:
                import json as _json
                def _pull_sync() -> None:
                    try:
                        pull_url = f"{base}/api/pull"
                        logger.info(f"Отправка запроса на pull: {pull_url}")
                        resp = requests.post(pull_url, json={"name": model}, stream=True, timeout=600)
                        logger.info(f"Статус ответа: {resp.status_code}")
                        
                        if resp.status_code != 200:
                            error_text = resp.text
                            logger.error(f"Ошибка при запросе pull: {error_text}")
                            self._pull_state.update({"error": f"HTTP {resp.status_code}: {error_text}"})
                            return
                        
                        for raw in resp.iter_lines():
                            if not raw:
                                continue
                            try:
                                obj = _json.loads(raw.decode("utf-8"))
                                logger.debug(f"Pull response: {obj}")
                            except Exception as e:
                                logger.error(f"Ошибка при разборе JSON: {e}, данные: {raw}")
                                continue
                            
                            status = obj.get("status") or ""
                            completed: Optional[int] = obj.get("completed")
                            total: Optional[int] = obj.get("total")
                            progress = 0
                            
                            if isinstance(completed, int) and isinstance(total, int) and total > 0:
                                progress = int((completed / total) * 100)
                            
                            logger.info(f"Прогресс загрузки {model}: {progress}% - {status}")
                            
                            self._pull_state.update({
                                "status": status,
                                "progress": progress,
                            })
                            
                            if obj.get("error"):
                                error = str(obj.get("error"))
                                logger.error(f"Ошибка от Ollama: {error}")
                                self._pull_state.update({"error": error})
                                return
                        
                        # Успешное завершение
                        logger.info(f"Загрузка модели {model} завершена успешно")
                        self._pull_state.update({
                            "status": "Загрузка завершена",
                            "progress": 100,
                        })
                        
                    except Exception as e:
                        logger.error(f"Исключение при загрузке модели: {e}", exc_info=True)
                        self._pull_state.update({"error": str(e)})
                    finally:
                        self._pull_state.update({"running": False})

                await asyncio.to_thread(_pull_sync)

            asyncio.get_event_loop().create_task(_task())
            logger.info("Фоновая задача загрузки модели запущена")
            return web.json_response({"ok": True})
        except Exception as e:
            logger.error(f"Ошибка при запуске загрузки модели: {e}", exc_info=True)
            self._pull_state.update({"running": False, "error": str(e)})
            return web.json_response({"ok": False, "error": str(e)}, status=500)

    async def _embeddings_pull_status(self, request: web.Request) -> web.Response:
        st = self._pull_state.copy()
        st.setdefault("running", False)
        st.setdefault("progress", 0)
        st.setdefault("status", "")
        st.setdefault("error", None)
        st.setdefault("model", None)
        return web.json_response({"ok": True, "state": st})

    async def _docker_logs(self, request: web.Request) -> web.StreamResponse:
        import logging
        import asyncio
        import queue
        import threading
        logger = logging.getLogger(__name__)
        logger.info("Получен запрос на стрим логов Docker")
        
        response = web.StreamResponse()
        response.headers["Content-Type"] = "text/event-stream"
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Connection"] = "keep-alive"
        response.headers["X-Accel-Buffering"] = "no"
        await response.prepare(request)

        try:
            def _get_containers():
                client = docker.from_env()
                containers_dict = {}
                
                try:
                    all_containers = client.containers.list()
                    logger.info(f"Найдено контейнеров: {len(all_containers)}")
                    
                    for c in all_containers:
                        labels = c.labels
                        service = labels.get('com.docker.compose.service')
                        
                        # Ищем контейнер бота
                        if service == 'bot' or 'tgbot-with-rag' in (c.image.tags[0] if c.image.tags else ''):
                            containers_dict['bot'] = c
                            logger.info(f"Контейнер bot найден: {c.name}")
                        
                        # Ищем контейнер ollama
                        if service == 'ollama' or 'ollama/ollama' in (c.image.tags[0] if c.image.tags else ''):
                            containers_dict['ollama'] = c
                            logger.info(f"Контейнер ollama найден: {c.name}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при поиске контейнеров: {e}")
                
                return containers_dict
            
            containers = await asyncio.to_thread(_get_containers)
            
            if not containers:
                msg = "data: Контейнеры не найдены. Проверьте права доступа к Docker socket.\n\n"
                await response.write(msg.encode("utf-8"))
                logger.error("Контейнеры не найдены")
                return response

            logger.info(f"Отправка логов из контейнеров: {list(containers.keys())}")
            
            # Отправляем последние 50 строк логов из каждого контейнера в обратном порядке
            def _get_initial_logs():
                all_logs = []
                for service_name, container in containers.items():
                    try:
                        logs = container.logs(tail=50).decode("utf-8", errors="ignore").strip()
                        for line in logs.split('\n'):
                            if line.strip():
                                all_logs.append(f"[{service_name}] {line.strip()}")
                    except Exception as e:
                        logger.error(f"Ошибка при чтении начальных логов {service_name}: {e}")
                return all_logs
            
            initial_logs = await asyncio.to_thread(_get_initial_logs)
            if initial_logs:
                # Отправляем в обратном порядке - самые новые первыми
                for log_line in reversed(initial_logs):
                    message = f"data: {log_line}\n\n"
                    await response.write(message.encode("utf-8"))
                    await response.drain()
                logger.info(f"Отправлено {len(initial_logs)} начальных строк логов")
            
            # Создаем очередь для объединения логов из нескольких контейнеров
            log_queue = queue.Queue()
            stop_event = threading.Event()
            
            def _stream_container_logs(service_name, container):
                try:
                    for line in container.logs(stream=True, follow=True):
                        if stop_event.is_set():
                            break
                        try:
                            decoded = line.decode("utf-8", errors="ignore").strip()
                            if decoded:
                                log_queue.put(f"[{service_name}] {decoded}")
                        except Exception as e:
                            logger.error(f"Ошибка при декодировании строки {service_name}: {e}")
                except Exception as e:
                    logger.error(f"Ошибка при стриминге логов {service_name}: {e}")
            
            # Запускаем потоки для каждого контейнера
            threads = []
            for service_name, container in containers.items():
                thread = threading.Thread(target=_stream_container_logs, args=(service_name, container))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            # Читаем из очереди и отправляем клиенту
            try:
                while True:
                    try:
                        log_line = log_queue.get(timeout=1)
                        message = f"data: {log_line}\n\n"
                        await response.write(message.encode("utf-8"))
                        await response.drain()
                        await asyncio.sleep(0)
                    except queue.Empty:
                        # Проверяем, активно ли соединение
                        await asyncio.sleep(0.1)
                        continue
            except asyncio.CancelledError:
                logger.info("Клиент отключился от стрима логов")
            except Exception as e:
                logger.info(f"Стрим логов прерван: {e}")
            finally:
                stop_event.set()
                for thread in threads:
                    thread.join(timeout=1)

        except docker.errors.DockerException as e:
            logger.error(f"Ошибка Docker API: {e}")
            try:
                error_msg = f"data: Ошибка Docker API: {str(e)}\n\n"
                await response.write(error_msg.encode("utf-8"))
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Ошибка при чтении логов: {e}", exc_info=True)
            try:
                error_msg = f"data: Ошибка при чтении логов: {str(e)}\n\n"
                await response.write(error_msg.encode("utf-8"))
            except Exception:
                pass

        return response

    async def run(self) -> None:
        runner = web.AppRunner(self._app)
        await runner.setup()
        site = web.TCPSite(runner, self._host, self._port)
        await site.start()
        # Фоновая попытка скачать модель эмбеддингов при старте
        async def _bg_pull_embeddings() -> None:
            try:
                cfg = self._store.load()
                model = cfg.get("EMBEDDINGS_MODEL") or ""
                endpoint = cfg.get("EMBEDDINGS_ENDPOINT") or "http://ollama:11434/api/embeddings"
                if not model:
                    return
                base = endpoint.rstrip("/")
                # Убираем /api/embeddings или /embeddings, чтобы получить базовый URL
                if base.endswith("/api/embeddings"):
                    base = base[: -len("/api/embeddings")]
                elif base.endswith("/embeddings"):
                    base = base[: -len("/embeddings")]
                try:
                    requests.post(f"{base}/api/pull", json={"name": model}, timeout=8)
                except Exception:
                    pass
            except Exception:
                pass
        asyncio.get_event_loop().create_task(_bg_pull_embeddings())
        while True:
            await asyncio.sleep(3600)


    async def _notify_config_changes(self, old: Dict[str, Any], new: Dict[str, Any]) -> None:
        """Отправляет уведомления в Telegram о изменённых параметрах.

        Сообщение формируется по шаблону из запроса. Отправка идет каждому
        пользователю из списка `ALLOWED_USERS` (ID через запятую).
        """
        try:
            import itertools
            # определим список адресатов
            allowed_raw = str(new.get("ALLOWED_USERS", old.get("ALLOWED_USERS", "")) or "")
            recipients = []
            for part in allowed_raw.split(","):
                p = part.strip()
                if not p:
                    continue
                try:
                    recipients.append(int(p))
                except Exception:
                    continue
            if not recipients:
                return

            # токен бота берём из env (он не хранится в JSON), Settings подтянет из .env
            settings = Settings()
            token = settings.telegram_token
            if not token:
                return

            # описания параметров для сообщения
            descriptions: Dict[str, str] = {
                "OPENAI_BASE_URL": "Базовый URL LLM API",
                "OPENAI_API_KEY": "API-ключ для доступа к провайдеру",
                "OPENAI_ORGANIZATION": "Идентификатор организации провайдера",
                "OPENAI_RESPONSE_MODEL": "LLM модель для генерации ответов",
                "EMBEDDINGS_MODEL": "Модель эмбеддингов в Ollama",
                "ALLOWED_USERS": "Белый список пользователей, которым разрешён доступ",
            }

            # вычислим отличающиеся ключи (только те, что мы показываем)
            interesting = set(descriptions.keys())
            changed_keys = [k for k in interesting if (old.get(k) != new.get(k))]
            if not changed_keys:
                return

            # функция отправки одного сообщения через Telegram Bot API
            import requests as _rq
            def _send(chat_id: int, text: str) -> None:
                try:
                    _rq.post(
                        f"https://api.telegram.org/bot{token}/sendMessage",
                        json={"chat_id": chat_id, "text": text},
                        timeout=10,
                    )
                except Exception:
                    pass

            # формируем и шлём
            for key in changed_keys:
                title = key
                desc = descriptions.get(key, "")
                old_val = old.get(key, "")
                new_val = new.get(key, "")
                if key == "OPENAI_API_KEY":
                    # не раскрываем ключ целиком
                    def _mask(s: Any) -> str:
                        s = str(s or "")
                        n = len(s)
                        if n <= 12:
                            return "*" * n
                        return s[:6] + ("*" * (n - 12)) + s[-6:]
                    old_val = _mask(old_val)
                    new_val = _mask(new_val)
                
                # Особое уведомление для смены модели LLM
                if key == "OPENAI_RESPONSE_MODEL":
                    text = (
                        f"Модель LLM изменена\n\n"
                        f"{desc}\n\n"
                        f"Предыдущая модель: {old_val or 'не задана'}\n"
                        f"Новая модель: {new_val or 'не задана'}\n\n"
                        f"Бот теперь использует новую модель для генерации ответов."
                    )
                else:
                    text = (
                        f"Изменился параметр: {title}\n"
                        f"Описание: {desc}\n"
                        f"-----\n"
                        f"Старое значение: {old_val}\n"
                        f"Новое значение: {new_val}"
                    )
                for uid in recipients:
                    await asyncio.to_thread(_send, uid, text)
        except Exception:
            # не мешаем сохранению настроек
            pass
