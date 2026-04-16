#!/usr/bin/env python3
"""
QQ Mail → Lark Calendar 同步脚本（AI 判断版）
代码粗筛 → AI 精判

首次运行或配置不完整时，自动进入引导流程。
"""

import sys
import argparse
import os
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

def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="QQ Mail → Lark Calendar sync")
    p.add_argument("--hours", type=int, default=12, help="扫描窗口（小时）")
    p.add_argument(
        "--non-interactive",
        action="store_true",
        help="非交互模式：配置缺失/未登录直接失败退出，不进入 setup_wizard",
    )
    return p.parse_args(argv)


def _ensure_config(non_interactive: bool) -> None:
    env_file = load_env_file(CONFIG_FILE)
    cfg = resolve_config(env_file, os.environ)
    missing = validate_config(cfg)
    if not missing:
        return

    if non_interactive:
        print(f"❌ 配置缺失: {', '.join(missing)}")
        print("请按 README.md 完成初始化（或运行 python3 setup_wizard.py），再用 --non-interactive 运行。")
        sys.exit(2)

    print("\n⚠️  检测到配置不完整，进入引导流程...\n")
    import setup_wizard

    setup_wizard.run_wizard()


def _parse_email_time_fallback(e: CandidateEmail) -> datetime:
    # date_display: "YYYY-MM-DD HH:MM"
    try:
        if e.date_display:
            return datetime.strptime(e.date_display, "%Y-%m-%d %H:%M")
    except Exception:
        pass
    return datetime.now()


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    _ensure_config(non_interactive=bool(args.non_interactive))

    env_file = load_env_file(CONFIG_FILE)
    cfg = resolve_config(env_file, os.environ)
    missing = validate_config(cfg)
    if missing:
        # interactive 模式下也可能没完成
        print(f"❌ 配置缺失: {', '.join(missing)}")
        return 2

    # 非交互/写日历模式下，必须确保已登录
    try:
        assert_logged_in()
    except LarkCliError as e:
        print(f"❌ Lark 鉴权失败: {e}")
        return 3

    started_at = datetime.now()
    print(f"[{started_at.strftime('%Y-%m-%d %H:%M:%S')}] 扫描 QQ 邮箱（hours={args.hours}）...")

    try:
        candidates = search_candidate_emails(cfg.qqmail_user, cfg.qqmail_auth_code, hours=int(args.hours))
    except Exception as e:
        print(f"❌ IMAP 失败: {e}")
        return 4

    print(f"  找到 {len(candidates)} 封候选邮件")
    if not candidates:
        print("  无候选邮件")
        return 0

    paths = ProcessedStatePaths(processed_emails_path=STATE_FILE, processed_events_path=EVENT_STATE_FILE)
    try:
        processed_subjects = load_processed_email_subjects(paths.processed_emails_path)
    except Exception as e:
        print(f"❌ 读取邮件状态失败: {e}")
        return 1

    try:
        event_map = load_event_map(paths.processed_events_path)
    except Exception as e:
        print(f"❌ 读取事件状态失败: {e}")
        return 1

    new_emails = [e for e in candidates if e.subject not in processed_subjects]
    if not new_emails:
        print(f"  全部已处理（{len(candidates)} 封）")
        return 0

    created = 0
    updated = 0
    failed = 0

    print(f"\n  === 新邮件 {len(new_emails)} 封 ===")
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
                updated += 1
            else:
                ev = create_event(
                    calendar_id=cfg.lark_calendar_id,
                    summary=info.title,
                    start=info.start,
                    end=info.end,
                    description=description,
                )
                event_map[info.dedupe_key] = ev.event_id
                created += 1
        except LarkCliError as ex:
            failed += 1
            print(f"\n  ❌ 写入 Lark 日历失败: {ex}")
            continue

        print(f"\n  [{e.date_display}] {e.subject}")
        print(f"  From: {e.from_[:60]}")
        print(f"  QQ邮件链接: {qq_link}")
        print(f"  事件: {info.title}")
        print(f"  时间: {info.start.strftime('%Y-%m-%d %H:%M')} - {info.end.strftime('%Y-%m-%d %H:%M')}")

        processed_subjects.add(e.subject)

    try:
        save_processed_email_subjects(paths.processed_emails_path, processed_subjects)
        save_event_map(paths.processed_events_path, event_map)
    except Exception as e:
        print(f"❌ 写入状态失败: {e}")
        return 1

    print("\n  === 汇总 ===")
    print(f"  创建事件: {created}")
    print(f"  更新事件: {updated}")
    print(f"  失败: {failed}")

    if failed:
        return 5
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
