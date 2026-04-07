# qqmail-feishu-calendar

将 QQ 邮箱中的面试通知邮件自动同步到飞书日历，支持 AI 智能判断时间（区分面试时间与截止时间）。

## 首次使用引导

当用户首次触发本 skill 时，检测到 `config.env` 不完整，会自动运行引导配置流程：

```
python3 ~/.openclaw/workspace/skills/qqmail-feishu-calendar/setup_wizard.py
```

**引导流程（共 3 步，逐步验证连通性）：**

| 步骤 | 内容 | 验证方式 |
|------|------|---------|
| 1 | 填写 QQ 邮箱地址 | 写入 config.env |
| 2 | 填写 IMAP 授权码 | IMAP NOOP 连接测试 |
| 3 | 检查飞书授权状态 | lark-cli auth status |

**用户触发方式：**
- 直接说"配置"、"开始使用"、"setup"
- 或直接运行 `python3 calendar_sync.py`（检测到未配置会自动进入引导）

## 功能

- 🔍 自动扫描 QQ 邮箱近 3 天内的面试通知/邀约/安排邮件
- 🤖 AI 判断邮件中的时间，区分"面试时间"与"截止时间"
- 📅 写入飞书日历，附 QQ 邮件原始链接
- ⏰ 每 6 小时自动运行（可通过 cron 调整）
- 🔄 智能查重，同一公司同一时间不重复创建
- 🧙 **首次运行自动引导配置**，逐步验证连通性

## 安装

```bash
skillhub install qqmail-feishu-calendar
```

## 快速开始

安装后直接运行，引导流程会自动启动：

```bash
python3 ~/.openclaw/workspace/skills/qqmail-feishu-calendar/calendar_sync.py
```

按提示逐步完成配置后即可使用。

## QQ 邮箱 IMAP 授权码获取

1. 打开 [mail.qq.com](https://mail.qq.com) 并登录
2. 设置 → 账户 → 向下滚动到 **IMAP/SMTP 服务**
3. 开启 IMAP/SMTP 服务，按提示用手机发送短信验证
4. 获得 **授权码**（形如 `xxxx xxxx xxxx xxxx`），妥善保存

## 飞书授权

```bash
lark-cli auth login
```

按提示在浏览器完成授权。

## 手动填写凭证（可选）

如不希望使用引导流程，可手动编辑配置文件：

```bash
nano ~/.openclaw/workspace/skills/qqmail-feishu-calendar/config.env
```

```env
QQMAIL_USER=your_email@qq.com
QQMAIL_AUTH_CODE=your_imap_auth_code
FEISHU_APP_ID=cli_xxxxxxxxxxxxxx
FEISHU_APP_SECRET=your_app_secret
```

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
检测 config.env → 不完整？
     ↓ 是
进入 setup_wizard.py 引导流程
  ① 填写 QQ 邮箱 → IMAP NOOP 验证
  ② 填写授权码 → IMAP 连接测试
  ③ 检查飞书 lark-cli 授权状态
     ↓ 否（已配置完整）
calendar_sync.py 主流程
  ① 连接 QQ 邮箱 IMAP，搜索面试邮件
  ② AI 判断是否为面试通知（区分截止时间）
  ③ 写入飞书日历，附 QQ 邮件直达链接
```

## 文件结构

```
qqmail-feishu-calendar/
├── calendar_sync.py        # 主脚本（含自动引导触发）
├── setup_wizard.py         # 引导配置流程
├── config_validator.py     # 配置验证（IMAP / 飞书授权）
├── config.env.example      # 凭证模板
└── SKILL.md               # 本文件
```

## 常见问题

**Q: 引导流程中途退出，想重新开始？**  
A: 删除 `config.env` 后重新运行 `calendar_sync.py` 即可。

**Q: 提示"IMAP 连接失败"？**  
A: 授权码可能已过期，请到 QQ 邮箱重新获取。

**Q: 飞书授权状态检查失败？**  
A: 请先运行 `lark-cli auth login` 完成授权。

**Q: 如何修改扫描频率？**  
A: 编辑 cron 表达式 `"0 */6 * * *"`，如改为每小时一次：`"0 * * * *"`。
