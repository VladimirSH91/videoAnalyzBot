#!/usr/bin/env python3
import sys
import asyncio
from pathlib import Path

# Добавляем путь к src директории
sys.path.append(str(Path(__file__).parent.parent / "src"))

from db.database import async_database_session_maker
from models.videos import Video
from models.video_snapshots import VideoSnapshot
from sqlalchemy import select


async def check_records():
    """Проверка количества записей в БД"""
    async with async_database_session_maker() as session:
        # Считаем видео
        video_result = await session.execute(select(Video))
        videos = video_result.scalars().all()
        
        # Считаем снапшоты
        snapshot_result = await session.execute(select(VideoSnapshot))
        snapshots = snapshot_result.scalars().all()
        
        print(f"Видео в БД: {len(videos)}")
        print(f"Снапшотов в БД: {len(snapshots)}")
        
        if videos:
            print("\nПервые 5 видео:")
            for video in videos[:5]:
                print(f"  ID: {video.id}, Creator: {video.creator_id}, Views: {video.views_count}")


if __name__ == "__main__":
    asyncio.run(check_records())
