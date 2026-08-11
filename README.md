# 桌面宠物 - 安卓版

## 功能说明
- 双角色切换（真人版 / 卡通版）
- 触摸拖动角色
- 点击触发随机互动（跳跃/压扁/抖动）
- 对话气泡
- 抱抱互动（卡通版专属）
- 自动走路
- 睡觉模式
- 底部快捷按钮栏

---

## 方案一：GitHub Actions 在线打包（推荐，免费）

不需要配置本地环境，用 GitHub 免费服务器打包：

### 步骤：

1. **注册 GitHub 账号**（如果没有）：https://github.com

2. **创建新仓库**：
   - 点击右上角 "+" → "New repository"
   - 仓库名随便填，比如 `desktoppet`
   - 选 Public（公开），勾选 "Add a README file"
   - 点击 "Create repository"

3. **上传文件**：
   - 在仓库页面点击 "Add file" → "Upload files"
   - 把本文件夹里的**所有文件**拖进去（main.py, buildozer.spec, 3张png图片, .github文件夹）
   - 拉到最下面点击 "Commit changes"

4. **触发打包**：
   - 点击仓库上方的 "Actions" 标签
   - 左边选 "Build Android APK"
   - 点击右边 "Run workflow" → 再点 "Run workflow"
   - 等待约 15-30 分钟（第一次会下载SDK，比较慢）

5. **下载 APK**：
   - 打包完成后，点击那个绿色对勾的任务
   - 拉到最下面 "Artifacts" 部分
   - 点击 `desktoppet-apk` 下载
   - 解压后就是 APK 文件，传到手机安装

---

## 方案二：Google Colab 在线打包

需要 Google 账号，用 Colab 免费服务器：

1. 打开 https://colab.research.google.com
2. 新建笔记本，依次运行以下代码：

```python
# 安装依赖
!sudo apt update
!sudo apt install -y openjdk-17-jdk build-essential git zlib1g-dev
!pip install buildozer cython

# 挂载Google Drive（可选，用于保存APK）
from google.colab import drive
drive.mount('/content/drive')

# 上传项目文件到 /content/desktoppet/ 目录
# （左侧文件图标 → 上传 → 选择所有文件）

# 打包
%cd /content/desktoppet
!buildozer android debug

# APK 在 bin/ 目录，下载到本地
```

---

## 方案三：Kivy Launcher 快速运行（最简单，5分钟）

不需要打包，直接运行代码：

1. 手机应用商店搜索安装 **"Kivy Launcher"**
   - 或下载：https://github.com/kivy/kivy-launcher/releases
2. 把本项目整个文件夹复制到手机 **内部存储/kivy/** 目录下
   - 没有 kivy 文件夹就手动创建
3. 打开 Kivy Launcher，点击"桌面宠物"运行

---

## 方案四：本地 WSL 打包（需要管理员权限）

1. **启用 WSL**（需要管理员 PowerShell）：
   ```powershell
   wsl --install -d Ubuntu
   ```
   重启电脑，设置 Ubuntu 用户名密码

2. **Ubuntu 中安装依赖**：
   ```bash
   sudo apt update
   sudo apt install -y openjdk-17-jdk python3-pip build-essential git zlib1g-dev
   pip3 install buildozer cython
   ```

3. **打包**：
   ```bash
   cd /mnt/c/路径到/android
   buildozer android debug
   ```

4. APK 在 `bin/` 目录

---

## 项目文件说明
- `main.py` - 主程序代码
- `buildozer.spec` - 打包配置
- `character.png` - 真人版角色
- `character2.png` - 卡通版角色
- `hug.png` - 抱抱形象
- `.github/workflows/build.yml` - GitHub Actions 自动打包配置

## 权限说明
- `SYSTEM_ALERT_WINDOW` - 悬浮窗权限
- `FOREGROUND_SERVICE` - 前台服务权限

## 注意事项
1. 首次打包会下载 Android SDK/NDK，约 2GB，需要耐心等待
2. GitHub Actions 免费额度每月 2000 分钟，足够用
3. 生成的是 debug 版 APK，可以直接安装
4. 安装时如果提示"未知来源"，需要在手机设置里允许安装未知应用

