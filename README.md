# RICOH3504ex_MCP

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-orange)](https://modelcontextprotocol.io/)

基于fastmcp的RICOH MP C3504ex打印机地址簿管理MCP服务器。支持多台打印机动态配置，客户端调用时指定打印机IP和账户信息。

## 功能特性

- 支持多台RICOH MP C3504ex打印机管理
- 用户登录认证与会话管理
- 添加用户到打印机地址簿
- 删除用户（支持索引和用户名）
- 查询用户信息
- 获取用户列表
- 客户端动态指定打印机配置
- 支持Python 3.8+

## 系统要求

- Python 3.8 或更高版本
- uvx（可选，用于快速运行）
- git（用于克隆仓库）

## 安装

### 方式1：使用uvx运行（推荐）

```bash
uvx --from git+https://github.com/wanli523/RICOH3504ex_MCP.git main.py
```

### 方式2：克隆仓库后运行

```bash
git clone https://github.com/wanli523/RICOH3504ex_MCP.git
cd RICOH3504ex_MCP
pip install -r requirements.txt
python main.py
```

### 方式3：使用pip安装

```bash
pip install git+https://github.com/wanli523/RICOH3504ex_MCP.git
ricoh3504ex-mcp
```

## 使用方式

### 客户端调用时指定打印机信息

MCP服务器由客户端调用时动态指定打印机IP和账户密码，无需在服务端配置。

**登录打印机：**
```python
# 登录一楼打印机
login_printer(ip="192.168.232.254", username="admin", password="")

# 登录二楼打印机
login_printer(ip="192.168.1.100", username="admin", password="password123")

# 登录三楼打印机
login_printer(ip="192.168.2.100", username="admin", password="password456")
```

**后续操作：**
```python
# 获取用户列表（使用已登录的打印机）
get_all_users()

# 添加用户
add_user(username="张三", email="zhangsan@example.com")

# 查找用户
find_user_by_name(usernames="张三")

# 删除用户（按索引）
delete_user(user_indices="00001")

# 删除用户（按名称）
delete_user_by_name(usernames="张三")
```

**切换打印机：**
```python
# 切换到另一台打印机
login_printer(ip="192.168.1.100", username="admin", password="password123")

# 现在所有操作都针对新登录的打印机
get_all_users()
```

## 1Panel部署

### 方式1：使用uvx从GitHub安装（推荐）

在1Panel的MCP管理页面中，使用以下配置：

```json
{
  "mcpServers": {
    "RICOH3504ex_MCP": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/wanli523/RICOH3504ex_MCP.git",
        "main"
      ]
    }
  }
}
```

**说明**：
- `--from git+https://github.com/wanli523/RICOH3504ex_MCP.git`：指定从GitHub仓库安装
- `main`：指定运行main模块的main函数
- uvx会自动处理依赖安装和虚拟环境管理

### 方式2：克隆仓库后运行

#### 1. 克隆仓库

```bash
cd /opt/1panel/mcp
git clone https://github.com/wanli523/RICOH3504ex_MCP.git
```

#### 2. 安装依赖

```bash
cd RICOH3504ex_MCP
pip install -r requirements.txt
```

#### 3. 配置MCP服务器

在1Panel的MCP管理页面中，使用以下配置：

```json
{
  "mcpServers": {
    "RICOH3504ex_MCP": {
      "command": "python",
      "args": [
        "/opt/1panel/mcp/RICOH3504ex_MCP/main.py"
      ]
    }
  }
}
```

#### 4. 重启服务

在1Panel的MCP管理页面重启服务。

### 方式3：使用uvx运行本地目录

#### 1. 克隆仓库

```bash
cd /opt/1panel/mcp
git clone https://github.com/wanli523/RICOH3504ex_MCP.git
```

#### 2. 配置MCP服务器

在1Panel的MCP管理页面中，使用以下配置：

```json
{
  "mcpServers": {
    "RICOH3504ex_MCP": {
      "command": "uvx",
      "args": [
        "--directory",
        "/opt/1panel/mcp/RICOH3504ex_MCP",
        "main.py"
      ]
    }
  }
}
```

#### 3. 重启服务

在1Panel的MCP管理页面重启服务。

## MCP工具

### login_printer
登录打印机并获取会话。
- `ip`: 打印机IP地址（必需）
- `username`: 登录用户名（必需）
- `password`: 登录密码（必需）

### get_all_users
获取打印机地址簿中的所有用户。

### find_user_by_name
根据用户名查找用户。
- `usernames`: 用户名或用户名列表

### add_user
添加用户到打印机地址簿。
- `username`: 用户名（必需）
- `email`: 邮箱（必需）
- `user_index`: 用户编号（可选，自动获取）

### delete_user
根据用户索引删除用户。
- `user_indices`: 用户索引或索引列表

### delete_user_by_name
根据用户名删除用户。
- `usernames`: 用户名或用户名列表

## 使用示例

### 示例1：管理一楼打印机

```python
# 登录一楼打印机
login_printer(ip="192.168.232.254", username="admin", password="")

# 获取用户列表
users = get_all_users()

# 添加用户
add_user(username="李四", email="lisi@example.com")

# 删除用户
delete_user_by_name(usernames="李四")
```

### 示例2：管理多台打印机

```python
# 管理一楼打印机
login_printer(ip="192.168.232.254", username="admin", password="")
add_user(username="张三", email="zhangsan1@example.com")

# 切换到二楼打印机
login_printer(ip="192.168.1.100", username="admin", password="password123")
add_user(username="李四", email="lisi2@example.com")

# 切换到三楼打印机
login_printer(ip="192.168.2.100", username="admin", password="password456")
get_all_users()
```

## 依赖项

- fastmcp >= 0.1.0
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- urllib3 >= 2.0.0

## 常见问题

### 问题1：uvx: not found

**错误**：`/bin/sh: uvx: not found`

**解决**：使用Python直接运行，或安装uvx

```bash
pip install uvx
```

### 问题2：No such file or directory

**错误**：`No such file or directory`

**解决**：确保目录和文件已正确上传

```bash
mkdir -p /opt/1panel/mcp/RICOH3504ex_MCP
ls -la /opt/1panel/mcp/RICOH3504ex_MCP/
```

### 问题3：Python版本过低

**错误**：需要Python 3.8或更高版本

**解决**：升级Python版本

```bash
python --version
```

### 问题4：GitHub仓库访问失败

**错误**：无法从GitHub拉取代码

**解决**：
1. 检查网络连接
2. 确认GitHub仓库地址正确
3. 检查防火墙设置
4. 使用代理或镜像源

### 问题5：依赖安装失败

**错误**：依赖包安装失败

**解决**：
1. 升级pip：`pip install --upgrade pip`
2. 使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 技术栈

- fastmcp: MCP服务器框架
- requests: HTTP客户端
- beautifulsoup4: HTML解析
- urllib3: HTTP库

## 兼容性

- Python 3.8+
- RICOH MP C3504ex 打印机
- MCP (Model Context Protocol)

## 作者

wanli523 - [GitHub](https://github.com/wanli523)

## 致谢

感谢所有为本项目做出贡献的开发者。
