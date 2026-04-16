#!/usr/bin/env python3
"""
QQ Mail → Lark Calendar 同步脚本。
作为可被智能体调用的一次性 skill 执行入口。
"""

import sys
import argparse
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from qqmail_lark_calendar.config import (
    load_env_file,
    resolve_config,
    validate_config,
)
from qqmail_lark_calendar.lark_cli import LarkCliError, assert_logged_in, create_event, patch_event
from qqmail_lark_calendar.mail_imap import CandidateEmail, search_candidate_emails
from qqmail_lark_calendar.parse_interview import extract_interview_info
from qqmail_lark_calendar.state_store import (
    ProcessedStatePaths,
    load_event_map,
    load_processed_email_subjects,
    save_event_map,
    save_processed_email_subjects,
)

# ============ 凭证路径 ============
SKILL_DIR = Path(__file__).parent
CONFIG_FILE = SKILL_DIR / 'config.env'
STATE_FILE = SKILL_DIR / '.processed_emails.json'
EVENT_STATE_FILE = SKILL_DIR / '.processed_events.json'


@dataclass(frozen=True)
class SyncRequest:
    hours: int = 12


@dataclass(frozen=True)
class SyncItemResult:
    subject: str
    qq_link: str
    title: str
    start: datetime
    end: datetime
    action: str


@dataclass
class SyncResult:
    hours: int
    started_at: datetime
    candidate_count: int = 0
    new_email_count: int = 0
    created_count: int = 0
    updated_count: int = 0
    failed_count: int = 0
    items: list[SyncItemResult] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="QQ Mail → Lark Calendar sync")
    p.add_argument("--hours", type=int, default=12, help="扫描窗口（小时）")
    return p.parse_args(argv)


def _load_config_or_exit():
    env_file = load_env_file(CONFIG_FILE)
    cfg = resolve_config(env_file, os.environ)
    missing = validate_config(cfg)
    if missing:
        print(f"❌ 配置缺失: {', '.join(missing)}")
        print("请由外部宿主系统提供完整配置后再运行该 skill。")
        sys.exit(2)
    return cfg


def _parse_email_time_fallback(e: CandidateEmail) -> datetime:
    try:
        if e.date_display:
            return datetime.strptime(e.date_display, "%Y-%m-%d %H:%M")
    except Exception:
        pass
    return datetime.now()


def run_sync(request: SyncRequest) -> SyncResult:
    cfg = _load_config_or_exit()
    result = SyncResult(hours=request.hours, started_at=datetime.now())

    assert_logged_in()
    candidates = search_candidate_emails(cfg.qqmail_user, cfg.qqmail_auth_code, hours=int(request.hours))
    result.candidate_count = len(candidates)
    if not candidates:
        return result

    paths = ProcessedStatePaths(processed_emails_path=STATE_FILE, processed_events_path=EVENT_STATE_FILE)
    processed_subjects = load_processed_email_subjects(paths.processed_emails_path)
    event_map = load_event_map(paths.processed_events_path)

    new_emails = [e for e in candidates if e.subject not in processed_subjects]
    result.new_email_count = len(new_emails)
    if not new_emails:
        return result

    for e in new_emails:
        fallback_time = _parse_email_time_fallback(e)
        info = extract_interview_info(e.subject, e.body_text, fallback_time)
        qq_link = f"https://mail.qq.com/cgi-bin/readmail?mailid={e.msg_id}"
        description = (info.description + "\n\n" + f"QQ邮件链接: {qq_link}").strip()

        try:
            existing_event_id = event_map.get(info.dedupe_key)
            if existing_event_id:
                patch_event(
                    calendar_id=cfg.lark_calendar_id,
                    event_id=existing_event_id,
                    summary=info.title,
                    start=info.start,
                    end=info.end,
                    description=description,
                )
                result.updated_count += 1
                action = "updated"
            else:
                ev = create_event(
                    calendar_id=cfg.lark_calendar_id,
                    summary=info.title,
                    start=info.start,
                    end=info.end,
                    description=description,
                )
                event_map[info.dedupe_key] = ev.event_id
                result.created_count += 1
                action = "created"
        except LarkCliError as ex:
            result.failed_count += 1
            result.failures.append(f"{e.subject}: {ex}")
            continue

        result.items.append(
            SyncItemResult(
                subject=e.subject,
                qq_link=qq_link,
                title=info.title,
                start=info.start,
                end=info.end,
                action=action,
            )
        )
        processed_subjects.add(e.subject)

    save_processed_email_subjects(paths.processed_emails_path, processed_subjects)
    save_event_map(paths.processed_events_path, event_map)
    return result


def _print_result(result: SyncResult) -> None:
    print(f"[{result.started_at.strftime('%Y-%m-%d %H:%M:%S')}] 扫描 QQ 邮箱（hours={result.hours}）...")
    print(f"  找到 {result.candidate_count} 封候选邮件")

    if result.candidate_count == 0:
        print("  无候选邮件")
        return
    if result.new_email_count == 0:
        print(f"  全部已处理（{result.candidate_count} 封）")
        return

    print(f"\n  === 新邮件 {result.new_email_count} 封 ===")
    for item in result.items:
        print(f"\n  {item.subject}")
        print(f"  QQ邮件链接: {item.qq_link}")
        print(f"  事件: {item.title}")
        print(f"  时间: {item.start.strftime('%Y-%m-%d %H:%M')} - {item.end.strftime('%Y-%m-%d %H:%M')}")
        print(f"  动作: {item.action}")

    for failure in result.failures:
        print(f"\n  ❌ 写入 Lark 日历失败: {failure}")

    print("\n  === 汇总 ===")
    print(f"  创建事件: {result.created_count}")
    print(f"  更新事件: {result.updated_count}")
    print(f"  失败: {result.failed_count}")


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        result = run_sync(SyncRequest(hours=args.hours))
    except LarkCliError as e:
        print(f"❌ Lark 鉴权失败: {e}")
        return 3
    except Exception as e:
        message = str(e)
        if message.startswith("读取邮件状态失败") or message.startswith("读取事件状态失败") or message.startswith("写入状态文件失败"):
            print(f"❌ 状态失败: {e}")
            return 1
        if "imap" in message.lower() or "auth" in message.lower():
            print(f"❌ IMAP 失败: {e}")
            return 4
        print(f"❌ 运行失败: {e}")
        return 1

    _print_result(result)
    if result.failed_count:
        return 5
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
