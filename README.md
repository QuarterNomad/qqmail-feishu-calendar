# qqmail-lark-calendar

这是一个面向 OpenClaw / agent 调用的一次性执行 skill 仓库，也已经补齐了从 GitHub 分发到 OpenClaw workspace 的基础包装层。

它负责：
- 扫描 QQ 邮箱中的面试通知类邮件
- 基于当前最小规则提取面试信息
- 通过 `lark-cli` 创建或更新 Lark 日历事件
- 持久化本地状态以支持重复调用
- 在日历描述中补充对应 QQ 邮件链接

这个仓库不负责托管凭证、自动登录 Lark 或交互式 onboarding；这些前置条件仍需由 OpenClaw 宿主环境或最终用户自行提供。

## 安装到 OpenClaw

### 方式一：一键安装

```bash
curl -sSL https://raw.githubusercontent.com/QuarterNomad/qqmail-feishu-calendar/main/install.sh | bash
```

### 方式二：手动安装

如果你已经手动下载了仓库，也可以直接在仓库根目录执行：

```bash
./install.sh
```

安装脚本会把仓库源码包下载并解压到：

```bash
~/.openclaw/workspace/skills/qqmail-lark-calendar
```

如果该目录已经存在，脚本会用最新源码包刷新 skill 文件，并保留已有 `config.env`；如果缺少 `config.env`，会基于 `config.env.example` 创建模板文件。安装脚本只负责安装 skill 本体并检查前置依赖；如果缺少 `lark-cli`，只会提示官方仓库地址。

## 前置依赖

运行这个 skill 前，外部环境需要已经提供 `lark-cli`。如果安装脚本检测不到它，只会提示你查看官方仓库：

- 飞书 / Lark CLI：https://github.com/larksuite/cli
- QQ 邮箱 IMAP / 授权码说明：https://service.mail.qq.com/detail/0/75

## 安装后需要做的事

1. 编辑 `~/.openclaw/workspace/skills/qqmail-lark-calendar/config.env`
2. 填写：
   - `QQMAIL_USER`
   - `QQMAIL_AUTH_CODE`
3. 如需指定非主日历，可额外填写：
   - `LARK_CALENDAR_ID`

## 手动验证

```bash
python3 ~/.openclaw/workspace/skills/qqmail-lark-calendar/calendar_sync.py --hours 12
```

如果配置缺失，脚本会提示缺少哪些变量；如果 Lark 未登录，会直接报鉴权失败。

## 定时任务示例

如果要让 OpenClaw 把这个 skill 配置成定时任务，可以每 6 小时执行一次：

```bash
python3 /root/.openclaw/workspace/skills/qqmail-lark-calendar/calendar_sync.py --hours 12
```

## 适用场景

当用户在 OpenClaw 或其他上层智能体里表达类似意图时，应调用这个 skill：

- 根据面试邮件安排飞书日历
- 扫描最近的面试通知并同步到 Lark 日历
- 把 QQ 邮箱里的面试邀约写到飞书日历

## OpenClaw 分发文件

仓库根目录新增了用于 GitHub / OpenClaw 分发的包装文件：

- `skill.json`：用于描述 skill 的基本元信息
- `agents/openai.yaml`：用于声明展示名、简介和默认 prompt
- `install.sh`：用于把仓库安装到 `~/.openclaw/workspace/skills/qqmail-lark-calendar`
- `config.env.example`：用于生成本地 `config.env` 模板

## 运行时约束

运行该 skill 前，外部环境需要自行提供：

- Python 3.8+
- `lark-cli`（若缺失，仅提示查看官方仓库：https://github.com/larksuite/cli）
- QQ 邮箱 IMAP 可用凭证
- Lark 登录状态
- 完整配置：
  - `QQMAIL_USER`
  - `QQMAIL_AUTH_CODE`
- 可选配置：
  - `LARK_CALENDAR_ID`（留空时自动使用当前 Lark 账号的主日历）

## 入口命令

```bash
python3 calendar_sync.py --hours 12
```

上面的命令可作为本地/脚本包装方式；但这个仓库的主定位是被上层智能体按意图触发的一次性 skill，而不是以 cron 为中心的仓库。

## 项目结构

```text
qqmail-lark-calendar/
├── agents/
│   └── openai.yaml           # OpenClaw / agent 接口元数据
├── calendar_sync.py          # 一次性执行入口：CLI 包装 + skill 可复用主流程
├── config.env.example        # OpenClaw 安装后复制为 config.env 的模板
├── install.sh                # GitHub → OpenClaw workspace 安装脚本
├── qqmail_lark_calendar/     # 核心逻辑包（配置 / IMAP / 解析 / Lark / 状态）
├── skill.json                # skill 元信息 manifest
├── SKILL.md                  # skill 调用契约
├── CLAUDE.md                 # Claude Code 协作说明
├── README.md                 # 仓库级简述
├── .processed_emails.json    # 邮件处理状态（运行后生成）
└── .processed_events.json    # 日历事件状态（运行后生成）
```

## 边界

当前实现仍然不包含：

- 自动填充或托管敏感凭证
- 自动完成 `lark-cli` 登录
- AI 语义理解级时间解析
- 完整的 onboarding 教学流程
