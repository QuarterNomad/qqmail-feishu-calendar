# qqmail-lark-calendar

这是一个只保留 standalone skill/runtime 的仓库。

它负责：
- 扫描 QQ 邮箱中的面试通知类邮件
- 提取最低配面试信息
- 通过 `lark-cli` 创建或更新 Lark 日历事件
- 持久化本地状态以支持重复运行

这个仓库**不再包含**交互式配置引导、安装教学或 onboarding 资产。运行所需的配置文件、环境变量、认证状态与调度方式，应由外部宿主系统提供。

## 保留内容

- `calendar_sync.py`：runtime 入口脚本
- `qqmail_lark_calendar/`：核心逻辑包
- `SKILL.md`：面向 agent 的 skill 契约

## 运行时约束

运行该 skill 前，外部环境需要自行提供：

- Python 3.8+
- `lark-cli`
- QQ 邮箱 IMAP 可用凭证
- Lark 登录状态
- 完整配置：
  - `QQMAIL_USER`
  - `QQMAIL_AUTH_CODE`
  - `LARK_CALENDAR_ID`

## 入口命令

```bash
python3 calendar_sync.py --hours 12
```

## 项目结构

```text
qqmail-lark-calendar/
├── calendar_sync.py          # 入口脚本：参数解析 + 调度
├── qqmail_lark_calendar/     # 核心逻辑包（配置 / IMAP / 解析 / Lark / 状态）
├── SKILL.md                  # skill 执行契约
├── README.md                 # 仓库级简述
├── .processed_emails.json    # 邮件处理状态（运行后生成）
└── .processed_events.json    # 日历事件状态（运行后生成）
```

## 边界

当前实现仍然不包含：

- 交互式初始化
- 配置引导
- AI 语义理解级时间解析
- 完整的 onboarding 文档
