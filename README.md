# qqmail-feishu-calendar

<p align="center">
  <strong>Never miss an interview again.</strong><br>
  <sub>将 QQ 邮箱中的面试通知自动同步到飞书日历，AI 智能判断时间</sub>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#安装">安装</a> •
  <a href="#配置指南">配置指南</a> •
  <a href="#定时任务">定时任务</a> •
  <a href="#工作原理">工作原理</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-0f172a?style=flat-square" alt="OpenClaw Skill">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Platform-Linux%2FmacOS-000000?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square" alt="MIT License">
</p>

---

## 功能特性

|     | 功能 | 说明 |
|:---:|------|------|
| 🤖 | **AI 判断时间** | 智能区分"面试时间"与"截止时间"，不误判 |
| 🔍 | **多关键词扫描** | 覆盖面试通知、邀约、安排等多类邮件 |
| ⏰ | **定时同步** | 每 6 小时自动运行（可自定义频率） |
| 🔄 | **智能查重** | 同一公司同一时间不重复创建 |
| 🔗 | **邮件直达** | 日历事件中直接附加 QQ 邮件原始链接 |
| 🌐 | **跨平台** | Linux / macOS 均可运行 |

---

## 安装

### 前置条件

- Python 3.8+

### 步骤

**第 1 步：克隆项目**

```bash
git clone https://github.com/QuarterNomad/qqmail-feishu-calendar.git ~/.openclaw/workspace/skills/qqmail-feishu-calendar
```

**第 2 步：安装 lark-cli**

```bash
npm install -g @larksuite/cli
```

**第 3 步：配置凭证**

详见[配置指南](#配置指南)。

**第 4 步：验证安装**

```bash
python3 ~/.openclaw/workspace/skills/qqmail-feishu-calendar/calendar_sync.py
```

---

## 配置指南

### QQ 邮箱 IMAP 授权码

1. 打开 [mail.qq.com](https://mail.qq.com) 并登录
2. 点击右上角 **设置** → **账号与安全**
3. 点击 **安全设置**
4. 下拉到页面最底部，点击 **开启服务**
5. 按提示用手机发送短信验证
6. 验证通过后页面显示 **授权码**（形如 `xxxx xxxx xxxx`）

### 飞书授权

```bash
lark-cli config init --new
lark-cli auth login --domain calendar --recommend
```

### 写入配置

将凭证写入 `config.env`：

```
QQMAIL_USER=<你的QQ邮箱>
QQMAIL_AUTH_CODE=<IMAP授权码>
```

### 交互式配置（可选）

如需交互式引导，可在终端运行：

```bash
python3 ~/.openclaw/workspace/skills/qqmail-feishu-calendar/setup_wizard.py
```

---

## 定时任务

创建 OpenClaw cron job（每 6 小时）：

```bash
openclaw tasks add \
  --name "QQ邮箱面试通知→飞书日历" \
  --cron "0 */6 * * *" \
  --timezone "Asia/Shanghai" \
  --message "python3 ~/.openclaw/workspace/skills/qqmail-feishu-calendar/calendar_sync.py"
```

---

## 工作原理

```
calendar_sync.py 扫描 QQ 邮箱（IMAP）
     ↓
AI 判断是否为面试通知（区分面试时间与截止时间）
     ↓
写入飞书日历，附 QQ 邮件直达链接
```

### 为什么用 AI 而不是正则？

| 正则匹配 | AI 判断 |
|----------|---------|
| 遇到新格式就失效 | 理解任意格式的邮件 |
| 无法区分截止时间与面试时间 | 真正理解语义 |
| 每个公司需要单独规则 | 通用所有发件方 |
| 需要人工维护 | 零维护 |

---

## 项目结构

```
qqmail-feishu-calendar/
├── calendar_sync.py        # 主脚本（扫描 + AI 解析）
├── setup_wizard.py         # 交互式配置引导
├── config_validator.py     # 配置验证
├── config.env.example      # 凭证模板
├── SKILL.md               # OpenClaw Skill 定义
└── README.md              # 本文件
```

---

## 常见问题

**Q: AI 提示"IMAP 连接失败"？**  
A: 授权码可能已过期，请到 QQ 邮箱重新获取新的授权码。

**Q: 飞书授权链接打不开？**  
A: 确保在浏览器中已登录对应飞书账号。

**Q: 如何修改扫描频率？**  
A: 编辑 cron 表达式 `"0 */6 * * *"`，如改为每小时一次：`"0 * * * *"`。

**Q: 支持除 QQ 邮箱以外的其他邮箱吗？**  
A: 目前仅支持 QQ 邮箱。理论上可扩展，欢迎 PR。

---

## License

[MIT License](./LICENSE)

---

<p align="center">
  Made with ❤️ for job seekers
</p>
