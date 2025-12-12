#!/bin/bash

# Скрипт для запуска импорта videos.json в БД Docker

echo "Проверка состояния Docker контейнера..."
docker-compose ps

echo "Запуск импорта данных..."
cd /home/vladimir/videoAnalyzBot

# Устанавливаем зависимости если нужно
pip install -r requirements.txt

# Запускаем импорт
python3 scripts/import_videos.py videos.json

echo "Импорт завершен!"
