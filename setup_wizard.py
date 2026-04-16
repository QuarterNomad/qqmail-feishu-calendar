#!/usr/bin/env python3
"""
引导式配置流程
逐步引导用户完成所有配置项的填写和验证，无跳过选项
"""

import os
import sys
import shutil
from pathlib import Path

from config_validator import (
    validate_qqmail_imap,
    validate_lark_auth,
    check_config_complete,
)

SCRIPT_DIR = Path(__file__).parent
DEFAULT_CONFIG_PATH = SCRIPT_DIR / "config.env"
EXAMPLE_CONFIG_PATH = SCRIPT_DIR / "config.env.example"


def print_step(step: int, total: int, title: str):
    print(f"\n{'='*50}")
    print(f"  步骤 {step}/{total}: {title}")
    print('='*50)


def print_ok(msg: str):
    print(f"  ✅ {msg}")


def print_err(msg: str):
    print(f"  ❌ {msg}")


def print_info(msg: str):
    print(f"  ℹ️  {msg}")


def write_config_field(field: str, value: str, config_path: Path = DEFAULT_CONFIG_PATH):
    """更新 config.env 中的单个字段"""
    if not config_path.exists():
        if EXAMPLE_CONFIG_PATH.exists():
            shutil.copy(EXAMPLE_CONFIG_PATH, config_path)
        else:
            config_path.write_text("")

    with open(config_path, "r") as f:
        lines = f.readlines()

    field_pattern = f"{field}="
    found = False
    new_lines = []
    for line in lines:
        if line.startswith(field_pattern) or line.startswith(field + " ="):
            new_lines.append(f"{field}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{field}={value}\n")

    with open(config_path, "w") as f:
        f.writelines(new_lines)


def run_wizard():
    print("\n" + "🧙  QQ邮箱 → Lark 日历 配置引导")
    print("    按提示逐步完成配置，按 Ctrl+C 可随时退出\n")

    total_steps = 3

    # Step 1: 初始化 config.env
    print_step(1, total_steps, "初始化配置文件")
    if not DEFAULT_CONFIG_PATH.exists():
        if EXAMPLE_CONFIG_PATH.exists():
            shutil.copy(EXAMPLE_CONFIG_PATH, DEFAULT_CONFIG_PATH)
            print_ok("已从 config.env.example 创建配置文件")
        else:
            DEFAULT_CONFIG_PATH.write_text("")
            print_info("已创建空白配置文件")
    else:
        print_ok("配置文件已存在")

    # Step 2: QQ 邮箱配置（必填，每步验证）
    print_step(2, total_steps, "配置 QQ 邮箱 IMAP")

    is_complete, fields = check_config_complete(str(DEFAULT_CONFIG_PATH))
    email = fields.get("QQMAIL_USER", (False, None))[1]
    auth_code = fields.get("QQMAIL_AUTH_CODE", (False, None))[1]

    # 只在未填写时引导，不给跳过选项
    if not email:
        print("\n  请填写 QQ 邮箱地址（用于接收面试通知）：")
        email = input("  QQ 邮箱地址: ").strip()
        while not email:
            print_err("邮箱不能为空，请重新输入")
            email = input("  QQ 邮箱地址: ").strip()
        write_config_field("QQMAIL_USER", email)
        print_ok(f"已保存邮箱: {email}")
    else:
        print_ok(f"已配置邮箱: {email}")

    # 授权码
    if not auth_code:
        print("\n  请填写 QQ 邮箱 IMAP 授权码：")
        print_info("获取方式：QQ邮箱设置 → 账户 → IMAP/SMTP服务 → 开启 → 发送短信获取")
        print_info("授权码格式形如: xxxx xxxx xxxx")
        auth_code = input("  IMAP 授权码: ").strip()
        while not auth_code:
            print_err("授权码不能为空，请重新输入")
            auth_code = input("  IMAP 授权码: ").strip()
        write_config_field("QQMAIL_AUTH_CODE", auth_code)
        print_ok("已保存授权码")
    else:
        print_ok("已配置授权码")

    # 每步必验证，失败不退出而是要求重新输入
    while True:
        print("\n  正在验证 IMAP 连接...")
        ok, msg = validate_qqmail_imap(email, auth_code)
        if ok:
            print_ok(msg)
            break
        else:
            print_err(msg)
            print_err("请重新获取授权码后再次运行 setup_wizard.py")
            sys.exit(1)

    # Step 3: Lark 授权（必填，每步验证）
    print_step(3, total_steps, "配置 Lark 日历授权")

    while True:
        auth_ok, auth_msg = validate_lark_auth()
        if auth_ok:
            print_ok("Lark 授权正常")
            break
        else:
            print_err(f"Lark 授权异常: {auth_msg}")
            print_info("请在另一个终端运行以下命令完成授权：")
            print("    lark-cli auth login")
            print_info("授权完成后回到本界面按回车继续验证...")
            input("  按回车继续验证: ")
            # 循环继续，重新验证

    # 完成
    print(f"\n{'='*50}")
    print("  🎉 配置完成！")
    print('='*50)
    print("\n  可选后续操作：")
    print("    1. 测试运行: python3 calendar_sync.py")
    print("    2. 创建定时任务，让 OpenClaw 自动同步")
    print()


if __name__ == "__main__":
    run_wizard()
