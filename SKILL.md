# qqmail-feishu-calendar

将 QQ 邮箱中的面试通知邮件同步到飞书日历，支持 AI 智能判断时间（区分面试时间与截止时间）。

## 能力

- 扫描 QQ 邮箱近 12 小时的面试通知/邀约/安排邮件
- AI 判断邮件中的时间，区分"面试时间"与"截止时间"
- 写入飞书日历，附 QQ 邮件原始链接
- 智能查重，同一公司同一时间不重复创建

## 触发方式

用户说"帮我同步面试通知"、"QQ 邮箱面试通知同步"或类似话语时调用本 skill。

## 前置要求

### 1. lark-cli（飞书 CLI）

未安装时执行：`npm install -g @larksuite/cli`

### 2. config.env 配置

必须包含以下字段：

```
QQMAIL_USER=<QQ邮箱地址>
QQMAIL_AUTH_CODE=<IMAP授权码>
```

### 3. 飞书授权

执行 `lark-cli auth login` 完成授权，`lark-cli auth status` 应显示已登录。

## 配置验证

执行同步前，agent 应验证配置完整性：

1. 读取 `config.env` 检查 `QQMAIL_USER` 和 `QQMAIL_AUTH_CODE` 已填写
2. 运行 `lark-cli auth status` 确认飞书已登录

## 文件结构

```
qqmail-feishu-calendar/
├── calendar_sync.py    # 主脚本
├── setup_wizard.py     # 人类用户交互式配置工具（可选）
├── config_validator.py # 配置验证
└── config.env.example  # 凭证模板
```
