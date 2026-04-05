#!/usr/bin/env python3
"""
QQ Mail → Feishu Calendar 同步脚本（AI 判断版）
代码粗筛 → AI 精判

凭证配置：~/.openclaw/workspace/skills/qqmail-feishu-calendar/config.env
"""

import os, re, json, html, imaplib, email, email.header, email.utils, subprocess, ssl
from datetime import datetime, timedelta
from pathlib import Path

# ============ 凭证路径 ============
SKILL_DIR = Path(__file__).parent
CONFIG_FILE = SKILL_DIR / 'config.env'
STATE_FILE = SKILL_DIR / '.processed_emails.json'

# ============ 读取凭证 ============
def load_env():
    env = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    return env

env = load_env()
QQMAIL_USER = env.get('QQMAIL_USER', os.environ.get('QQMAIL_USER', ''))
QQMAIL_AUTH_CODE = env.get('QQMAIL_AUTH_CODE', os.environ.get('QQMAIL_AUTH_CODE', ''))

if not QQMAIL_USER or not QQMAIL_AUTH_CODE:
    print("❌ 凭证未配置。请编辑 config.env 填写 QQMAIL_USER 和 QQMAIL_AUTH_CODE")
    exit(1)

# ============ IMAP ============
def connect_imap():
    ctx = ssl.create_default_context()
    conn = imaplib.IMAP4_SSL("imap.qq.com", 993, ssl_context=ctx)
    conn.login(QQMAIL_USER, QQMAIL_AUTH_CODE)
    _orig = conn._command
    def _utf8_cmd(name, *args):
        encoded = [(a.encode('utf-8') if isinstance(a, str) else a) for a in args]
        return _orig(name, *encoded)
    conn._command = _utf8_cmd
    return conn

def decode_header_value(raw):
    if raw is None: return ""
    parts = email.header.decode_header(raw)
    return "".join(d.decode(c or "utf-8", errors="replace") if isinstance(d, bytes) else d for d, c in parts)

def get_email_body(msg):
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            disp = str(part.get("Content-Disposition", ""))
            if ct == "text/html" and "attachment" not in disp:
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    break
        if not body:
            for part in msg.walk():
                ct = part.get_content_type()
                if ct == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    # HTML 标签清理
    from html.parser import HTMLParser
    class _TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.texts = []
            self.skip = False
        def handle_starttag(self, tag, attrs):
            if tag in ('style','script','head'): self.skip = True
        def handle_endtag(self, tag):
            if tag in ('style','script','head'): self.skip = False
        def handle_data(self, data):
            if not self.skip and data.strip():
                self.texts.append(data.strip())
    html_text = html.unescape(body)
    parser = _TextExtractor()
    parser.feed(html_text)
    text = '\n'.join(parser.texts)
    return text[:5000].strip()

# ============ 搜索候选邮件 ============
def search_candidates(days=3):
    conn = connect_imap()
    try:
        conn.select('INBOX', readonly=True)
        keywords = ['面试通知', '面试邀约', '面试安排']
        results = []
        for kw in keywords:
            date_imap = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
            criteria_args = ['SUBJECT', kw.encode('utf-8'), 'SINCE', date_imap.encode('utf-8')]
            status, messages = conn.search('UTF-8', *criteria_args)
            if status != 'OK': continue
            msg_ids = messages[0].split()
            if not msg_ids: continue
            msg_ids.reverse()
            for msg_id in msg_ids:
                status, data = conn.fetch(msg_id, '(RFC822)')
                if status != 'OK': continue
                raw = data[0][1]
                msg = email.message_from_bytes(raw) if isinstance(raw, bytes) else email.message_from_string(raw)
                subj = decode_header_value(msg.get('Subject', ''))
                frm = decode_header_value(msg.get('From', ''))
                date_str = msg.get('Date', '')
                date_parsed = email.utils.parsedate_to_datetime(date_str) if date_str else None
                date_display = date_parsed.strftime('%Y-%m-%d %H:%M') if date_parsed else ''
                body_text = get_email_body(msg)
                results.append({
                    'subject': subj,
                    'from': frm,
                    'date': date_display,
                    'body': body_text,
                    'msg_id': msg_id.decode()
                })
        return results
    finally:
        conn.logout()

# ============ 本地记录已处理邮件 ============
def load_processed():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return set(json.load(f))
        except: return set()
    return set()

def save_processed(keys):
    with open(STATE_FILE, 'w') as f:
        json.dump(list(keys), f)

# ============ 主流程 ============
def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 扫描 QQ 邮箱...")

    candidates = search_candidates(days=3)
    print(f"  找到 {len(candidates)} 封候选邮件")

    if not candidates:
        print("  无候选邮件")
        return

    processed = load_processed()
    new_emails = [e for e in candidates if e['subject'] not in processed]

    if not new_emails:
        print(f"  全部已处理（{len(candidates)} 封）")
        return

    print(f"\n  === 新邮件 {len(new_emails)} 封 ===")
    for e in new_emails:
        print(f"\n  [{e['date']}] {e['subject']}")
        print(f"  From: {e['from'][:60]}")
        print(f"  QQ邮件链接: https://mail.qq.com/cgi-bin/readmail?mailid={e['msg_id']}")
        print(f"  正文前600字:\n  {e['body'][:600]}")
        print()

    # 标记为已处理（同一标题不再重复扫）
    for e in new_emails:
        processed.add(e['subject'])
    save_processed(processed)
    print(f"已标记 {len(new_emails)} 封为已处理，下次扫描将跳过")

if __name__ == '__main__':
    main()
