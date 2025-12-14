from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from nlq.schemas import TimeRange


@dataclass(frozen=True)
class UtcDateTimeRange:
    start: datetime
    end: datetime


def _day_start_utc(d: date) -> datetime:
    return datetime.combine(d, time.min)


def to_utc_datetime_range(tr: TimeRange, now_utc: datetime | None = None) -> UtcDateTimeRange:
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    if now_utc.tzinfo is not None:
        now_utc = now_utc.astimezone(timezone.utc).replace(tzinfo=None)

    today = now_utc.date()

    if tr.type.value == "today":
        start = _day_start_utc(today)
        end = start + timedelta(days=1)
        return UtcDateTimeRange(start=start, end=end)

    if tr.type.value == "yesterday":
        start = _day_start_utc(today - timedelta(days=1))
        end = start + timedelta(days=1)
        return UtcDateTimeRange(start=start, end=end)

    if tr.type.value == "last_n_days":
        if tr.n is None:
            raise ValueError("time_range.n is required for last_n_days")
        end = _day_start_utc(today) + timedelta(days=1)
        start = end - timedelta(days=tr.n)
        return UtcDateTimeRange(start=start, end=end)

    if tr.type.value == "between":
        if tr.from_ is None or tr.to is None:
            raise ValueError("time_range.from and time_range.to are required for between")
        start = _day_start_utc(tr.from_)
        end = _day_start_utc(tr.to) + timedelta(days=1)
        return UtcDateTimeRange(start=start, end=end)

    raise ValueError(f"Unsupported time_range.type: {tr.type}")
