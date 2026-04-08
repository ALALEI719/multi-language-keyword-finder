# Cross-Language SEO Intent Tool

通过源语言关键词，自动翻译并查找目标市场中相同搜索意图的关键词及相关词，包含月搜索量、KD、搜索意图等数据。

## 用户系统与权限

- 游客：仅可免费查询 1 次，结果只显示前 5 条
- 注册用户：赠送 10 credits，可查看完整结果、解锁深度分析和 CSV 下载
- 有个人 Ahrefs API 的用户：可在侧边栏输入自己的 API Key，不消耗 credits
- 无个人 API 的用户：使用平台共享 API Key，每次查询消耗 1 credit

## 本地运行

```bash
# 1) 安装依赖
pip install -r requirements.txt

# 2) 设置环境变量（平台共享 API / 管理员密码）
export PLATFORM_AHREFS_KEY="your_ahrefs_api_key"
export ADMIN_PASSWORD="your_admin_password"

# 3) 启动主应用
streamlit run app.py
```

浏览器访问：`http://localhost:8501`

## 管理员后台（手动充值 credits）

```bash
export ADMIN_PASSWORD="your_admin_password"
streamlit run admin.py --server.port 8502
```

浏览器访问：`http://localhost:8502`

后台支持：
- 查看用户邮箱、credits、注册时间、是否绑定个人 API Key
- 为指定用户手动增加 credits

## 部署建议（生产）

推荐：Railway / Render / 自建 VPS（需要持久化磁盘保存 SQLite `data.db`）。

至少配置以下环境变量：

- `PLATFORM_AHREFS_KEY`：平台共享 Ahrefs API Key（无个人 API 的用户会用到）
- `ADMIN_PASSWORD`：管理员后台登录密码

启动命令：

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## 依赖与数据

- 数据库：SQLite（自动创建 `data.db`）
- 密码加密：`bcrypt`
- 翻译：`deep-translator`
