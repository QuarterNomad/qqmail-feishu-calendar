# qqmail-feishu-calendar

将 QQ 邮箱中的面试通知邮件自动同步到飞书日历，支持 AI 智能判断时间（区分面试时间与截止时间）。

## 首次使用引导

当用户首次触发本 skill 时，直接在对话中引导用户填写配置，无需手动运行脚本。

**引导流程（共 4 步，全部在对话中完成）：**

| 步骤 | 内容 | 验证方式 |
|------|------|---------|
| 1 | 安装 lark-cli | 检查 lark-cli 是否可用 |
| 2 | 提供 QQ 邮箱地址 | AI 写入 config.env |
| 3 | 提供 IMAP 授权码 | AI 调用 IMAP NOOP 连接测试 |
| 4 | 飞书授权 | 调用 lark-cli auth login + 状态验证 |

**用户触发方式：**
直接告诉 AI "帮我配置 qqmail-feishu-calendar" 或 "开始使用 qqmail-feishu-calendar"。

## 前置要求

### 1. 安装 lark-cli（飞书 CLI 工具）

```bash
npm install -g @larksuite/cli
```

验证安装成功：
```bash
lark-cli --version
```

### 2. QQ 邮箱 IMAP 授权码获取

**详细步骤：**

1. 打开 [mail.qq.com](https://mail.qq.com) 并登录
2. 点击右上角 **设置** → **账号与安全**
3. 点击 **安全设置**
4. 下拉到页面最底部，点击 **开启服务**
5. 按提示用手机发送短信验证
6. 验证通过后，页面会显示 **授权码**（形如 `xxxx xxxx xxxx`），复制它

**注意：** 授权码不是 QQ 密码，是专用于 IMAP 访问的 16 位字母，只能通过以上步骤在网页获取。

### 3. 飞书授权

```bash
lark-cli auth login
```

按提示在浏览器完成授权。

## 功能

- 🔍 自动扫描 QQ 邮箱近 3 天内的面试通知/邀约/安排邮件
- 🤖 AI 判断邮件中的时间，区分"面试时间"与"截止时间"
- 📅 写入飞书日历，附 QQ 邮件原始链接
- ⏰ 每 6 小时自动运行（可通过 cron 调整）
- 🔄 智能查重，同一公司同一时间不重复创建
- 🧙 **对话式引导配置**，逐步验证连通性

## 安装

```bash
git clone https://github.com/QuarterNomad/qqmail-feishu-calendar.git ~/.openclaw/workspace/skills/qqmail-feishu-calendar
```

## 快速开始

安装后直接告诉 AI "帮我配置 qqmail-feishu-calendar"，按提示在对话中完成配置即可。

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
AI 在对话中引导填写配置
  ① 安装 lark-cli（如未安装）
  ② QQ 邮箱地址 → IMAP 验证
  ③ IMAP 授权码 → 连接测试
  ④ 飞书授权 → lark-cli auth login
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

**Q: 提示"lark-cli 未找到"？**  
A: 运行 `npm install -g @larksuite/cli` 安装。

**Q: 提示"IMAP 连接失败"？**  
A: 授权码可能已过期，请到 QQ 邮箱重新获取。

**Q: 飞书授权状态检查失败？**  
A: 请先运行 `lark-cli auth login` 完成授权。

**Q: 如何修改扫描频率？**  
A: 编辑 cron 表达式 `"0 */6 * * *"`，如改为每小时一次：`"0 * * * *"`。
