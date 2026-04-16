from __future__ import annotations

import email
import email.header
import email.utils
import html
import imaplib
import ssl
from dataclasses import dataclass
from datetime import datetime, timedelta
from html.parser import HTMLParser


@dataclass(frozen=True)
class CandidateEmail:
    subject: str
    from_: str
    date_display: str
    body_text: str
    msg_id: str


def decode_header_value(raw) -> str:
    if raw is None:
        return ""
    parts = email.header.decode_header(raw)
    return "".join(
        d.decode(c or "utf-8", errors="replace") if isinstance(d, bytes) else d for d, c in parts
    )


def _extract_text_from_html_or_plain(msg: email.message.Message) -> str:
    body = ""
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
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")

    class _TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.texts: list[str] = []
            self.skip = False

        def handle_starttag(self, tag, attrs):
            if tag in ("style", "script", "head"):
                self.skip = True

        def handle_endtag(self, tag):
            if tag in ("style", "script", "head"):
                self.skip = False

        def handle_data(self, data):
            if not self.skip and data.strip():
                self.texts.append(data.strip())

    html_text = html.unescape(body)
    parser = _TextExtractor()
    parser.feed(html_text)
    text = "\n".join(parser.texts)
    return text[:5000].strip()


def connect_qqmail_imap(user: str, auth_code: str) -> imaplib.IMAP4_SSL:
    ctx = ssl.create_default_context()
    conn = imaplib.IMAP4_SSL("imap.qq.com", 993, ssl_context=ctx)
    conn.login(user, auth_code)

    # 让 search/fetch 支持 UTF-8 关键词（复用旧脚本做法）
    _orig = conn._command

    def _utf8_cmd(name, *args):
        encoded = [(a.encode("utf-8") if isinstance(a, str) else a) for a in args]
        return _orig(name, *encoded)

    conn._command = _utf8_cmd
    return conn


def search_candidate_emails(user: str, auth_code: str, *, hours: int = 12) -> list[CandidateEmail]:
    conn = connect_qqmail_imap(user, auth_code)
    try:
        conn.select("INBOX", readonly=True)
        keywords = ["面试通知", "面试邀约", "面试安排"]
        since_datetime = datetime.now() - timedelta(hours=hours)
        date_imap = since_datetime.strftime("%d-%b-%Y")

        results: list[CandidateEmail] = []
        for kw in keywords:
            status, messages = conn.search(
                "UTF-8",
                "SUBJECT",
                kw.encode("utf-8"),
                "SINCE",
                date_imap.encode("utf-8"),
            )
            if status != "OK":
                continue
            msg_ids = messages[0].split()
            if not msg_ids:
                continue
            msg_ids.reverse()
            for msg_id in msg_ids:
                status, data = conn.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue
                raw = data[0][1]
                msg = (
                    email.message_from_bytes(raw)
                    if isinstance(raw, (bytes, bytearray))
                    else email.message_from_string(raw)
                )
                subject = decode_header_value(msg.get("Subject", ""))
                from_ = decode_header_value(msg.get("From", ""))
                date_str = msg.get("Date", "")
                date_parsed = email.utils.parsedate_to_datetime(date_str) if date_str else None
                date_display = date_parsed.strftime("%Y-%m-%d %H:%M") if date_parsed else ""
                body_text = _extract_text_from_html_or_plain(msg)
                results.append(
                    CandidateEmail(
                        subject=subject,
                        from_=from_,
                        date_display=date_display,
                        body_text=body_text,
                        msg_id=msg_id.decode(),
                    )
                )
        return results
    finally:
        try:
            conn.logout()
        except Exception:
            pass

