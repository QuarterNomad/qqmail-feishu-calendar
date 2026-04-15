# qqmail-feishu-calendar

将 QQ 邮箱中的面试通知类邮件扫描出来，供后续人工处理或二次集成使用。

> 当前仓库里的实现以 **邮件扫描与配置校验** 为主，尚未真正创建飞书日历事件，也没有接入大模型做时间解析。

## 当前能力

- 扫描 QQ 邮箱近 12 小时内、主题包含以下关键词的邮件：
  - `面试通知`
  - `面试邀约`
  - `面试安排`
- 输出候选邮件的时间、发件人、QQ 邮件链接、正文摘要
- 使用 `.processed_emails.json` 按 **邮件标题** 记录已处理邮件，避免重复输出
- 提供 `setup_wizard.py` 进行交互式配置
- 提供 `config_validator.py` 进行配置完整性、QQ 邮箱 IMAP、飞书登录状态检查

## 当前不包含的能力

以下能力目前仍未在代码中实现：

- AI 判断邮件中的面试时间
- 区分面试时间与截止时间
- 自动创建飞书日历事件
- 基于“公司 + 时间”的事件级查重

如果后续要支持这些能力，需要继续扩展 `calendar_sync.py` 的解析与日历写入逻辑。

## 运行环境

- Python 3.8+
- macOS 或 Linux
- `lark-cli`（仅用于检查飞书登录状态）

安装 `lark-cli`：

```bash
npm install -g @larksuite/cli
```

## 配置

### 1. 获取 QQ 邮箱 IMAP 授权码

1. 打开 [mail.qq.com](https://mail.qq.com) 并登录
2. 点击右上角 **设置** → **账号与安全**
3. 点击 **安全设置**
4. 下拉到页面底部，开启 IMAP 服务
5. 按提示完成短信验证
6. 获取授权码（形如 `xxxx xxxx xxxx`）

### 2. 登录飞书（可选但脚本会检查状态）

```bash
lark-cli auth login
```

### 3. 写入配置文件

在项目根目录创建 `config.env`，内容如下：

```env
QQMAIL_USER=<你的QQ邮箱>
QQMAIL_AUTH_CODE=<IMAP授权码>
```

也可以从模板复制：

```bash
cp config.env.example config.env
```

### 4. 交互式配置（可选）

如果希望一步步引导填写并校验配置：

```bash
python3 setup_wizard.py
```

## 使用方式

### 手动运行扫描

```bash
python3 calendar_sync.py
```

运行后脚本会：

1. 检查 `config.env` 是否完整
2. 配置缺失时自动进入 `setup_wizard.py`
3. 连接 QQ 邮箱 IMAP
4. 搜索近 12 小时的候选邮件
5. 输出新邮件摘要并记录到 `.processed_emails.json`

### 定时运行示例

如果你希望定时扫描，可以自行用 cron 或其他任务系统包装，例如每 6 小时执行一次：

```bash
0 */6 * * * cd /path/to/qqmail-feishu-calendar && python3 calendar_sync.py
```

## 项目结构

```text
qqmail-feishu-calendar/
├── calendar_sync.py        # 主脚本：扫描候选邮件并输出结果
├── setup_wizard.py         # 交互式配置引导
├── config_validator.py     # 配置与连通性检查
├── config.env.example      # 配置模板
├── SKILL.md                # 面向 agent 的 skill 执行规范
├── README.md               # 面向人类用户的项目说明
└── .processed_emails.json  # 已处理邮件标题记录（运行后生成）
```

## 已知限制

- 目前只支持 QQ 邮箱 IMAP
- 关键词筛选依赖邮件主题，不会理解正文语义
- 已处理记录只按邮件标题去重，标题相同可能被视为同一封邮件
- 虽然会检查飞书登录状态，但当前脚本不会真正写入飞书日历

## License

[MIT License](./LICENSE)
