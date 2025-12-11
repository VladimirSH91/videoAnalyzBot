import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from db import Base


class VideoSnapshot(Base):
    __tablename__ = 'video_snapshots'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey('videos.id'), nullable=False, index=True)

    views_count = Column(Integer, nullable=False)
    likes_count = Column(Integer, nullable=False)
    comments_count = Column(Integer, nullable=False)
    reports_count = Column(Integer, nullable=False)

    delta_views_count = Column(Integer, nullable=False)
    delta_likes_count = Column(Integer, nullable=False)
    delta_comments_count = Column(Integer, nullable=False)
    delta_reports_count = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False)  # время замера (раз в час)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
