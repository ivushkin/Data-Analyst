.PHONY: help build rebuild up logs down restart stop start shell ps clean-data clean-all

.DEFAULT_GOAL := help

help:
	@echo "Доступные команды:"
	@echo ""
	@echo "  make build        - Сборка Docker образов"
	@echo "  make rebuild      - Полная пересборка Docker образов с нуля (без кеша)"
	@echo "  make up           - Запуск контейнеров в фоновом режиме"
	@echo "  make start        - Запуск остановленных контейнеров"
	@echo "  make stop         - Остановка контейнеров без удаления"
	@echo "  make restart      - Перезапуск контейнеров"
	@echo "  make logs         - Просмотр логов контейнеров в режиме реального времени"
	@echo "  make down         - Остановка и удаление контейнеров"
	@echo "  make ps           - Список запущенных контейнеров"
	@echo "  make shell        - Вход в shell контейнера bot"
	@echo "  make clean-data   - Очистка векторной базы данных"
	@echo "  make clean-all    - Полная очистка (контейнеры, образы, volumes, данные)"
	@echo ""

build:
	docker compose build

rebuild:
	docker compose build --no-cache --pull

up:
	docker compose up -d

start:
	docker compose start

stop:
	docker compose stop

restart:
	docker compose restart

logs:
	docker compose logs -f

down:
	docker compose down

ps:
	docker compose ps

shell:
	docker compose exec bot /bin/bash

clean-data:
	rm -rf data/vector/*

clean-all:
	docker compose down -v --rmi all --remove-orphans
	rm -rf data/vector/*

