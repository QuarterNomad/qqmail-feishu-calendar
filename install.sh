#!/bin/bash
set -e

SKILLS_DIR="$HOME/.openclaw/workspace/skills"
SKILL_NAME="qqmail-lark-calendar"
SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"
CONFIG_TEMPLATE="config.env.example"
CONFIG_FILE="config.env"
REPO_URL="https://github.com/zhanzhifan/qqmail-feishu-calendar.git"

printf '🚀 Installing %s into OpenClaw workspace\n\n' "$SKILL_NAME"

mkdir -p "$SKILLS_DIR"

if [ -d "$SKILL_PATH/.git" ]; then
  printf '📦 Existing install found, updating %s...\n' "$SKILL_PATH"
  git -C "$SKILL_PATH" pull --ff-only
else
  if [ -e "$SKILL_PATH" ]; then
    printf '❌ Target path exists but is not a git repo: %s\n' "$SKILL_PATH"
    exit 1
  fi
  printf '📦 Cloning %s to %s...\n' "$REPO_URL" "$SKILL_PATH"
  git clone "$REPO_URL" "$SKILL_PATH"
fi

if ! command -v python3 >/dev/null 2>&1; then
  printf '❌ Missing prerequisite: python3\n'
  exit 1
fi

if ! command -v lark-cli >/dev/null 2>&1; then
  printf '⚠️  Missing prerequisite: lark-cli\n'
  printf '   Install lark-cli before running the skill.\n'
fi

if [ ! -f "$SKILL_PATH/$CONFIG_FILE" ] && [ -f "$SKILL_PATH/$CONFIG_TEMPLATE" ]; then
  cp "$SKILL_PATH/$CONFIG_TEMPLATE" "$SKILL_PATH/$CONFIG_FILE"
  printf '📝 Created %s from template.\n' "$SKILL_PATH/$CONFIG_FILE"
fi

printf '\n✅ Install complete.\n\n'
printf 'Next steps:\n'
printf '1. Edit %s/%s and fill QQMAIL_USER, QQMAIL_AUTH_CODE, LARK_CALENDAR_ID\n' "$SKILL_PATH" "$CONFIG_FILE"
printf '2. Run: lark-cli auth login\n'
printf '3. Verify with: python3 %s/calendar_sync.py --hours 12\n' "$SKILL_PATH"
