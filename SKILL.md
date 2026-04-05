# qqmail-feishu-calendar

将 QQ 邮箱中的面试通知邮件自动同步到飞书日历，支持 AI 智能判断时间（区分面试时间与截止时间）。

## 功能

- 🔍 自动扫描 QQ 邮箱近 3 天内的面试通知/邀约/安排邮件
- 🤖 AI 判断邮件中的时间，区分"面试时间"与"截止时间"
- 📅 写入飞书日历，附 QQ 邮件原始链接
- ⏰ 每 6 小时自动运行（可通过 cron 调整）
- 🔄 智能查重，同一公司同一时间不重复创建

## 安装

```bash
skillhub install qqmail-feishu-calendar
```

## 配置

### 1. QQ 邮箱开启 IMAP

1. 打开 [mail.qq.com](https://mail.qq.com) 并登录
2. 设置 → 账户 → 向下滚动到 **IMAP/SMTP 服务**
3. 开启 IMAP/SMTP 服务，按提示用手机发送短信验证
4. 获得 **授权码**（形如 `xxxx xxxx xxxx xxxx`），妥善保存

### 2. 飞书应用凭证

如果你已有飞书应用的 `App ID` 和 `App Secret`，跳过此步骤。

1. 打开 [open.feishu.cn/app](https://open.feishu.cn/app) 创建自建应用
2. 复制 `App ID`（`cli_xxx` 格式）和 `App Secret`
3. 开通权限：日历读写相关权限（`calendar:calendar` 系列）

### 3. 填写凭证

安装后编辑技能目录下的配置文件：

```bash
nano ~/.openclaw/workspace/skills/qqmail-feishu-calendar/config.env
```

写入以下内容（替换对应值）：

```env
QQMAIL_USER=your_email@qq.com
QQMAIL_AUTH_CODE=your_imap_auth_code
FEISHU_APP_ID=cli_xxxxxxxxxxxxxx
FEISHU_APP_SECRET=your_app_secret
```

### 4. 用户授权（飞书）

必须完成用户身份授权才能读写飞书日历：

```bash
lark-cli auth login
```

按提示在浏览器完成授权（需要你的飞书账号）。

### 5. 安装 Cron 定时任务

技能不会自动创建 cron job，需要手动创建或让它自动安装：

```bash
# 查看是否已有定时任务
openclaw tasks list

# 手动创建定时任务（每6小时）
openclaw tasks add \
  --name "QQ邮箱面试通知→飞书日历" \
  --cron "0 */6 * * *" \
  --timezone "Asia/Shanghai" \
  --message "运行：python3 ~/.openclaw/workspace/skills/qqmail-feishu-calendar/calendar_sync.py"
```

## 使用

### 手动触发

```bash
python3 ~/.openclaw/workspace/skills/qqmail-feishu-calendar/calendar_sync.py
```

### 查看定时任务

```bash
openclaw tasks list
```

### 查看飞书日历事件

```bash
lark-cli calendar +agenda
```

## 常见问题

**Q: 提示"channel is required"无法推送通知？**  
A: 这是因为隔离 session 无法推送消息，不影响核心功能，日程仍会正常写入。

**Q: 飞书日历出现了重复事件？**  
A: 查重依赖 AI 判断，如果同一时间的事件仍被重复创建，请手动删除多余事件。

**Q: 如何修改扫描频率？**  
A: 编辑 cron 表达式 `"0 */6 * * *"`，如改为每 12 小时一次：`"0 */12 * * *"`。

**Q: 可以只扫描特定公司吗？**  
A: 可以修改脚本中的 `keywords` 列表，添加/删除关键词。

## 工作原理

1. Python 脚本连接 QQ 邮箱 IMAP，搜索近 3 天内的面试相关邮件
2. 提取邮件正文，通过 OpenClaw AI Agent 判断是否为真正的面试通知
3. AI 区分"面试时间"与"截止时间"，决定是否创建日历事件
4. 事件写入飞书日历，description 包含 QQ 邮件原始链接
5. 通过 `lark-cli` API 查重，确保同一事件不重复创建

## 技术细节

- 依赖：`lark-cli`（飞书）、Python 3 标准库
- 凭证存储：本地 `config.env` 文件（不提交到 Git）
- 日历查重：`lark-cli api POST /open-apis/calendar/v4/calendars/primary/events/search`
- 邮件链接格式：`https://mail.qq.com/cgi-bin/readmail?mailid={msg_id}`
