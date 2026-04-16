from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any


class LarkCliError(RuntimeError):
    pass


@dataclass(frozen=True)
class LarkEvent:
    event_id: str


def _run(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError as e:
        raise LarkCliError("未找到 lark-cli，请查看: https://github.com/larksuite/cli") from e
    except subprocess.TimeoutExpired as e:
        raise LarkCliError(f"lark-cli 执行超时: {' '.join(cmd)}") from e

    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        raise LarkCliError(out.strip() or f"lark-cli 执行失败: {' '.join(cmd)}")
    return out


def assert_logged_in() -> None:
    out = _run(["lark-cli", "auth", "status"])
    if "not logged in" in out.lower() or "未登录" in out:
        raise LarkCliError("Lark 未登录，请查看: https://github.com/larksuite/cli")


def get_default_calendar_id() -> str:
    out = _run(["lark-cli", "calendar", "list", "--format", "json"])
    obj = _parse_json_maybe(out)
    if obj is None:
        raise LarkCliError(f"无法解析日历列表，原始输出:\n{out[:800]}")

    calendars = _extract_calendars(obj)
    if not calendars:
        raise LarkCliError("未找到可用日历，请先在 Lark 中确认当前账号已有可写日历")

    preferred = _pick_primary_calendar(calendars)
    if not preferred:
        raise LarkCliError("已读取日历列表，但无法识别默认日历 ID")
    return preferred


def _parse_json_maybe(text: str) -> Any | None:
    text = text.strip()
    if not text:
        return None
    # 有些 CLI 会输出多行，尽量找到 JSON 起始
    for i in range(len(text)):
        if text[i] in "{[":
            try:
                return json.loads(text[i:])
            except Exception:
                break
    try:
        return json.loads(text)
    except Exception:
        return None


def _find_event_id(obj: Any) -> str | None:
    if isinstance(obj, dict):
        for k in ("event_id", "eventId", "id"):
            v = obj.get(k)
            if isinstance(v, str) and v:
                return v
        for v in obj.values():
            got = _find_event_id(v)
            if got:
                return got
    if isinstance(obj, list):
        for v in obj:
            got = _find_event_id(v)
            if got:
                return got
    return None


def _extract_calendars(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        return [item for item in obj if isinstance(item, dict)]
    if isinstance(obj, dict):
        for key in ("items", "calendars", "data"):
            value = obj.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            if isinstance(value, dict):
                nested = _extract_calendars(value)
                if nested:
                    return nested
    return []


def _pick_primary_calendar(calendars: list[dict[str, Any]]) -> str | None:
    def calendar_id(item: dict[str, Any]) -> str | None:
        for key in ("calendar_id", "calendarId", "id"):
            value = item.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    preferred_flag_keys = (
        "is_primary",
        "isPrimary",
        "primary",
        "default",
        "is_default",
        "isDefault",
    )

    for item in calendars:
        if any(item.get(key) is True for key in preferred_flag_keys):
            found = calendar_id(item)
            if found:
                return found

    for item in calendars:
        summary = " ".join(
            str(item.get(key, "")) for key in ("summary", "name", "title")
        ).lower()
        if any(token in summary for token in ("primary", "default", "主日历", "默认")):
            found = calendar_id(item)
            if found:
                return found

    for item in calendars:
        found = calendar_id(item)
        if found:
            return found
    return None


def create_event(
    *,
    calendar_id: str,
    summary: str,
    start: datetime,
    end: datetime,
    description: str,
) -> LarkEvent:
    # 用快捷命令创建；优先让 CLI 输出 json（若 CLI 不支持，也能从输出里解析）
    cmd = [
        "lark-cli",
        "calendar",
        "+create",
        "--summary",
        summary,
        "--start",
        start.isoformat(timespec="minutes"),
        "--end",
        end.isoformat(timespec="minutes"),
        "--description",
        description,
        "--calendar-id",
        calendar_id,
        "--format",
        "json",
    ]
    out = _run(cmd)
    obj = _parse_json_maybe(out)
    event_id = _find_event_id(obj) if obj is not None else None
    if not event_id:
        # 兜底：输出可能是 pretty 格式或包含提示语
        raise LarkCliError(f"创建日历事件成功但无法解析 event_id，原始输出:\n{out[:800]}")
    return LarkEvent(event_id=event_id)


def patch_event(
    *,
    calendar_id: str,
    event_id: str,
    summary: str,
    start: datetime,
    end: datetime,
    description: str,
) -> None:
    # 使用底层 API patch（更稳定可控）。此处仅更新核心字段。
    payload = {
        "summary": summary,
        "description": description,
        "start_time": {"timestamp": str(int(start.timestamp())), "timezone": "Asia/Shanghai"},
        "end_time": {"timestamp": str(int(end.timestamp())), "timezone": "Asia/Shanghai"},
        "need_notification": False,
    }
    _run(
        [
            "lark-cli",
            "api",
            "PATCH",
            f"/open-apis/calendar/v4/calendars/{calendar_id}/events/{event_id}",
            "--data",
            json.dumps(payload, ensure_ascii=False),
            "--format",
            "json",
        ]
    )

