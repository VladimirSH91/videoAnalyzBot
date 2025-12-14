from __future__ import annotations

from sqlalchemy import func, select

from models.video_snapshots import VideoSnapshot
from models.videos import Video
from nlq.schemas import Metric, QueryIntent
from nlq.time_range import to_utc_datetime_range


_METRIC_TO_VIDEO_COL = {
    Metric.views: Video.views_count,
    Metric.likes: Video.likes_count,
    Metric.comments: Video.comments_count,
    Metric.reports: Video.reports_count,
}

_METRIC_TO_SNAPSHOT_DELTA_COL = {
    Metric.views: VideoSnapshot.delta_views_count,
    Metric.likes: VideoSnapshot.delta_likes_count,
    Metric.comments: VideoSnapshot.delta_comments_count,
    Metric.reports: VideoSnapshot.delta_reports_count,
}


def build_scalar_query(intent: QueryIntent):
    if intent.measure.value == "final":
        if intent.metric == Metric.videos:
            q = select(func.count(Video.id) if not intent.filters.unique_videos else func.count(func.distinct(Video.id)))
        else:
            metric_col = _METRIC_TO_VIDEO_COL[intent.metric]
            q = select(func.coalesce(func.sum(metric_col), 0))

        tr = to_utc_datetime_range(intent.time_range)
        start = tr.start.replace(tzinfo=None)
        end = tr.end.replace(tzinfo=None)
        q = q.select_from(Video).where(
            Video.video_created_at >= start,
            Video.video_created_at < end,
        )

        if intent.filters.creator_id:
            q = q.where(Video.creator_id == intent.filters.creator_id)

        if intent.filters.min_views is not None:
            q = q.where(Video.views_count >= intent.filters.min_views)

        return q

    if intent.measure.value == "delta_sum":
        if intent.metric == Metric.videos:
            raise ValueError("delta_sum is not supported for metric=videos")
        delta_col = _METRIC_TO_SNAPSHOT_DELTA_COL[intent.metric]

        tr = to_utc_datetime_range(intent.time_range)

        if intent.filters.unique_videos:
            q = (
                select(func.count(func.distinct(VideoSnapshot.video_id)))
                .select_from(VideoSnapshot)
                .join(Video, Video.id == VideoSnapshot.video_id)
                .where(
                    VideoSnapshot.created_at >= tr.start,
                    VideoSnapshot.created_at < tr.end,
                )
            )
        else:
            q = (
                select(func.coalesce(func.sum(delta_col), 0))
                .select_from(VideoSnapshot)
                .where(
                    VideoSnapshot.created_at >= tr.start,
                    VideoSnapshot.created_at < tr.end,
                )
            )

        if intent.filters.creator_id:
            q = q.where(Video.creator_id == intent.filters.creator_id)

        return q

    raise ValueError(f"Unsupported measure: {intent.measure}")
