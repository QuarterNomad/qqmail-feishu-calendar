---
name: qqmail-lark-calendar
description: standalone skill/runtime。扫描 QQ 邮箱面试通知邮件，提取关键信息并通过 lark-cli 写入 Lark 日历，支持幂等去重与非交互运行。用于“同步/扫描 QQ 邮箱面试通知到 Lark 日历”等场景；不用于 onboarding、交互式初始化或实现讲解。
---

# qqmail-lark-calendar

## 适用场景（触发词）
- 用户要求“同步/扫描/检查 QQ 邮箱里的面试通知”
- 用户要求“把面试邮件写到 Lark 日历”
- 用户希望运行一次该 skill，或把它接入外部调度系统

## 不适用场景
- 需要交互式配置引导
- 需要安装教学或 onboarding
- 只讨论原理、结构或代码实现
- 用户要求 AI 级语义理解、精准区分截止时间与面试时间

## 前置条件
该 skill 只接受非交互运行。外部宿主系统必须提前提供：

- `python3`
- `lark-cli`
- 已可用的 QQ 邮箱 IMAP 凭证
- 已登录的 Lark CLI 会话
- 完整配置：
  - `QQMAIL_USER`
  - `QQMAIL_AUTH_CODE`
  - `LARK_CALENDAR_ID`

## 执行命令
```bash
python3 "{baseDir}/calendar_sync.py" --hours 12
```

## 执行行为
一次运行应完成：
- 扫描 QQ 邮箱 IMAP 中近 `--hours` 小时的候选邮件
- 对新邮件提取最低配面试信息
- 幂等写入 Lark 日历：已存在则更新，否则创建
- 更新状态文件：
  - `{baseDir}/.processed_emails.json`
  - `{baseDir}/.processed_events.json`

## 输出与退出码
- **退出码 0**：执行成功（包括“无候选邮件”）
- **退出码 2**：配置缺失或不完整
- **退出码 3**：Lark CLI 不可用、未登录或权限不足
- **退出码 4**：QQ 邮箱 IMAP 失败
- **退出码 5**：写入 Lark 日历失败
- **退出码 1**：其他未分类异常

成功输出应包含：
- 扫描窗口
- 候选邮件数
- 创建事件数
- 更新事件数
- 失败数

失败输出应包含：
- 失败阶段
- 关键错误信息

## 输出边界
本 skill 当前不会：
- 提供交互式初始化
- 自动生成配置文件
- 提供安装/登录教学
- 做 AI 级正文语义解析

## 相关文件
- `{baseDir}/calendar_sync.py`
- `{baseDir}/qqmail_lark_calendar/config.py`
- `{baseDir}/qqmail_lark_calendar/mail_imap.py`
- `{baseDir}/qqmail_lark_calendar/parse_interview.py`
- `{baseDir}/qqmail_lark_calendar/lark_cli.py`
- `{baseDir}/qqmail_lark_calendar/state_store.py`
