# 沙龙之家 示例项目（中文说明）

这是一个简单的 Django 上门美发预约示例项目，包含：

- 客户注册与登录
- 客户预约表单
- 员工管理面板（增删改查）
- 超级管理员可通过 Django 后台管理全部数据

## 项目路径


品牌：沙龙之家（项目展示用名）

- 应用逻辑： [core](./core)
- 模板： [templates](./templates)
- 设置文件： [config/settings.py](./config/settings.py)

## 快速启动

在项目根目录运行以下命令：

```powershell
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py seed_data
venv\Scripts\python.exe manage.py createsuperuser
venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

## 创建员工用户（可选）

如果希望创建一个可以访问管理面板的普通员工账号：

```powershell
venv\Scripts\python.exe manage.py createsuperuser
```

或者在 Django 后台创建普通用户并设置：

- `is_staff = True`（允许访问管理面板）
- `is_superuser = True`（仅为超级管理员使用）

## 常用链接

启动服务后在浏览器打开：

- 主页: `http://127.0.0.1:8000/`
- 客户注册: `http://127.0.0.1:8000/register/`
- 登录: `http://127.0.0.1:8000/login/`
- 客户预约页: `http://127.0.0.1:8000/bookings/`
- 员工管理面板: `http://127.0.0.1:8000/dashboard/`
- Django 后台管理: `http://127.0.0.1:8000/admin/`

## 用户权限说明

- 客户：
  - 从 `/register/` 注册
  - 从 `/login/` 登录
  - 只能查看自己的预约

- 员工用户：
  - 从 `/login/` 登录
  - 进入 `/dashboard/` 管理服务、发型师与预约

- 超级管理员：
  - 从 `/admin/` 登录
  - 在 Django 后台管理所有数据

## 初始化数据（Seed Data）

下面命令会在数据库中添加示例记录（如果尚未存在）：

```powershell
venv\Scripts\python.exe manage.py seed_data
```

示例数据包括：

- 3 个服务项目
- 3 位发型师

## M-Pesa 付款设置（Daraja）

“Pay now”会打开付款窗口，要求输入肯尼亚手机号码，并通过 Safaricom Daraja STK Push 向手机发送 PIN 确认提示。订单只有收到成功的 Daraja 回调后才会标记为已付款。网站不会收集 M-Pesa PIN 或银行卡资料。

要启用真实提示，请在环境中设置 Daraja 应用凭据：

在项目目录的 `.env` 文件中填写以下项目（本地 `.env` 已准备好，且不会提交到 Git）：

- `MPESA_ENVIRONMENT=sandbox`（上线后改为 `production`）
- `MPESA_CONSUMER_KEY`：Daraja 应用的 Consumer Key
- `MPESA_CONSUMER_SECRET`：Daraja 应用的 Consumer Secret
- `MPESA_SHORTCODE`：Daraja 支持的商户短代码
- `MPESA_PASSKEY`：对应短代码的 STK Push Passkey
- `MPESA_CALLBACK_URL`：公网可访问的 HTTPS 地址，路径为 `/payments/mpesa/callback/`

可参考 `.env.example`。在 Safaricom Daraja 门户创建/选择应用后，从 Daraja 提供的应用凭据和测试/生产配置复制对应值。不要把 Consumer Secret 或 Passkey 发到聊天、提交到 Git，或放进网页表单；修改 `.env` 后重启 Django 服务。

然后运行数据库迁移：

```powershell
venv\Scripts\python.exe manage.py migrate
```

本地地址 `127.0.0.1` 不能接收 Safaricom 的回调；请使用可公开访问的 HTTPS 回调地址，并将其填入 `MPESA_CALLBACK_URL` 及 Daraja 配置。当前只实现 M-Pesa STK Push；银行卡支付需要另行接入支付服务商，切勿在本网站直接收集卡号或 CVV。

## 备注

- 服务项目和发型师信息来自数据库动态加载。
- 客户提交预约后由管理员分配发型师。
- 本项目为教学示例，删除操作为真实删除。
