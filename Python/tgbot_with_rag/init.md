# Инструкция по установке и запуску проекта

## Описание

Telegram-бот с RAG технологией для работы с документами:
- Индексация PDF, DOCX, XLSX, изображений
- Ответы на вопросы по содержимому
- Локальные модели эмбеддингов через Ollama
- Облачные или локальные LLM для генерации ответов

---

## Общие требования

- 8 ГБ RAM (рекомендуется 16 ГБ)
- 10 ГБ свободного места на диске
- Telegram Bot Token (получить через @BotFather)
- API ключ Cloud.ru (или локальная LLM через LM Studio)

## Что вам понадобится

- Архив с проектом (будет предоставлен)
- Telegram аккаунт
- Cloud.ru аккаунт (для облачных моделей) или LM Studio (для локальных)

---

## Выберите вашу операционную систему

- [macOS](#установка-для-macos)
- [Windows](#установка-для-windows)
- [Ubuntu/Debian](#установка-для-ubuntudebian)
- [Arch Linux](#установка-для-arch-linux)

---

## Установка для macOS

### Шаг 1: Установка Docker

**Вариант А: Docker Desktop (рекомендуется)**

1. Скачайте Docker Desktop под вашу архитектуру (Intel/Apple Silicon): https://www.docker.com/products/docker-desktop

2. Откройте скачанный `.dmg` файл

3. Перетащите Docker в папку Applications

4. Запустите Docker из Applications

5. Дождитесь полного запуска (иконка в меню станет активной)

**Вариант Б: OrbStack (легкая альтернатива)**

1. Установите через Homebrew:
   ```bash
   brew install orbstack
   ```
   
   Или скачайте с https://orbstack.dev/

2. Запустите OrbStack

3. Следуйте инструкциям первого запуска

### Шаг 2: Установка Poppler (опционально)

**Что делает Poppler:**
Poppler - это библиотека для работы с PDF файлами. Используется для:
- Извлечения метаданных из PDF (количество страниц, автор, дата)
- Конвертации PDF в изображения для OCR (распознавания текста на сканах)
- Обработки защищенных и сложных PDF документов

**Нужно ли устанавливать:**
- НЕ обязательно - бот работает без Poppler
- Рекомендуется, если будете загружать сканированные PDF или изображения с текстом
- Без Poppler: работает извлечение текста из обычных PDF через PyPDF

**Установка:**
```bash
brew install poppler
```

Проверка:
```bash
pdfinfo -v
```

### Шаг 3: Распаковка проекта

1. Распакуйте полученный архив проекта
2. Откройте терминал и перейдите в папку:
   ```bash
   cd /путь/к/tgbot_with_rag
   ```

### Шаг 4: Создание .env файла

Скопируйте файл-пример:
```bash
cp .env.example .env
```

Откройте для редактирования:

```bash
open -e .env
```

Заполните необходимые значения:
```env
TELEGRAM_TOKEN=ваш_токен_от_BotFather
EMBEDDINGS_PROVIDER=ollama
EMBEDDINGS_ENDPOINT=http://ollama:11434
EMBEDDINGS_MODEL=bge-m3
OPENAI_API_KEY=ваш_ключ_cloud_ru
OPENAI_BASE_URL=https://foundation-models.api.cloud.ru/v1
OPENAI_RESPONSE_MODEL=openai/gpt-oss-120b
VECTOR_STORE_PATH=/data/chroma
CHUNK_SIZE=800
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=4
ALLOWED_USERS=ваш_telegram_user_id
```

### Шаг 5: Запуск проекта

**Через Docker Compose:**
```bash
docker compose build
docker compose up -d
```

**Через Makefile (удобнее):**
```bash
make build && make up
```

### Шаг 6: Проверка

Откройте браузер: http://localhost:8080

Проверьте статус:
```bash
docker compose ps
```

Логи:
```bash
docker compose logs -f bot
```

---

## Установка для Windows

### Шаг 1: Установка Docker Desktop

1. Скачайте Docker Desktop: https://www.docker.com/products/docker-desktop

2. Запустите установщик

3. Включите WSL 2 при появлении запроса

4. Перезагрузите компьютер после установки

5. Запустите Docker Desktop

6. Дождитесь полного запуска

Проверка в PowerShell:
```powershell
docker --version
docker compose version
```

### Шаг 2: Установка Make для Windows (опционально)

Для использования команд `make` на Windows установите один из вариантов:

**Вариант 1: Chocolatey**
```powershell
# Установите Chocolatey (если не установлен):
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Установите Make:
choco install make
```

**Вариант 2: Git Bash**
Make уже включен в Git для Windows. Используйте Git Bash вместо PowerShell.

**Вариант 3: Без Make**
Просто используйте команды `docker compose` напрямую вместо `make`.

### Шаг 3: Установка Poppler (опционально)

**Что делает Poppler:**
Poppler - это библиотека для работы с PDF файлами. Используется для:
- Извлечения метаданных из PDF (количество страниц, автор, дата)
- Конвертации PDF в изображения для OCR (распознавания текста на сканах)
- Обработки защищенных и сложных PDF документов

**Нужно ли устанавливать:**
- НЕ обязательно - бот работает без Poppler
- Рекомендуется, если будете загружать сканированные PDF или изображения с текстом
- Без Poppler: работает извлечение текста из обычных PDF через PyPDF

**Установка (если нужно):**

1. Скачайте: https://github.com/oschwartz10612/poppler-windows/releases/
2. Распакуйте в `C:\Program Files\poppler`
3. Добавьте в PATH: `C:\Program Files\poppler\Library\bin`
4. Перезапустите PowerShell и проверьте: `pdfinfo -v`

### Шаг 4: Распаковка проекта

1. Распакуйте полученный архив проекта
2. Откройте PowerShell и перейдите в папку:
   ```powershell
   cd C:\путь\к\tgbot_with_rag
   ```

### Шаг 5: Создание .env файла

Скопируйте файл-пример:
```powershell
copy .env.example .env
```

Откройте для редактирования:

```powershell
notepad .env
```

Заполните необходимые значения:
```env
TELEGRAM_TOKEN=ваш_токен_от_BotFather
EMBEDDINGS_PROVIDER=ollama
EMBEDDINGS_ENDPOINT=http://ollama:11434
EMBEDDINGS_MODEL=bge-m3
OPENAI_API_KEY=ваш_ключ_cloud_ru
OPENAI_BASE_URL=https://foundation-models.api.cloud.ru/v1
OPENAI_RESPONSE_MODEL=openai/gpt-oss-120b
VECTOR_STORE_PATH=/data/chroma
CHUNK_SIZE=800
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=4
ALLOWED_USERS=ваш_telegram_user_id
```

**Важные параметры:**
- `CHUNK_SIZE` - размер фрагмента текста для векторизации
- `CHUNK_OVERLAP` - перекрытие между фрагментами
- `RETRIEVAL_TOP_K` - количество фрагментов для контекста ответа

Эти параметры можно менять только через .env файл.

### Шаг 6: Запуск проекта

**Через Docker Compose:**
```powershell
docker compose build
docker compose up -d
```

**Через Make (если установлен):**
```bash
# В Git Bash:
make build && make up
```

### Шаг 7: Проверка

Откройте браузер: http://localhost:8080

Проверка в PowerShell:
```powershell
docker compose ps
docker compose logs -f bot
```

---

## Установка для Ubuntu/Debian

### Шаг 1: Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

### Шаг 2: Установка Docker

```bash
# Удаление старых версий
sudo apt remove docker docker-engine docker.io containerd runc

# Установка зависимостей
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Добавление GPG ключа Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Добавление репозитория
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Применение изменений
newgrp docker
```

Проверка:
```bash
docker --version
docker compose version
```

### Шаг 3: Установка Poppler (опционально)

**Что делает Poppler:**
Poppler - это библиотека для работы с PDF файлами. Используется для:
- Извлечения метаданных из PDF (количество страниц, автор, дата)
- Конвертации PDF в изображения для OCR (распознавания текста на сканах)
- Обработки защищенных и сложных PDF документов

**Нужно ли устанавливать:**
- НЕ обязательно - бот работает без Poppler
- Рекомендуется, если будете загружать сканированные PDF или изображения с текстом
- Без Poppler: работает извлечение текста из обычных PDF через PyPDF

**Установка (если нужно):**
```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr tesseract-ocr-rus
```

Проверка:
```bash
pdfinfo -v
```

### Шаг 4: Распаковка проекта

1. Распакуйте полученный архив проекта
2. Откройте терминал и перейдите в папку:
   ```bash
   cd /путь/к/tgbot_with_rag
   ```

### Шаг 5: Создание .env файла

Скопируйте файл-пример:
```bash
cp .env.example .env
```

Откройте для редактирования:

```bash
nano .env
```

Содержимое:
```env
TELEGRAM_TOKEN=ваш_токен_от_BotFather
EMBEDDINGS_PROVIDER=ollama
EMBEDDINGS_ENDPOINT=http://ollama:11434
EMBEDDINGS_MODEL=bge-m3
OPENAI_API_KEY=ваш_ключ_cloud_ru
OPENAI_BASE_URL=https://foundation-models.api.cloud.ru/v1
OPENAI_RESPONSE_MODEL=openai/gpt-oss-120b
VECTOR_STORE_PATH=/data/chroma
CHUNK_SIZE=800
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=4
ALLOWED_USERS=ваш_telegram_user_id
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Шаг 6: Запуск проекта

```bash
docker compose build
docker compose up -d
```

Или через Makefile:
```bash
make build && make up
```

### Шаг 7: Проверка

Откройте браузер: http://localhost:8080

Логи:
```bash
docker compose logs -f bot
```

---

## Установка для Arch Linux

### Шаг 1: Обновление системы

```bash
sudo pacman -Syu
```

### Шаг 2: Установка Docker

```bash
# Установка Docker
sudo pacman -S docker docker-compose

# Запуск и автозапуск Docker
sudo systemctl enable docker
sudo systemctl start docker

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Применение изменений (перелогиньтесь или выполните)
newgrp docker
```

Проверка:
```bash
docker --version
docker compose version
```

### Шаг 3: Установка Poppler (опционально)

**Что делает Poppler:**
Poppler - это библиотека для работы с PDF файлами. Используется для:
- Извлечения метаданных из PDF (количество страниц, автор, дата)
- Конвертации PDF в изображения для OCR (распознавания текста на сканах)
- Обработки защищенных и сложных PDF документов

**Нужно ли устанавливать:**
- НЕ обязательно - бот работает без Poppler
- Рекомендуется, если будете загружать сканированные PDF или изображения с текстом
- Без Poppler: работает извлечение текста из обычных PDF через PyPDF

**Установка (если нужно):**
```bash
sudo pacman -S poppler tesseract tesseract-data-rus
```

Проверка:
```bash
pdfinfo -v
```

### Шаг 4: Распаковка проекта

1. Распакуйте полученный архив проекта
2. Откройте терминал и перейдите в папку:
   ```bash
   cd /путь/к/tgbot_with_rag
   ```

### Шаг 5: Создание .env файла

Скопируйте файл-пример:
```bash
cp .env.example .env
```

Откройте для редактирования:

```bash
nano .env
```

Содержимое:
```env
TELEGRAM_TOKEN=ваш_токен_от_BotFather
EMBEDDINGS_PROVIDER=ollama
EMBEDDINGS_ENDPOINT=http://ollama:11434
EMBEDDINGS_MODEL=bge-m3
OPENAI_API_KEY=ваш_ключ_cloud_ru
OPENAI_BASE_URL=https://foundation-models.api.cloud.ru/v1
OPENAI_RESPONSE_MODEL=openai/gpt-oss-120b
VECTOR_STORE_PATH=/data/chroma
CHUNK_SIZE=800
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=4
ALLOWED_USERS=ваш_telegram_user_id
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Шаг 6: Запуск проекта

```bash
docker compose build
docker compose up -d
```

Или через Makefile:
```bash
make build && make up
```

### Шаг 7: Проверка

Откройте браузер: http://localhost:8080

Логи:
```bash
docker compose logs -f bot
```

---

## Получение необходимых токенов

### Telegram Bot Token

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Придумайте имя бота
4. Придумайте username бота (должен заканчиваться на `bot`)
5. Скопируйте полученный токен
6. Вставьте в `.env` как `TELEGRAM_TOKEN`

### Telegram User ID

1. Найдите @userinfobot в Telegram
2. Отправьте ему любое сообщение
3. Скопируйте ваш ID
4. Вставьте в `.env` как `ALLOWED_USERS`

Для нескольких пользователей укажите через запятую:
```env
ALLOWED_USERS=123456789,987654321
```

### Cloud.ru API Key

1. Зарегистрируйтесь на https://cloud.ru/
2. Откройте консоль управления: https://console.cloud.ru/
3. В верхнем правом углу нажмите на имя пользователя
4. Выберите "API ключи"
5. Нажмите "Создать ключ"
6. Выберите тип: "Статический ключ"
7. Скопируйте созданный ключ (он показывается только один раз!)
8. Вставьте в `.env` как `OPENAI_API_KEY`

Подробная инструкция: https://cloud.ru/docs/console_api/ug/topics/guides__static-api-keys__create

---

## Настройка через веб-интерфейс

После запуска проекта откройте http://localhost:8080

### Управление моделями эмбеддингов

1. Раздел "Управление моделями эмбеддингов"
2. Выберите модель из списка:
   - `bge-m3` (1.2 GB) - мультиязычная, **рекомендуется**
   - `embeddinggemma` (622 MB) - универсальная
   - `qwen3-embedding:0.6b` (639 MB) - длинные контексты
   - `qwen3-embedding:4b` (2.5 GB) - высокая точность
3. Нажмите "Загрузить модель"
4. Дождитесь завершения загрузки
5. Нажмите "Сохранить" - изменения применятся автоматически

### Настройки LLM (Cloud.ru)

1. Раздел "Настройки LLM API"
2. Заполните поля:
   - **API Base URL**: `https://foundation-models.api.cloud.ru/v1`
   - **API Key**: ваш ключ Cloud.ru
3. Нажмите кнопку "Загрузить модели" - система получит список доступных моделей
4. Выберите модель из выпадающего списка:
   - `openai/gpt-oss-120b` - рекомендуется
   - `meta-llama/Llama-3.3-70B-Instruct`
   - или другие
5. Нажмите "Сохранить" - изменения применятся автоматически (перезапуск НЕ нужен)

**Примечание:** Параметры обработки текста (Chunk Size, Chunk Overlap, Top-K) настраиваются только через файл `.env`

---

## Использование локальной LLM через LM Studio

### Установка LM Studio

**Windows/macOS/Linux:**
Скачайте с https://lmstudio.ai/ и установите

### Запуск локальной модели

1. Откройте LM Studio
2. Вкладка "Discover" → найдите модель `gpt-oss-20b` (рекомендуется как оптимальная и точная)
3. Скачайте модель с квантизацией Q4_K_M или Q5_K_M
4. Вкладка "Local Server" → выберите скачанную модель
5. **ВАЖНО:** Нажмите кнопку загрузки модели в память (Load Model)
6. Дождитесь загрузки модели в память
7. Нажмите "Start Server"
8. Сервер запустится на `localhost:1234`

### Настройка в проекте

1. Откройте веб-интерфейс: http://localhost:8080
2. Раздел "Настройки LLM API"
3. Измените **API Base URL**:
   - Windows/macOS: `http://host.docker.internal:1234/v1`
   - Ubuntu/Arch Linux: `http://172.17.0.1:1234/v1`
4. Нажмите кнопку "Загрузить модели"
5. Выберите модель из выпадающего списка (должна появиться модель из LM Studio)
6. Нажмите "Сохранить" - изменения применятся автоматически (перезапуск НЕ нужен)

**Для Ubuntu/Arch - узнать IP хоста:**
```bash
ip addr show docker0 | grep inet
```

**КРИТИЧЕСКИ ВАЖНО:** В LM Studio модель должна быть загружена в память (Load Model), иначе запросы будут возвращать ошибки!

---

## Первый запуск

1. Откройте Telegram и найдите вашего бота

2. Отправьте `/start`

3. Вы увидите приветственное сообщение с информацией о статусе

4. Отправьте тестовый документ (PDF или DOCX)

5. Дождитесь обработки (бот покажет примерное время)

6. Задайте вопрос по содержимому документа

7. Получите ответ на основе загруженных данных

---

## Команды управления

### Просмотр логов
**Docker Compose:**
```bash
docker compose logs -f bot
```
**Make:**
```bash
make logs
```

### Перезапуск
**Docker Compose:**
```bash
docker compose restart
```
**Make:**
```bash
make restart
```

### Остановка
**Docker Compose:**
```bash
docker compose stop
```
**Make:**
```bash
make stop
```

### Запуск (после остановки)
**Docker Compose:**
```bash
docker compose start
```
**Make:**
```bash
make start
```

### Полная остановка и удаление
**Docker Compose:**
```bash
docker compose down
```
**Make:**
```bash
make down
```

### Очистка векторной базы
**Docker Compose:**
```bash
rm -rf data/vector/*
docker compose restart bot
```
**Make:**
```bash
make clean-data
docker compose restart bot
```

### Просмотр статуса
**Docker Compose:**
```bash
docker compose ps
```
**Make:**
```bash
make ps
```

### Вход в контейнер (для отладки)
**Docker Compose:**
```bash
docker compose exec bot /bin/bash
```
**Make:**
```bash
make shell
```

---

## Решение проблем

### Контейнеры не запускаются

1. Проверьте, что Docker запущен
2. Проверьте логи: `docker compose logs`
3. Пересоберите: `docker compose down && docker compose build --no-cache && docker compose up -d`

### Бот не отвечает

1. Проверьте токен в `.env`
2. Проверьте `ALLOWED_USERS` в веб-интерфейсе
3. Проверьте логи бота: `docker compose logs -f bot`

### Модель эмбеддингов не загружается

1. Откройте веб-интерфейс: http://localhost:8080
2. Раздел "Управление моделями"
3. Проверьте статус загрузки
4. При ошибке попробуйте другую модель

### Веб-интерфейс не открывается

1. Проверьте, что контейнер запущен: `docker compose ps`
2. Проверьте, что порт 8080 свободен
3. Попробуйте: http://127.0.0.1:8080

### Windows: ошибки с WSL 2

1. Включите WSL 2 в Docker Desktop Settings
2. Убедитесь, что виртуализация включена в BIOS
3. Перезапустите Docker Desktop

### Ubuntu/Arch: Permission denied

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Затем перелогиньтесь или перезагрузите систему.

---

## Дополнительные настройки

### Изменение порта веб-интерфейса

В `docker-compose.yml` измените:
```yaml
ports:
  - "8080:8080"  # измените первое число
```

На, например:
```yaml
ports:
  - "3000:8080"
```

Затем перезапустите: `docker compose up -d`

### Использование GPU (для ускорения)

**NVIDIA GPU на Linux:**

1. Установите NVIDIA Container Toolkit
2. В `docker-compose.yml` добавьте для сервиса `ollama`:
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: all
             capabilities: [gpu]
   ```

---

## Обновление проекта

```bash
git pull
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## Полезные ссылки

- Docker: https://docs.docker.com/
- Ollama: https://ollama.ai/
- LM Studio: https://lmstudio.ai/
- Cloud.ru: https://cloud.ru/
- Telegram Bot API: https://core.telegram.org/bots/api
