import uuid
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from db import Base


class Video(Base):
    __tablename__ = 'videos'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    video_created_at = Column(DateTime, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    likes_count = Column(Integer, default=0, nullable=False)
    comments_count = Column(Integer, default=0, nullable=False)
    reports_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    