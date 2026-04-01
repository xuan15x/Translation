# Git 版本控制设置指南

**项目**: AI 智能翻译工作台  
**仓库地址**: https://github.com/xuan15x/Translation.git  
**当前状态**: ✅ 本地 Git 仓库已初始化并提交  
**待完成**: ⏳ 推送到 GitHub 远程仓库

---

## ✅ 已完成的操作

### 1. 初始化本地 Git 仓库

```bash
cd C:\Users\13457\PycharmProjects\translation
git init
```

✅ **状态**: 已完成

---

### 2. 配置 Git 用户信息

```bash
git config user.name "xuan15x"
git config user.email "xuan15x@users.noreply.github.com"
```

✅ **状态**: 已完成

---

### 3. 添加所有文件到暂存区

```bash
git add .
```

✅ **状态**: 已完成  
📊 **统计**: 132 个文件，42,883 行代码

---

### 4. 首次提交

```bash
git commit -m "Initial commit: AI 智能翻译工作台 v2.2.0"
```

✅ **状态**: 已完成  
📝 **提交哈希**: `9effb82`

---

### 5. 添加远程仓库

```bash
git remote add origin https://github.com/xuan15x/Translation.git
```

✅ **状态**: 已完成

---

### 6. 重命名分支为 main

```bash
git branch -M main
```

✅ **状态**: 已完成

---

## ⏳ 待完成的操作

### 推送到 GitHub

由于网络连接问题，推送命令执行超时。请按以下步骤手动完成：

#### 方式 1: 使用 HTTPS 推送（推荐）

```bash
cd C:\Users\13457\PycharmProjects\translation
git push -u origin main
```

**操作步骤**:
1. 打开 PowerShell 或命令行终端
2. 切换到项目目录：`cd C:\Users\13457\PycharmProjects\translation`
3. 执行推送命令：`git push -u origin main`
4. 当提示输入用户名和密码时：
   - **Username**: 输入你的 GitHub 用户名
   - **Password**: 输入你的 GitHub Personal Access Token（不是登录密码）

**获取 Personal Access Token**:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：勾选 `repo` (Full control of private repositories)
4. 生成后复制 Token（只显示一次，请妥善保存）
5. 使用此 Token 作为密码

---

#### 方式 2: 使用 SSH 推送（更安全）

**步骤 1: 生成 SSH 密钥**

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

按回车接受默认路径，然后设置一个密码短语（可选）。

**步骤 2: 将公钥添加到 GitHub**

1. 复制公钥内容：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   （Windows: `type C:\Users\你的用户名\.ssh\id_ed25519.pub`）

2. 访问 https://github.com/settings/keys
3. 点击 "New SSH key"
4. 粘贴公钥内容，保存

**步骤 3: 更改远程仓库 URL 为 SSH**

```bash
git remote set-url origin git@github.com:xuan15x/Translation.git
```

**步骤 4: 推送**

```bash
git push -u origin main
```

---

## 📋 验证推送成功

推送成功后，访问以下链接验证：

- 🔗 https://github.com/xuan15x/Translation

应该能看到：
- ✅ 所有 132 个文件已上传
- ✅ 提交历史包含 "Initial commit: AI 智能翻译工作台 v2.2.0"
- ✅ 主要分支显示为 `main`

---

## 🔧 常见问题解决

### 问题 1: 推送超时

**症状**:
```
fatal: unable to access 'https://github.com/...': Failed to connect to github.com port 443 after xxx ms: Timed out
```

**解决方案**:

**方案 A**: 使用代理（如果有）
```bash
# 设置 HTTP 代理
git config --global http.proxy http://proxy.example.com:8080

# 设置 HTTPS 代理
git config --global https.proxy https://proxy.example.com:8080

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

**方案 B**: 修改 DNS
```
1. 打开网络设置
2. 修改 DNS 为 8.8.8.8 或 1.1.1.1
3. 刷新 DNS: ipconfig /flushdns
4. 重试推送
```

**方案 C**: 使用 SSH 代替 HTTPS
```bash
git remote set-url origin git@github.com:xuan15x/Translation.git
git push -u origin main
```

---

### 问题 2: 认证失败

**症状**:
```
remote: Support for password authentication was removed on August 13, 2021.
remote: Please see https://docs.github.com/en/get-started/getting-started-with-git/managing-remote-repositories#changing-a-remote-repository-url for more information.
fatal: Authentication failed
```

**解决方案**:

必须使用 Personal Access Token 而不是密码：

1. 访问 https://github.com/settings/tokens
2. 生成新 Token（选择 `repo` 权限）
3. 复制 Token
4. 推送时粘贴 Token 作为密码

或者使用 SSH 方式（见上方）。

---

### 问题 3: 远程仓库已存在内容

**症状**:
```
! [rejected]        main -> main (fetch first)
error: failed to push some refs to '...'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally.
```

**解决方案**:

如果远程仓库是空的，只是创建时自动生成的 README：

```bash
# 强制推送（谨慎使用，会覆盖远程内容）
git push -f origin main

# 或者先拉取再合并
git pull origin main --allow-unrelated-histories
git push -u origin main
```

---

## 📊 当前仓库状态

查看当前 Git 状态：

```bash
# 查看提交历史
git log --oneline

# 查看远程仓库
git remote -v

# 查看分支
git branch -a

# 查看状态
git status
```

**预期输出**:
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

---

## 🎯 后续 Git 工作流

### 日常开发流程

1. **开始工作前**
   ```bash
   git pull origin main
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/new-feature
   ```

3. **开发和提交**
   ```bash
   # 修改文件...
   git add .
   git commit -m "feat: 添加新功能"
   ```

4. **推送分支**
   ```bash
   git push origin feature/new-feature
   ```

5. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 等待审查和合并

---

### 约定式提交规范

使用规范的提交信息格式：

```
<类型>(<范围>): <主题>

[可选的主体]

[可选的脚注]
```

**类型说明**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具/配置
- `BREAKING CHANGE`: 破坏性变更

**示例**:
```
docs(config): 更新 API 密钥配置方式至 v2.2.0

- 取消环境变量读取 API 密钥
- 新增配置文件和 GUI 界面配置方式
- 更新相关文档 5 篇

BREAKING CHANGE: 不再支持通过环境变量配置 API 密钥
```

---

## 📝 检查清单

在推送前确认：

- [ ] `.gitignore` 已正确配置
- [ ] 不包含敏感信息（API 密钥、密码等）
- [ ] 不包含大文件（>100MB）
- [ ] 提交信息清晰规范
- [ ] 代码已通过测试
- [ ] 文档已同步更新

---

## 🔗 相关资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 文档](https://docs.github.com/)
- [约定式提交规范](https://www.conventionalcommits.org/zh-hans/)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [Personal Access Token 使用指南](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

---

**最后更新**: 2026-04-01  
**文档版本**: v2.2.0  
**维护者**: xuan15x
