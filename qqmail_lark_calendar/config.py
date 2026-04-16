from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class AppConfig:
    qqmail_user: str
    qqmail_auth_code: str
    lark_calendar_id: str
    openclaw_command: str


def load_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def resolve_config(env_file: Mapping[str, str], process_env: Mapping[str, str]) -> AppConfig:
    # 约定：env_file 优先，其次才是进程环境变量（方便 cron 用文件）
    def pick(key: str) -> str:
        return (env_file.get(key) or process_env.get(key) or "").strip()

    return AppConfig(
        qqmail_user=pick("QQMAIL_USER"),
        qqmail_auth_code=pick("QQMAIL_AUTH_CODE"),
        lark_calendar_id=pick("LARK_CALENDAR_ID"),
        openclaw_command=pick("OPENCLAW_COMMAND") or "openclaw",
    )


def validate_config(cfg: AppConfig) -> list[str]:
    missing: list[str] = []
    if not cfg.qqmail_user:
        missing.append("QQMAIL_USER")
    if not cfg.qqmail_auth_code:
        missing.append("QQMAIL_AUTH_CODE")
    if not cfg.lark_calendar_id:
        missing.append("LARK_CALENDAR_ID")
    return missing

