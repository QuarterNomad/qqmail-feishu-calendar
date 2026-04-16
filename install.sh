#!/bin/bash
set -e

SKILLS_DIR="$HOME/.openclaw/workspace/skills"
SKILL_NAME="qqmail-lark-calendar"
SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"
CONFIG_TEMPLATE="config.env.example"
CONFIG_FILE="config.env"
ARCHIVE_URL="https://github.com/QuarterNomad/qqmail-feishu-calendar/archive/refs/heads/main.tar.gz"
TMP_DIR="$(mktemp -d)"
ARCHIVE_PATH="$TMP_DIR/skill.tar.gz"
STAGING_DIR="$TMP_DIR/staging"
BACKUP_DIR="$TMP_DIR/backup"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

printf '🚀 Installing %s into OpenClaw workspace\n\n' "$SKILL_NAME"

mkdir -p "$SKILLS_DIR"
mkdir -p "$STAGING_DIR" "$BACKUP_DIR"

printf '📦 Downloading latest source archive...\n'
curl -fsSL "$ARCHIVE_URL" -o "$ARCHIVE_PATH"

tar -xzf "$ARCHIVE_PATH" -C "$STAGING_DIR"
EXTRACTED_DIR="$(find "$STAGING_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"

if [ -z "$EXTRACTED_DIR" ]; then
  printf '❌ Failed to extract skill archive.\n'
  exit 1
fi

if [ -f "$SKILL_PATH/$CONFIG_FILE" ]; then
  cp "$SKILL_PATH/$CONFIG_FILE" "$BACKUP_DIR/$CONFIG_FILE"
fi

if [ -f "$SKILL_PATH/.processed_emails.json" ]; then
  cp "$SKILL_PATH/.processed_emails.json" "$BACKUP_DIR/.processed_emails.json"
fi

if [ -f "$SKILL_PATH/.processed_events.json" ]; then
  cp "$SKILL_PATH/.processed_events.json" "$BACKUP_DIR/.processed_events.json"
fi

rm -rf "$SKILL_PATH"
mkdir -p "$SKILL_PATH"
cp -R "$EXTRACTED_DIR"/. "$SKILL_PATH"

if [ -f "$BACKUP_DIR/$CONFIG_FILE" ]; then
  cp "$BACKUP_DIR/$CONFIG_FILE" "$SKILL_PATH/$CONFIG_FILE"
elif [ -f "$SKILL_PATH/$CONFIG_TEMPLATE" ]; then
  cp "$SKILL_PATH/$CONFIG_TEMPLATE" "$SKILL_PATH/$CONFIG_FILE"
  printf '📝 Created %s from template.\n' "$SKILL_PATH/$CONFIG_FILE"
fi

if [ -f "$BACKUP_DIR/.processed_emails.json" ]; then
  cp "$BACKUP_DIR/.processed_emails.json" "$SKILL_PATH/.processed_emails.json"
fi

if [ -f "$BACKUP_DIR/.processed_events.json" ]; then
  cp "$BACKUP_DIR/.processed_events.json" "$SKILL_PATH/.processed_events.json"
fi

if ! command -v python3 >/dev/null 2>&1; then
  printf '❌ Missing prerequisite: python3\n'
  exit 1
fi

if ! command -v lark-cli >/dev/null 2>&1; then
  printf '⚠️  Missing prerequisite: lark-cli\n'
  printf '   See: https://github.com/larksuite/cli\n'
fi

printf '\n✅ Install complete.\n\n'
printf 'Next steps:\n'
printf '1. Edit %s/%s and fill QQMAIL_USER, QQMAIL_AUTH_CODE\n' "$SKILL_PATH" "$CONFIG_FILE"
printf '   QQ Mail IMAP / 授权码说明: https://service.mail.qq.com/detail/0/75\n'
printf '2. Optional: set LARK_CALENDAR_ID if you do not want to use the primary Lark calendar\n'
printf '3. Verify with: python3 %s/calendar_sync.py --hours 12\n' "$SKILL_PATH"
