"""
配置验证模块
各配置项的连通性/有效性检查
"""

import imaplib
import subprocess
import os
import re


def validate_qqmail_imap(email: str, auth_code: str) -> tuple[bool, str]:
    """
    验证 QQ 邮箱 IMAP 连接
    Returns: (success, message)
    """
    if not email or not auth_code:
        return False, "邮箱或授权码为空"

    try:
        mail = imaplib.IMAP4_SSL("imap.qq.com", 993)
        result, _ = mail.login(email, auth_code)
        mail.logout()
        if result == "OK":
            return True, "IMAP 连接成功"
        else:
            return False, f"登录失败: {result}"
    except imaplib.IMAP4.error as e:
        error_msg = str(e)
        if b"Authentication failed" in error_msg.encode() or "Authentication failed" in error_msg:
            return False, "认证失败，授权码可能已过期，请到 QQ 邮箱重新获取"
        elif "connection" in error_msg.lower():
            return False, "无法连接到 QQ 邮箱服务器，请检查网络或 IMAP 服务是否开启"
        else:
            return False, f"IMAP 错误: {error_msg}"
    except Exception as e:
        return False, f"连接异常: {str(e)}"


def validate_lark_auth() -> tuple[bool, str]:
    """
    验证 Lark 授权状态（通过 lark-cli）
    Returns: (success, message)
    """
    try:
        result = subprocess.run(
            ["lark-cli", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout + result.stderr

        if result.returncode == 0 and ("logged in" in output.lower() or "已登录" in output):
            return True, "Lark 授权正常"
        elif "not logged in" in output.lower() or "未登录" in output:
            return False, "Lark 未登录，请先运行 lark-cli auth login"
        else:
            return False, f"授权状态未知: {output[:200]}"
    except FileNotFoundError:
        return False, "未找到 lark-cli，请确认已安装并加入 PATH"
    except subprocess.TimeoutExpired:
        return False, "lark-cli auth status 执行超时"
    except Exception as e:
        return False, f"检查 Lark 授权时异常: {str(e)}"


def check_config_complete(config_path: str = "config.env") -> tuple[bool, dict]:
    """
    检查 config.env 是否包含所有必填项
    Returns: (is_complete, fields_dict)
    fields_dict: {field_name: (filled, value)}
    """
    required_fields = ["QQMAIL_USER", "QQMAIL_AUTH_CODE"]
    optional_fields = ["LARK_APP_ID", "LARK_APP_SECRET"]

    fields = {}
    all_required_filled = True

    if not os.path.exists(config_path):
        for f in required_fields + optional_fields:
            fields[f] = (False, None)
        return False, fields

    with open(config_path, "r") as f:
        content = f.read()

    all_fields = required_fields + optional_fields
    for field in all_fields:
        # 支持 "KEY=value" 或 "KEY = value" 格式
        pattern = rf'^{field}\s*=\s*(.+)$'
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            value = match.group(1).strip()
            filled = len(value) > 0
            fields[field] = (filled, value if filled else None)
        else:
            fields[field] = (False, None)

        if field in required_fields and not fields[field][0]:
            all_required_filled = False

    return all_required_filled, fields


def read_config_field(field: str, config_path: str = "config.env") -> str | None:
    """读取 config.env 中的指定字段值"""
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r") as f:
        content = f.read()
    pattern = rf'^{field}\s*=\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else None
