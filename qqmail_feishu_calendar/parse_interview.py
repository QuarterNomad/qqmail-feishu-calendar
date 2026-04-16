from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class InterviewInfo:
    title: str
    description: str
    start: datetime
    end: datetime
    dedupe_key: str


_TIME_RANGE_PATTERNS: list[re.Pattern[str]] = [
    # 2026-04-16 14:00-15:00 / 2026/04/16 14:00-15:00
    re.compile(
        r"(?P<date>\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+"
        r"(?P<h1>\d{1,2}):(?P<m1>\d{2})\s*[-~—–]\s*(?P<h2>\d{1,2}):(?P<m2>\d{2})"
    ),
    # 4月16日 14:00-15:00（默认取当前年）
    re.compile(
        r"(?P<mon>\d{1,2})\s*月\s*(?P<day>\d{1,2})\s*日\s+"
        r"(?P<h1>\d{1,2}):(?P<m1>\d{2})\s*[-~—–]\s*(?P<h2>\d{1,2}):(?P<m2>\d{2})"
    ),
]


def _stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _parse_date_ymd(s: str) -> tuple[int, int, int]:
    parts = re.split(r"[-/]", s)
    y, m, d = (int(parts[0]), int(parts[1]), int(parts[2]))
    return y, m, d


def extract_interview_info(subject: str, body_text: str, fallback_base_time: datetime) -> InterviewInfo:
    """
    最低配解析：
    - 尝试从正文提取 “日期 + 起止时间”
    - 提取不到则用 fallback_base_time 开始，默认 30 分钟时长，并在标题/描述里标记“待确认”
    """
    text = f"{subject}\n{body_text}"

    for pat in _TIME_RANGE_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        if "date" in m.groupdict():
            y, mon, day = _parse_date_ymd(m.group("date"))
        else:
            y = fallback_base_time.year
            mon = int(m.group("mon"))
            day = int(m.group("day"))
        h1, m1 = int(m.group("h1")), int(m.group("m1"))
        h2, m2 = int(m.group("h2")), int(m.group("m2"))
        start = datetime(y, mon, day, h1, m1)
        end = datetime(y, mon, day, h2, m2)
        if end <= start:
            end = start + timedelta(minutes=30)
        title = subject.strip() or "面试安排"
        desc = body_text[:2000].strip()
        key_material = f"{title}|{start.isoformat()}|{end.isoformat()}"
        return InterviewInfo(
            title=title,
            description=desc,
            start=start,
            end=end,
            dedupe_key=_stable_hash(key_material),
        )

    # fallback
    start = fallback_base_time.replace(second=0, microsecond=0)
    end = start + timedelta(minutes=30)
    title = (subject.strip() or "面试安排") + "（待确认时间）"
    desc = ("未从邮件中提取到明确时间范围，已用邮件时间做占位。\n\n" + body_text[:2000]).strip()
    key_material = f"{subject}|{start.isoformat()}|fallback"
    return InterviewInfo(
        title=title,
        description=desc,
        start=start,
        end=end,
        dedupe_key=_stable_hash(key_material),
    )

