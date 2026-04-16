# qqmail-feishu-calendar

扫描 QQ 邮箱面试通知类邮件，提取最低配关键信息，并通过 `lark-cli` 写入飞书日历（支持幂等去重与定时运行）。

## 当前能力

- 扫描 QQ 邮箱近 12 小时内、主题包含以下关键词的邮件：
  - `面试通知`
  - `面试邀约`
  - `面试安排`
- 提取最低配面试信息（优先从正文匹配“日期 + 起止时间”，匹配不到则创建“待确认时间”的占位事件）
- 创建/更新飞书日历事件（通过 `lark-cli`）
- 幂等去重：
  - `.processed_emails.json`：按邮件标题去重，避免重复处理
  - `.processed_events.json`：按去重键记录 `event_id`，重复运行优先更新事件

## 当前不包含的能力

以下能力目前仍未在代码中实现：

- AI 判断邮件中的面试时间
- 区分面试时间与截止时间
- 基于“公司 + 时间”的事件级查重

如果后续要支持这些能力，需要继续扩展 `qqmail_feishu_calendar/parse_interview.py` 与去重策略。

## 运行环境

- Python 3.8+
- macOS 或 Linux
- `lark-cli`（用于日历写入）

安装 `lark-cli`：

```bash
npm install -g @larksuite/cli
```

## 配置

### 1. 获取 QQ 邮箱 IMAP 授权码

1. 打开 [mail.qq.com](https://mail.qq.com) 并登录
2. 点击右上角 **设置** → **账号与安全**
3. 点击 **安全设置**
4. 下拉到页面底部，开启 IMAP 服务
5. 按提示完成短信验证
6. 获取授权码（形如 `xxxx xxxx xxxx`）

### 2. 登录飞书（可选但脚本会检查状态）

```bash
lark-cli auth login --recommend
lark-cli auth status
```

### 3. 写入配置文件

在项目根目录创建 `config.env`，内容如下：

```env
QQMAIL_USER=<你的QQ邮箱>
QQMAIL_AUTH_CODE=<IMAP授权码>
FEISHU_CALENDAR_ID=primary
```

也可以从模板复制：

```bash
cp config.env.example config.env
```

### 4. 选择写入哪个日历（calendar_id）
本项目使用 `FEISHU_CALENDAR_ID` 作为写入目标：
- **推荐先用**：`primary`
- 如果你要写入指定日历：用 `lark-cli calendar calendars list --format json` 查出日历列表并选择对应 `calendar_id`，把它写进 `config.env`

### 4. 交互式配置（可选）

如果希望一步步引导填写并校验配置：

```bash
python3 setup_wizard.py
```

## 使用方式

### 手动运行（推荐非交互）

```bash
python3 calendar_sync.py --non-interactive --hours 12
```

运行后脚本会：

1. 检查 `config.env` 是否完整（缺失则退出并提示）
2. 校验 `lark-cli auth status` 已登录（未登录则退出）
3. 连接 QQ 邮箱 IMAP
4. 搜索近 `--hours` 小时的候选邮件
5. 对新邮件创建/更新飞书日历事件
6. 更新 `.processed_emails.json` 与 `.processed_events.json`

### 定时运行示例

如果你希望定时运行，有两种方式：

#### A. 系统 cron（最简单）
每 6 小时执行一次：

```bash
0 */6 * * * cd /path/to/qqmail-feishu-calendar && python3 calendar_sync.py
```

#### B. OpenClaw Cron（推荐）
前提：你把仓库放进 OpenClaw workspace 的 `./skills/qqmail-feishu-calendar/`，并确保 `config.env` 与 `lark-cli` 登录状态在网关主机上可用。

示例（每 6 小时跑一次；注意 `--to` 需要替换为你的投递目标）：

```bash
openclaw cron add \
  --name "qqmail-feishu-calendar-sync" \
  --every "6h" \
  --session isolated \
  --message "同步 QQ 邮箱面试通知到飞书日历（非交互）" \
  --announce \
  --to "chat:YOUR_CHAT_ID"
```

验证与排错：
- `openclaw cron list`
- `openclaw cron run <job-id>`
- `openclaw cron runs --id <job-id>`

## 项目结构

```text
qqmail-feishu-calendar/
├── calendar_sync.py        # 入口脚本：参数解析 + 调度（cron 运行用）
├── qqmail_feishu_calendar/ # 核心逻辑包（IMAP/解析/状态/飞书写入）
├── setup_wizard.py         # 交互式配置引导
├── config_validator.py     # 配置与连通性检查
├── config.env.example      # 配置模板
├── SKILL.md                # 面向 agent 的 skill 执行规范
├── README.md               # 面向人类用户的项目说明
├── .processed_emails.json  # 已处理邮件标题记录（运行后生成）
└── .processed_events.json  # 已写入日历事件映射（运行后生成）
```

## 已知限制

- 目前只支持 QQ 邮箱 IMAP
- 关键词筛选依赖邮件主题，不会理解正文语义
- 已处理记录只按邮件标题去重，标题相同可能被视为同一封邮件
- 时间解析为最低配规则匹配，可能创建“待确认时间”的占位事件

## License

[MIT License](./LICENSE)
