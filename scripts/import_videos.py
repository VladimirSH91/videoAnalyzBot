#!/usr/bin/env python3
import asyncio
import json
import sys
import os
from pathlib import Path

# Добавляем путь к src директории
sys.path.append(str(Path(__file__).parent.parent / "src"))

from sqlalchemy.ext.asyncio import AsyncSession
from db.database import async_database_session_maker, Base
from models.videos import Video
from models.video_snapshots import VideoSnapshot
from sqlalchemy import select
from datetime import datetime
import uuid


async def create_tables():
    """Создание таблиц в БД"""
    from db.database import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы созданы успешно")


async def import_videos_from_json(json_file_path: str):
    """Импорт видео из JSON файла в БД"""
    print(f"Загрузка данных из {json_file_path}...")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Данные находятся в поле "videos"
        if 'videos' in data:
            videos_data = data['videos']
        else:
            videos_data = data
            
    except Exception as e:
        print(f"Ошибка чтения JSON файла: {e}")
        return
    
    async with async_database_session_maker() as session:
        imported_count = 0
        
        for video_data in videos_data:
            try:
                # Проверяем, существует ли уже видео
                existing = await session.execute(
                    select(Video).where(Video.id == video_data['id'])
                )
                if existing.scalar_one_or_none():
                    print(f"Видео {video_data['id']} уже существует, пропускаем")
                    continue
                
                # Создаем запись видео
                video_created_dt = datetime.fromisoformat(video_data['video_created_at'])
                if video_created_dt.tzinfo is not None:
                    video_created_dt = video_created_dt.replace(tzinfo=None)
                
                video = Video(
                    id=video_data['id'],
                    creator_id=video_data['creator_id'],
                    video_created_at=video_created_dt,
                    views_count=video_data.get('views_count', 0),
                    likes_count=video_data.get('likes_count', 0),
                    comments_count=video_data.get('comments_count', 0),
                    reports_count=video_data.get('reports_count', 0)
                )
                
                session.add(video)
                await session.flush()  # Сохраняем видео чтобы получить ID для foreign key
                
                # Добавляем снапшоты если они есть
                if 'snapshots' in video_data:
                    for snapshot_data in video_data['snapshots']:
                        snapshot = VideoSnapshot(
                            id=uuid.uuid4(),
                            video_id=video_data['id'],
                            views_count=snapshot_data.get('views_count', 0),
                            likes_count=snapshot_data.get('likes_count', 0),
                            comments_count=snapshot_data.get('comments_count', 0),
                            reports_count=snapshot_data.get('reports_count', 0),
                            delta_views_count=snapshot_data.get('delta_views_count', 0),
                            delta_likes_count=snapshot_data.get('delta_likes_count', 0),
                            delta_comments_count=snapshot_data.get('delta_comments_count', 0),
                            delta_reports_count=snapshot_data.get('delta_reports_count', 0),
                            created_at=datetime.fromisoformat(snapshot_data['created_at'])
                        )
                        session.add(snapshot)
                
                imported_count += 1
                if imported_count % 100 == 0:
                    print(f"Импортировано: {imported_count} видео")
                    
            except Exception as e:
                print(f"Ошибка импорта видео {video_data.get('id', 'unknown')}: {e}")
                continue
        
        await session.commit()
        print(f"Импорт завершен. Всего импортировано: {imported_count} видео")


async def main():
    """Главная функция"""
    if len(sys.argv) != 2:
        print("Использование: python import_videos.py <путь_к_videos.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"Файл {json_file} не найден")
        sys.exit(1)
    
    try:
        await create_tables()
        await import_videos_from_json(json_file)
        print("Импорт данных завершен успешно!")
    except Exception as e:
        print(f"Ошибка при импорте: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
