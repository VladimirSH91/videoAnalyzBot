from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class Metric(str, Enum):
    views = "views"
    likes = "likes"
    comments = "comments"
    reports = "reports"
    videos = "videos"


class Measure(str, Enum):
    final = "final"
    delta_sum = "delta_sum"


class TimeRangeType(str, Enum):
    last_n_days = "last_n_days"
    today = "today"
    yesterday = "yesterday"
    between = "between"


class TimeRange(BaseModel):
    type: TimeRangeType
    n: Optional[int] = Field(default=None, ge=1)
    from_: Optional[date] = Field(default=None, alias="from")
    to: Optional[date] = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_between(cls, data):
        if isinstance(data, dict) and data.get("type") in (TimeRangeType.between, "between"):
            from_v = data.get("from")
            to_v = data.get("to")
            if from_v is None and to_v is not None:
                data = dict(data)
                data["from"] = to_v
            elif to_v is None and from_v is not None:
                data = dict(data)
                data["to"] = from_v
        return data

    @model_validator(mode="after")
    def _validate_required_fields(self) -> "TimeRange":
        if self.type == TimeRangeType.last_n_days:
            if self.n is None:
                raise ValueError("time_range.n is required for last_n_days")

        if self.type == TimeRangeType.between:
            if self.from_ is None or self.to is None:
                raise ValueError("time_range.from and time_range.to are required for between")
            if self.to < self.from_:
                raise ValueError("time_range.to must be >= time_range.from")

        return self


class Filters(BaseModel):
    creator_id: Optional[str] = None
    min_views: Optional[int] = Field(default=None, ge=0)
    unique_videos: Optional[bool] = Field(default=False)


class QueryIntent(BaseModel):
    metric: Metric
    measure: Measure
    time_range: TimeRange
    filters: Filters | None = Field(default_factory=Filters)
    confidence: Optional[float] = Field(default=None, ge=0, le=1)

    @model_validator(mode="before")
    @classmethod
    def _normalize_filters(cls, data):
        if isinstance(data, dict) and data.get("filters") is None:
            data = dict(data)
            data["filters"] = {}
        return data

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
