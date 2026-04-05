# qqmail-feishu-calendar

<p align="center">
  <img src="./assets/banner.svg" alt="qqmail-feishu-calendar" width="100%">
</p>

<p align="center">
  <strong>Never miss an interview again.</strong><br>
  <sub>将 QQ 邮箱中的面试通知自动同步到飞书日历，AI 智能判断时间</sub>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#快速上手">快速上手</a> •
  <a href="#安装">安装</a> •
  <a href="#配置">配置</a> •
  <a href="#工作原理">工作原理</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-0f172a?style=flat-square" alt="OpenClaw Skill">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Platform-Linux%2FmacOS-000000?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square" alt="MIT License">
</p>

---

## 痛点

找工作时，面试通知邮件堆积如山：
- 邮件太多，真正的面试邀请被淹没
- 收到面试时间后还要手动去日历创建日程
- 截止时间 ≠ 面试时间，Regex 容易误判
- 手动创建容易忘记或搞错时间

**结果：错过面试。**

---

## 解决方案

**qqmail-feishu-calendar** 自动完成全流程：

```
📧 QQ 邮件收到面试通知
      ↓
🤖 AI 判断邮件中的时间（区分面试时间与截止时间）
      ↓
📅 自动写入飞书日历
      ↓
🔔 面试前收到飞书提醒
```

无需手动处理，不依赖脆弱的正则匹配，任何格式的邮件都能理解。

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

## 快速上手

```bash
# 1. 克隆项目
git clone https://github.com/QuarterNomad/qqmail-feishu-calendar.git
cd qqmail-feishu-calendar

# 2. 填写凭证
cp config.env.example config.env
# 编辑 config.env，填入 QQ 邮箱 IMAP 授权码

# 3. 飞书授权
lark-cli auth login

# 4. 手动测试运行
python3 calendar_sync.py

# 5. 创建定时任务（可选，每6小时自动同步）
# 在 OpenClaw 中创建 cron job
```

---

## 安装

### 前置条件

- Python 3.8+
- [`lark-cli`](https://github.com) 已安装并完成用户授权
- QQ 邮箱开启 IMAP 服务
- 飞书自建应用（用于日历读写）

### 步骤 1：QQ 邮箱开启 IMAP

1. 打开 [mail.qq.com](https://mail.qq.com) 并登录
2. 设置 → 账户 → **IMAP/SMTP 服务** → 开启
3. 按提示用手机发送短信验证，获得**授权码**（形如 `xxxx xxxx xxxx`）

### 步骤 2：飞书应用配置

1. 打开 [open.feishu.cn/app](https://open.feishu.cn/app) 创建自建应用
2. 开通权限：`calendar:calendar`（日历读写）
3. 复制 `App ID`（`cli_xxx` 格式）和 `App Secret`

### 步骤 3：用户授权

```bash
lark-cli auth login
```

按提示在浏览器完成飞书账号授权。

### 步骤 4：填写配置

```bash
cp config.env.example config.env
```

编辑 `config.env`：

```env
QQMAIL_USER=your_email@qq.com
QQMAIL_AUTH_CODE=your_imap_auth_code
FEISHU_APP_ID=cli_your_app_id
FEISHU_APP_SECRET=your_app_secret
```

---

## 配置

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `QQMAIL_USER` | ✅ | QQ 邮箱地址 |
| `QQMAIL_AUTH_CODE` | ✅ | QQ 邮箱 IMAP 授权码 |
| `FEISHU_APP_ID` | ❌ | 飞书应用 ID（`lark-cli auth login` 已处理则不需） |
| `FEISHU_APP_SECRET` | ❌ | 飞书应用密钥 |

### 定时任务

创建 OpenClaw cron job（每 6 小时）：

```bash
openclaw tasks add \
  --name "QQ邮箱面试通知→飞书日历" \
  --cron "0 */6 * * *" \
  --timezone "Asia/Shanghai" \
  --message "python3 /path/to/calendar_sync.py"
```

---

## 工作原理

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Python 脚本         │ ──▶ │  OpenClaw AI Agent │ ──▶ │  飞书日历           │
│  扫描 QQ 邮箱        │     │  AI 判断时间        │     │  写入日程事件       │
│  (IMAP, 关键词过滤)  │     │  区分面试/截止时间  │     │  + 邮件直达链接     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
         ↑                                                                    │
         │  cron job（每 6 小时）                                              │
         └────────────────────────────────────────────────────────────────────┘
```

### 为什么用 AI 而不是正则？

| 正则匹配 | AI 判断 |
|----------|---------|
| 遇到新格式就失效 | 理解任意格式的邮件 |
| 无法区分截止时间与面试时间 | 真正理解语义 |
| 每个公司需要单独规则 | 通用所有发件方 |
| 需要人工维护 | 零维护 |

---

## 使用

### 手动运行

```bash
python3 calendar_sync.py
```

输出示例：

```
[2026-04-05 12:00:00] 扫描 QQ 邮箱...
  找到 3 封候选邮件

  === 新邮件 2 封 ===

  [2026-04-05] 【字节跳动】面试通知
  From: recruiting@bytedance.com
  QQ邮件链接: https://mail.qq.com/cgi-bin/readmail?mailid=415
  正文: 占志凡同学，您好！欢迎参加...
```

### 查看日历

```bash
lark-cli calendar +agenda
```

---

## 项目结构

```
qqmail-feishu-calendar/
├── calendar_sync.py      # 主脚本（扫描 + AI 解析）
├── config.env.example    # 凭证配置模板
├── SKILL.md             # OpenClaw Skill 定义
├── README.md            # 本文件
└── assets/
    └── banner.svg       # 项目 Banner
```

---

## 常见问题

**Q: 提示"凭证未配置"？**  
A: 检查 `config.env` 是否存在且 `QQMAIL_USER` 和 `QQMAIL_AUTH_CODE` 已填写。

**Q: 飞书日历出现重复事件？**  
A: 脚本会通过 AI 查重，但如果同一事件被重复创建，手动删除多余日程即可。

**Q: 如何修改扫描频率？**  
A: 编辑 cron 表达式 `"0 */6 * * *"`，如每小时一次：`"0 * * * *"`。

**Q: 支持除 QQ 邮箱以外的其他邮箱吗？**  
A: 目前仅支持 QQ 邮箱。理论上可扩展，欢迎 PR。

---

## License

[MIT License](./LICENSE)

---

<p align="center">
  Made with ❤️ for job seekers
</p>
