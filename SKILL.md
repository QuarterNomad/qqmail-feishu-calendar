# qqmail-feishu-calendar

将 QQ 邮箱中的面试通知邮件自动同步到飞书日历，支持 AI 智能判断时间（区分面试时间与截止时间）。

## 首次使用引导

当用户首次触发本 skill 时，AI 自动执行以下步骤，用户只需配合填写信息：

**引导流程（共 4 步）：**

| 步骤 | AI 执行 | 用户操作 |
|------|---------|---------|
| 1 | 检查 lark-cli，未安装则自动安装 | 无 |
| 2 | 引导用户提供 QQ 邮箱地址 | 提供邮箱 |
| 3 | 引导用户提供 IMAP 授权码（附获取链接） | 提供授权码，AI 验证连通性 |
| 4 | AI 自动运行 lark-cli 授权流程，生成授权链接 | 点击链接完成飞书授权 |

**用户触发方式：**
直接告诉 AI "帮我配置 qqmail-feishu-calendar" 或 "开始使用 qqmail-feishu-calendar"。

## 前置要求

### lark-cli（飞书 CLI）

AI 会自动检测并安装，用户无需手动操作。

### QQ 邮箱 IMAP 授权码获取

1. 打开 [mail.qq.com](https://mail.qq.com) 并登录
2. 点击右上角 **设置** → **账号与安全**
3. 点击 **安全设置**
4. 下拉到页面最底部，点击 **开启服务**
5. 按提示用手机发送短信验证
6. 验证通过后页面显示 **授权码**（形如 `xxxx xxxx xxxx`），复制给 AI

## 功能

- 🔍 自动扫描 QQ 邮箱近 3 天内的面试通知/邀约/安排邮件
- 🤖 AI 判断邮件中的时间，区分"面试时间"与"截止时间"
- 📅 写入飞书日历，附 QQ 邮件原始链接
- ⏰ 每 6 小时自动运行（可通过 cron 调整）
- 🔄 智能查重，同一公司同一时间不重复创建
- 🧙 **AI 全自动引导配置**，用户只需提供凭证

## 安装

```bash
git clone https://github.com/QuarterNomad/qqmail-feishu-calendar.git ~/.openclaw/workspace/skills/qqmail-feishu-calendar
```

## 快速开始

安装后告诉 AI "帮我配置 qqmail-feishu-calendar"，AI 自动完成全部配置流程。

## 创建定时任务

```bash
openclaw tasks add \
  --name "QQ邮箱面试通知→飞书日历" \
  --cron "0 */6 * * *" \
  --timezone "Asia/Shanghai" \
  --message "python3 ~/.openclaw/workspace/skills/qqmail-feishu-calendar/calendar_sync.py"
```

## 工作原理

```
用户首次触发
     ↓
AI 自动检测并安装 lark-cli（如未安装）
     ↓
用户提供 QQ 邮箱 + IMAP 授权码 → AI 验证连通性
     ↓
AI 运行 lark-cli 授权 → 生成链接 → 用户点击授权
     ↓ 配置完成
calendar_sync.py 主流程
  ① 连接 QQ 邮箱 IMAP，搜索面试邮件
  ② AI 判断是否为面试通知（区分截止时间）
  ③ 写入飞书日历，附 QQ 邮件直达链接
```

## 文件结构

```
qqmail-feishu-calendar/
├── calendar_sync.py        # 主脚本
├── setup_wizard.py         # 脚本式引导（非对话场景备用）
├── config_validator.py     # 配置验证（IMAP / 飞书授权）
├── config.env.example      # 凭证模板
└── SKILL.md               # 本文件
```

## 常见问题

**Q: 提示"IMAP 连接失败"？**  
A: 授权码可能已过期，请到 QQ 邮箱重新获取。

**Q: 飞书授权链接打不开？**  
A: 确保链接在浏览器中已登录对应飞书账号。

**Q: 如何修改扫描频率？**  
A: 编辑 cron 表达式 `"0 */6 * * *"`，如改为每小时一次：`"0 * * * *"`。
