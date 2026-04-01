# Git 自动同步指南

## 📋 功能概述

本项目已配置自动同步机制，确保每次提交后都能及时推送到 GitHub 远程仓库。

**GitHub 仓库**: https://github.com/xuan15x/Translation

---

## 🚀 使用方法

### 方法一：使用同步脚本（推荐）

#### Windows CMD
```bash
sync_to_github.bat
```

#### PowerShell
```powershell
.\sync_to_github.ps1
```

#### 功能流程
脚本会自动执行以下 4 个步骤：
1. ✅ 检查本地状态
2. ✅ Fetch 远程更新
3. ✅ Pull 远程变更
4. ✅ Push 本地提交

---

### 方法二：手动命令

```bash
# 1. 查看状态
git status

# 2. 添加文件
git add -A

# 3. 提交更改
git commit -m "描述你的更改"

# 4. 拉取远程更新
git pull origin main --rebase

# 5. 推送到 GitHub
git push origin main
```

---

## 🔔 自动提醒功能

项目已安装 **Git post-commit hook**，每次提交后会自动：

- ✅ 检查本地与远程的同步状态
- ⚠️ 如果有未推送的提交，会提示你运行同步脚本
- 💡 如果远程有新提交，会提醒你先行拉取

**示例输出**：
```
========================================
  🔄 检查远程仓库同步状态...
========================================

📊 同步状态：
   本地领先远程：2 个提交
   本地落后远程：0 个提交

💡 建议：运行以下命令推送到远程仓库
   git push origin main

   或使用自动同步脚本:
   Windows: sync_to_github.bat
   Linux/Mac: ./sync_to_github.sh
========================================
```

---

## 📝 最佳实践

### ✅ 推荐做法
1. **每次提交后立即同步**
   - 使用 post-commit hook 的提醒
   - 运行 `sync_to_github.bat` 或 `.\sync_to_github.ps1`

2. **定期拉取远程更新**
   - 避免长期不同步导致合并冲突
   - 每天至少同步一次

3. **推送前检查**
   ```bash
   git status
   git fetch origin
   git log --oneline HEAD..origin/main  # 查看远程领先
   git log --oneline origin/main..HEAD  # 查看本地领先
   ```

### ❌ 避免的做法
1. **不要积累大量提交后再推送**
   - 容易导致大型冲突
   - 增加代码审查难度

2. **不要忽略 hook 提醒**
   - 可能导致代码丢失
   - 团队协作时会造成混乱

3. **不要在公共分支强制推送**
   ```bash
   # ❌ 禁止这样做
   git push --force origin main
   
   # ✅ 如果需要，使用安全的方式
   git push --force-with-lease origin main
   ```

---

## 🛠️ 故障排除

### 问题 1: Push 被拒绝
```
❌ error: failed to push some refs to '...'
```

**解决方案**：
```bash
# 先拉取远程更新
git pull origin main --rebase

# 解决可能的冲突后再次推送
git push origin main
```

### 问题 2: 认证失败
```
❌ Authentication failed
```

**解决方案**：
1. 检查是否配置了 Git credential manager
2. 使用 GitHub Personal Access Token
3. 配置 SSH key（推荐）

### 问题 3: 同步脚本无法执行
```
❌ 无法加载文件，因为在此系统上禁止运行脚本
```

**PowerShell 解决方案**：
```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后重新运行同步脚本
.\sync_to_github.ps1
```

---

## 📊 同步状态检查命令

### 查看本地和远程差异
```bash
# 本地领先的提交（待推送）
git log --oneline HEAD..origin/main

# 远程领先的提交（待拉取）
git log --oneline origin/main..HEAD
```

### 查看分支跟踪状态
```bash
git branch -vv
```

输出示例：
```
* main    abc1234 [origin/main: ahead 2] 最新的提交信息
```
`ahead 2` 表示本地领先远程 2 个提交，需要推送。

---

## 🔗 相关资源

- [Git 官方文档 - git-push](https://git-scm.com/docs/git-push)
- [GitHub Desktop - 简化 Git 操作](https://desktop.github.com/)
- [Git Credential Manager - 认证管理](https://github.com/GitCredentialManager/git-credential-manager)

---

## 📞 需要帮助？

如果遇到同步问题，请检查：
1. 网络连接是否正常
2. GitHub 账号权限是否正确
3. Git 配置是否正确（`git config --list`）
4. 远程仓库 URL 是否正确（`git remote -v`）

**仓库地址**: https://github.com/xuan15x/Translation
