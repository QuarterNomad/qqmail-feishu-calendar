---
name: qqmail-feishu-calendar
description: 扫描 QQ 邮箱面试通知邮件，提取关键信息并写入飞书日历（通过 lark-cli），支持幂等去重与 OpenClaw cron 非交互定时运行。用于“同步/扫描 QQ 邮箱面试通知到飞书日历”“定时同步面试邀约”等场景；不用于讲解实现细节或交互式配置引导。
---

# qqmail-feishu-calendar

## 适用场景（触发词）
- 用户要求“同步/扫描/检查 QQ 邮箱里的面试通知”“把面试邮件写到飞书日历”“定时同步面试邀约”
- 用户已完成配置，希望**运行一次**或**定时运行**全流程

## 不适用场景
- 只讨论原理/结构/代码实现（这类直接回答，不要跑脚本）
- 需要交互式引导配置（引导属于 onboarding，请让用户按 `README.md` 处理）
- 用户要求“AI 精准解析正文语义/区分截止时间 vs 面试时间”（本版本只做最低配规则提取与可重复落日历）

## 前置条件（非交互）
必须满足以下条件，否则 **cron/非交互模式应直接失败退出**：
- **配置文件**：`{baseDir}/config.env` 存在并包含：
  - `QQMAIL_USER`
  - `QQMAIL_AUTH_CODE`
  - `FEISHU_CALENDAR_ID`（写入目标日历；可用 `"primary"` 或实际 `cal_...`，以 README 为准）
- **可执行文件**：
  - `python3`
  - `lark-cli`（`lark-cli auth status` 可执行且已登录，具备日历写入权限）

## 一次执行（推荐命令）
### 非交互（cron/无人值守）
只允许用非交互模式运行（缺配置就失败，不进入向导）：

```bash
python3 "{baseDir}/calendar_sync.py" --non-interactive --hours 12
```

### 交互式（仅首次人工初始化）
如果是第一次配置，请按 `README.md` 先完成初始化（例如运行 `python3 setup_wizard.py`、`lark-cli auth login`），再回到非交互命令。

## 执行行为（本 skill 约定）
一次运行应完成：
- 扫描 QQ 邮箱 IMAP（默认近 `--hours` 小时），主题包含：`面试通知`/`面试邀约`/`面试安排`
- 对新邮件做最低配信息提取（标题、时间窗口/地点（若可提取）、原始链接等）
- **幂等写入飞书日历**：
  - 事件已存在则更新（event_id 已记录时优先 patch）
  - 否则创建新事件
- 更新本地状态文件（都在 `{baseDir}`）：
  - `.processed_emails.json`：邮件去重
  - `.processed_events.json`：事件幂等（去重键 → event_id）

## 输出与退出码（用于 cron 判定）
- **退出码 0**：本次运行成功（即使“无新邮件”也算成功）
- **退出码 2**：配置缺失/不完整（提示用户按 `README.md` 初始化）
- **退出码 3**：`lark-cli` 不可用或未登录/权限不足
- **退出码 4**：QQ 邮箱 IMAP 认证失败/连接失败
- **退出码 5**：写入飞书日历失败（创建/更新 API 失败）
- **退出码 1**：其他未分类异常

成功输出需包含：
- 扫描窗口（hours）、候选邮件数、新邮件数
- 创建/更新事件数量、跳过数量

失败输出需包含：
- 失败阶段（config / imap / parse / feishu）
- 关键错误信息原样保留（便于定位）

## 相关文件（只做指引，不在此展开 onboarding）
- `{baseDir}/calendar_sync.py`：入口脚本（非交互 cron 运行用）
- `{baseDir}/setup_wizard.py`：交互式初始化（仅人工）
- `{baseDir}/README.md`：安装/配置/cron 创建/排错
