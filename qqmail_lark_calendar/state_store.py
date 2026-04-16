from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class StateStoreError(RuntimeError):
    pass


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise StateStoreError(f"读取状态文件失败: {path} ({e})") from e


def _write_json(path: Path, data: Any) -> None:
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise StateStoreError(f"写入状态文件失败: {path} ({e})") from e


@dataclass
class ProcessedStatePaths:
    processed_emails_path: Path
    processed_events_path: Path


def load_processed_email_subjects(path: Path) -> set[str]:
    raw = _read_json(path, default=[])
    if isinstance(raw, list):
        return {str(x) for x in raw}
    # 兼容未来可能的结构
    if isinstance(raw, dict) and "items" in raw and isinstance(raw["items"], list):
        return {str(x) for x in raw["items"]}
    raise StateStoreError(f"状态文件格式不正确（期望 list）: {path}")


def save_processed_email_subjects(path: Path, subjects: set[str]) -> None:
    _write_json(path, sorted(subjects))


def load_event_map(path: Path) -> dict[str, str]:
    raw = _read_json(path, default={})
    if isinstance(raw, dict):
        out: dict[str, str] = {}
        for k, v in raw.items():
            if isinstance(k, str) and isinstance(v, str):
                out[k] = v
        return out
    raise StateStoreError(f"事件状态文件格式不正确（期望 object）: {path}")


def save_event_map(path: Path, event_map: dict[str, str]) -> None:
    _write_json(path, event_map)

