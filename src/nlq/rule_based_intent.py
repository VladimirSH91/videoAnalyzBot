from __future__ import annotations

import re
from datetime import date

from nlq.schemas import Filters, Measure, Metric, QueryIntent, TimeRange, TimeRangeType


_UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)

_DATE_ISO_RE = re.compile(r"\b(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})\b")
_DATE_DMY_RE = re.compile(r"\b(?P<d>\d{1,2})\.(?P<m>\d{1,2})\.(?P<y>\d{4})\b")
_LAST_N_DAYS_RE = re.compile(r"(?:last|за)\s+(?P<n>\d{1,4})\s*(?:days|дн(?:ей|я)?)", re.IGNORECASE)
_RUSSIAN_MONTH_DATE_RE = re.compile(r"\b(?P<d>\d{1,2})\s+(?P<month>января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(?P<y>\d{4})\b", re.IGNORECASE)
_MORE_THAN_VIEWS_RE = re.compile(r"\b(?:больше|более|свыше|>\s*)\s*(?P<n>\d{1,9})\s*(?:просмотров|просмотра|просмотр|views)\b", re.IGNORECASE)
_UNIQUE_VIDEOS_RE = re.compile(r"\b(?:разных|различных|уникальных)\s+(?:видео|видеоролик|видеороликов|ролик|роликов)\b", re.IGNORECASE)


def _parse_date(token: str) -> date | None:
    m = _DATE_ISO_RE.search(token)
    if m:
        return date(int(m.group("y")), int(m.group("m")), int(m.group("d")))

    m = _DATE_DMY_RE.search(token)
    if m:
        return date(int(m.group("y")), int(m.group("m")), int(m.group("d")))

    m = _RUSSIAN_MONTH_DATE_RE.search(token)
    if m:
        month_map = {
            "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
            "мая": 5, "июня": 6, "июля": 7, "августа": 8,
            "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
        }
        return date(int(m.group("y")), month_map[m.group("month").lower()], int(m.group("d")))

    return None


def parse_intent_rule_based(user_text: str) -> QueryIntent:
    text = user_text.strip()
    low = text.lower()

    metric: Metric | None = None
    video_keywords = [
        "видео",
        "видеоролик",
        "видеороликов",
        "ролик",
        "ролика",
        "роликов",
        "видос",
        "видосик",
        "видеозапись",
        "видеозаписей",
    ]

    if any(k in low for k in ["просмотр", "просмотры", "просмотров", "views"]):
        metric = Metric.views
    elif any(k in low for k in ["лайк", "лайки", "лайков", "likes"]):
        metric = Metric.likes
    elif any(k in low for k in ["коммент", "комменты", "комментар", "comments"]):
        metric = Metric.comments
    elif any(k in low for k in ["репорт", "репорты", "жалоб", "жалобы", "reports"]):
        metric = Metric.reports
    elif any(k in low for k in video_keywords):
        metric = Metric.videos

    if metric is None:
        raise ValueError("Unsupported metric")

    measure = Measure.final
    if any(k in low for k in ["прирост", "увелич", "рост", "delta", "на сколько"]):
        measure = Measure.delta_sum

    creator_id = None
    m_uuid = _UUID_RE.search(text)
    if m_uuid:
        creator_id = m_uuid.group(0)

    min_views = None
    m_views = _MORE_THAN_VIEWS_RE.search(text)
    if m_views:
        min_views = int(m_views.group("n"))

    unique_videos = bool(_UNIQUE_VIDEOS_RE.search(text))

    filters = Filters(
        creator_id=creator_id,
        min_views=min_views,
        unique_videos=unique_videos,
    )

    # time_range
    if any(k in low for k in ["за всё время", "за все время", "в системе", "all time", "all-time"]):
        time_range = TimeRange(type=TimeRangeType.last_n_days, n=36500)
    elif "сегодня" in low or "today" in low:
        time_range = TimeRange(type=TimeRangeType.today)
    elif "вчера" in low or "yesterday" in low:
        time_range = TimeRange(type=TimeRangeType.yesterday)
    else:
        m_last = _LAST_N_DAYS_RE.search(low)
        if m_last:
            time_range = TimeRange(type=TimeRangeType.last_n_days, n=int(m_last.group("n")))
        else:
            dates: list[date] = []
            for m in _DATE_ISO_RE.finditer(text):
                dates.append(date(int(m.group("y")), int(m.group("m")), int(m.group("d"))))
            for m in _DATE_DMY_RE.finditer(text):
                dates.append(date(int(m.group("y")), int(m.group("m")), int(m.group("d"))))
            for m in _RUSSIAN_MONTH_DATE_RE.finditer(text):
                month_map = {
                    "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
                    "мая": 5, "июня": 6, "июля": 7, "августа": 8,
                    "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
                }
                dates.append(date(int(m.group("y")), month_map[m.group("month").lower()], int(m.group("d"))))

            if len(dates) >= 2:
                start, end = dates[0], dates[1]
                time_range = TimeRange(type=TimeRangeType.between, **{"from": start}, to=end)
            elif len(dates) == 1:
                d = dates[0]
                time_range = TimeRange(type=TimeRangeType.between, **{"from": d}, to=d)
            else:
                time_range = TimeRange(type=TimeRangeType.today)

    if metric == Metric.videos and measure == Measure.delta_sum:
        raise ValueError("delta_sum is not supported for metric=videos")

    return QueryIntent(
        metric=metric,
        measure=measure,
        time_range=time_range,
        filters=filters,
        confidence=1.0,
    )
