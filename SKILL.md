---
name: qqmail-lark-calendar
description: Conversational one-shot skill that scans QQ Mail interview-notification emails and creates or updates Lark calendar events via lark-cli.
---

# qqmail-lark-calendar

## Purpose

When the user asks to arrange Lark calendar events from interview emails, run one bounded sync from QQ Mail to Lark Calendar.

## When to use

Use this skill when the user wants to:
- 根据面试邮件安排飞书日历
- 扫描最近的面试通知并同步到 Lark 日历
- 把 QQ 邮箱里的面试邀约写到飞书日历

## When not to use

Do not use this skill when the user wants:
- interactive configuration or setup guidance
- installation or onboarding instructions
- codebase explanation, architecture discussion, or implementation walkthroughs
- AI-level semantic understanding of mail content, including precise distinction between interview time and deadline time

## Required inputs and dependencies

The host environment must already provide:

- `python3`
- `lark-cli`
- valid QQ Mail IMAP credentials
- an authenticated Lark CLI session
- complete runtime configuration via `config.env` and/or process environment:
  - `QQMAIL_USER`
  - `QQMAIL_AUTH_CODE`
  - `LARK_CALENDAR_ID`

## Invocation shape

This is a one-shot execution skill.

Default behavior:
- scan recent candidate emails within the default lookback window
- skip subjects already recorded in `{baseDir}/.processed_emails.json`
- extract minimal interview information from each new candidate email
- create or patch the matching Lark calendar event
- append the QQ mail link into the final event description
- persist updated local state
- return a readable summary to the caller

Optional user intent may narrow the time window, for example “最近 24 小时”.

## Command wrapper

```bash
python3 "{baseDir}/calendar_sync.py" --hours 12
```

This command is the canonical local wrapper around the same one-shot execution path. GitHub/OpenClaw installation is handled by `install.sh`; this file only defines when the skill should run and what it should do.

## Expected result summary

A successful run should be able to report:
- scan window
- candidate email count
- new email count
- created event count
- updated event count
- failure count

If the skill cannot run, the failure should clearly identify the stage, such as:
- missing configuration
- Lark authentication unavailable
- QQ Mail IMAP access failed
- state load/save failed
- Lark calendar write failed

## Parsing and idempotency constraints

This skill currently uses minimal rule-based extraction, not AI semantic parsing.

- If a clear date and time range is found, the event uses that range.
- If no clear time range is found, the runtime falls back to the email timestamp and creates a 30-minute placeholder event.
- Processed-email dedupe is subject-based.
- Event upsert behavior depends on the local `dedupe_key -> event_id` mapping; it does not search Lark remotely for matching events.

## Side effects

A run may:
- read emails from QQ Mail IMAP
- create or update events in the configured Lark calendar
- write local state files under `{baseDir}`

## Hard boundaries

This skill must not:
- provide interactive initialization
- generate credentials automatically
- teach installation or login flows
- claim AI-level semantic understanding of email content

## Related runtime files

- `{baseDir}/calendar_sync.py`
- `{baseDir}/qqmail_lark_calendar/config.py`
- `{baseDir}/qqmail_lark_calendar/mail_imap.py`
- `{baseDir}/qqmail_lark_calendar/parse_interview.py`
- `{baseDir}/qqmail_lark_calendar/lark_cli.py`
- `{baseDir}/qqmail_lark_calendar/state_store.py`
