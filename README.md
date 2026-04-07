# qqmail-feishu-calendar

<p align="center">
  <strong>Never miss an interview again.</strong><br>
  <sub>将 QQ 邮箱中的面试通知自动同步到飞书日历，AI 智能判断时间</sub>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#快速上手">快速上手</a> •
  <a href="#安装">安装</a> •
  <a href="#配置引导">配置引导</a> •
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
| 🧙 | **AI 全自动引导** | 用户只需提供凭证，AI 自动完成所有配置 |
| 🌐 | **跨平台** | Linux / macOS 均可运行 |

---

## 快速上手

```bash
# 1. 克隆项目
git clone https://github.com/QuarterNomad/qqmail-feishu-calendar.git ~/.openclaw/workspace/skills/qqmail-feishu-calendar

# 2. 告诉 AI 帮你配置
# 直接对 AI 说："帮我配置 qqmail-feishu-calendar"
# AI 会自动引导你完成全部配置，你只需要提供 QQ 邮箱和授权码
```

---

## 安装

### 前置条件

- Python 3.8+

### 步骤 1：克隆项目

```bash
git clone https://github.com/QuarterNomad/qqmail-feishu-calendar.git ~/.openclaw/workspace/skills/qqmail-feishu-calendar
```

### 步骤 2：AI 引导配置

直接告诉 AI：

> 帮我配置 qqmail-feishu-calendar

AI 会自动完成：
1. 检测并安装 lark-cli（如未安装）
2. 引导你提供 QQ 邮箱 + IMAP 授权码
3. 自动运行飞书授权流程（你只需点击授权链接）
4. 验证全部连通性

---

## 配置引导

### QQ 邮箱 IMAP 授权码获取

1. 打开 [mail.qq.com](https://mail.qq.com) 并登录
2. 点击右上角 **设置** → **账号与安全**
3. 点击 **安全设置**
4. 下拉到页面最底部，点击 **开启服务**
5. 按提示用手机发送短信验证
6. 验证通过后页面显示 **授权码**（形如 `xxxx xxxx xxxx`），复制给 AI

### 飞书授权

AI 在引导过程中会自动生成授权链接，你只需点击完成授权。

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
用户首次触发
     ↓
AI 自动检测并安装 lark-cli（如未安装）
     ↓
用户提供 QQ 邮箱 + IMAP 授权码 → AI 验证连通性
     ↓
AI 运行飞书授权流程 → 生成链接 → 用户点击授权
     ↓ 配置完成

定时任务触发
     ↓
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
├── setup_wizard.py         # 脚本式引导（非对话场景备用）
├── config_validator.py     # 配置验证（IMAP / 飞书授权）
├── config.env.example      # 凭证模板
├── SKILL.md               # OpenClaw Skill 定义（AI 引导流程）
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
