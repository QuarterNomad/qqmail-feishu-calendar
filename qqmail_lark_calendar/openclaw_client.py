from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta

from qqmail_lark_calendar.mail_imap import CandidateEmail
from qqmail_lark_calendar.parse_interview import InterviewInfo


class OpenClawError(RuntimeError):
    pass


def _build_prompt(email: CandidateEmail, fallback_time: datetime, qq_link: str) -> str:
    fallback_start = fallback_time.replace(second=0, microsecond=0)
    fallback_end = fallback_start + timedelta(minutes=30)
    return f"""你是一个邮件信息抽取器。请从下面的面试相关邮件中提取结构化信息，并且只输出 JSON，不要输出解释。

要求：
1. 只返回一个 JSON 对象。
2. JSON 字段固定为：title, description, start, end, dedupe_key。
3. start 和 end 必须是 ISO 8601 datetime 字符串，例如 2026-04-16T14:00:00。
4. 如果邮件里没有明确时间范围，请使用 fallback 时间：start={fallback_start.isoformat()}，end={fallback_end.isoformat()}，并在 title 中标记 待确认时间。
5. description 不要包含 QQ 邮件链接；链接会由下游追加。
6. dedupe_key 需要稳定，基于你识别出的标题和时间生成一个简短稳定字符串。

邮件主题：{email.subject}
发件人：{email.from_}
邮件时间：{email.date_display}
QQ邮件链接：{qq_link}

邮件正文：
{email.body_text[:4000]}
"""


def _parse_json_object(text: str) -> dict[str, object]:
    text = text.strip()
    for i, ch in enumerate(text):
        if ch == "{":
            try:
                return json.loads(text[i:])
            except json.JSONDecodeError:
                continue
    raise OpenClawError("OpenClaw 返回内容不是可解析的 JSON 对象")


def extract_interview_info_with_openclaw(
    *,
    command: str,
    email: CandidateEmail,
    fallback_time: datetime,
    qq_link: str,
) -> InterviewInfo:
    prompt = _build_prompt(email, fallback_time, qq_link)
    try:
        result = subprocess.run(
            [command, "run", prompt],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError as e:
        raise OpenClawError(f"未找到 OpenClaw 命令: {command}") from e
    except subprocess.TimeoutExpired as e:
        raise OpenClawError("OpenClaw 执行超时") from e

    output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
    if result.returncode != 0:
        raise OpenClawError(output or "OpenClaw 执行失败")

    obj = _parse_json_object(output)
    try:
        title = str(obj["title"]).strip()
        description = str(obj.get("description", "")).strip()
        start = datetime.fromisoformat(str(obj["start"]).strip())
        end = datetime.fromisoformat(str(obj["end"]).strip())
        dedupe_key = str(obj["dedupe_key"]).strip()
    except Exception as e:
        raise OpenClawError(f"OpenClaw 返回字段不完整或格式非法: {output[:500]}") from e

    if not title:
        raise OpenClawError("OpenClaw 返回的 title 为空")
    if not dedupe_key:
        raise OpenClawError("OpenClaw 返回的 dedupe_key 为空")
    if end <= start:
        raise OpenClawError("OpenClaw 返回的 end 早于或等于 start")

    return InterviewInfo(
        title=title,
        description=description,
        start=start,
        end=end,
        dedupe_key=dedupe_key,
    )
