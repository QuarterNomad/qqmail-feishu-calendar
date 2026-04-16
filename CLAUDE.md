# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This repository is intentionally scoped to a single OpenClaw/agent-facing skill: scan QQ Mail interview-notification emails, extract minimal interview details, and create or update Lark calendar events through `lark-cli` when the user expresses an intent like “根据面试邮件安排飞书日历”.

The repo does **not** include onboarding flows, interactive setup, or installation guidance. Future changes should preserve that boundary unless the user explicitly asks to change the repository scope.

## Common commands

### Run the skill wrapper locally
```bash
python3 calendar_sync.py --hours 12
```

### Show CLI help
```bash
python3 calendar_sync.py --help
```

### Verify fail-fast behavior with missing config
```bash
python3 calendar_sync.py
```
Expected behavior: exits with code `2` and reports missing `QQMAIL_USER` and/or `QQMAIL_AUTH_CODE`.

## Runtime requirements

The runtime expects the host environment to provide:

- `python3`
- `lark-cli`
- QQ Mail IMAP credentials
- an authenticated Lark CLI session
- configuration via `config.env` and/or process environment:
  - `QQMAIL_USER`
  - `QQMAIL_AUTH_CODE`
- optional configuration:
  - `LARK_CALENDAR_ID` (if unset, the runtime should auto-select the current Lark account's primary/default calendar)

`qqmail_lark_calendar/config.py` resolves config with **file values first, then environment variables**. This is important for stable one-shot runs in the host environment.

## High-level architecture

### End-to-end flow

`calendar_sync.py` is the public wrapper, but the important contract is a one-shot sync execution that can be triggered by an upper-level agent.

The flow is:

1. Parse `--hours` when using the local CLI wrapper.
2. Load config from `config.env` / environment and fail fast if any required field is missing.
3. Verify `lark-cli auth status` before doing any mail work.
4. Search QQ Mail IMAP for recent candidate emails.
5. Load local state from `.processed_emails.json` and `.processed_events.json`.
6. Skip subjects that were already processed.
7. Extract minimal interview info from each new email.
8. Append the QQ mail link into the final event description.
9. Upsert the Lark calendar event:
   - if the dedupe key already maps to an event ID, patch the existing event
   - otherwise create a new event and record its event ID
10. Persist both state files.
11. Return a readable summary for the skill caller; CLI mode also preserves exit-code behavior.

### Module responsibilities

- `calendar_sync.py`: wrapper entrypoint plus reusable one-shot sync orchestration/result summary.
- `qqmail_lark_calendar/config.py`: reads `config.env`, merges with process environment, validates required keys, and treats `LARK_CALENDAR_ID` as optional.
- `qqmail_lark_calendar/mail_imap.py`: connects to QQ Mail IMAP, searches recent candidate emails by subject keywords, decodes MIME content, and normalizes each result into `CandidateEmail`.
- `qqmail_lark_calendar/parse_interview.py`: performs minimal rule-based extraction for date/time ranges and generates a stable dedupe key. If no explicit time range is found, it creates a fallback 30-minute placeholder event based on the email timestamp.
- `qqmail_lark_calendar/lark_cli.py`: shell adapter around `lark-cli`; checks auth, auto-discovers the default/primary calendar when needed, creates calendar events, and patches existing events.
- `qqmail_lark_calendar/state_store.py`: reads/writes the two local JSON state files.

## State model

Two local files are central to idempotency:

- `.processed_emails.json`: a set-like list of processed email subjects used to avoid reprocessing the same subject.
- `.processed_events.json`: a mapping from parser-generated dedupe key to Lark `event_id`, used to decide between create vs update.

When changing parsing or dedupe behavior, consider the migration impact on both files. The current implementation treats email **subject** as the first-level processed marker, so changing subject-handling logic can affect reprocessing behavior.

## External integration details

### QQ Mail

QQ Mail scanning is subject-keyword based, not semantic classification. `mail_imap.py` currently searches for these Chinese subject keywords within the requested time window:

- `面试通知`
- `面试邀约`
- `面试安排`

### Lark

Lark writes go through `lark-cli`, not a Python SDK. `create_event()` uses `lark-cli calendar +create`; `patch_event()` uses a direct `lark-cli api PATCH` call to the calendar event endpoint. If Lark behavior changes, check CLI output parsing first.

## Boundaries to preserve

Unless the user explicitly requests otherwise, keep this repository as a non-onboarding, one-shot execution skill repository:

- do not reintroduce setup wizards or onboarding files into the main execution path
- do not add installation tutorials to the repo docs
- do not expand the parser into “AI semantic understanding” unless requested
- keep `SKILL.md` focused on invocation contract, and `README.md` focused on repository-level scope
- prefer maintaining the reusable sync execution path over baking more logic into CLI-only behavior
