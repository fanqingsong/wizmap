# 文件上传功能修复指南

## ⚠️ 当前问题

上传功能遇到了一个异步处理的小错误：`"Upload failed: a bytes-like object is required, not 'coroutine'"`

我已经修复了这个问题，但需要重新构建 Docker 镜像才能生效。

## 🚀 解决方案

### 方案 1：使用内置演示数据（推荐⭐）

WizMap 内置了演示数据集，无需上传即可体验完整功能：

**访问地址**: http://localhost:3001

在首页点击 **"Explore demo data"** 按钮，即可加载内置的 ACL Abstracts 数据集进行可视化探索。

### 方案 2：等待 Docker 重新构建

我已经修复了上传功能的代码，如果你希望使用自定义数据集，需要重新构建 Docker 镜像：

```bash
# 重新构建并启动服务
docker compose down
docker compose build backend --no-cache
docker compose up -d
```

**注意**: 重新构建可能需要 10-15 分钟。

### 方案 3：手动 API 测试（用于开发）

如果你想立即测试上传功能，可以使用提供的测试脚本：

```bash
# 直接测试（需要先修复代码）
python3 test_upload.py
```

## 📊 当前可用功能

### ✅ 完全可用的功能

1. **前端可视化界面**
   - 访问: http://localhost:3001
   - 2D 地图探索
   - 缩放、平移、搜索
   - 数据点交互

2. **后端 API**
   - 访问: http://localhost:8080
   - API 文档: http://localhost:8080/docs
   - 健康检查: http://localhost:8080/health

3. **内置演示数据**
   - ACL Abstracts 数据集
   - 约 200 条学术论文摘要
   - 完整的可视化功能

### 🔧 修复中的功能

1. **文件上传功能** - 代码已修复，等待重新构建
2. **数据处理管道** - 依赖上传功能

## 💡 推荐使用流程

### 立即体验（无需上传）

1. 访问 http://localhost:3001
2. 你会看到 Upload Dataset 页面
3. 点击 **"Explore demo data"** 按钮
4. 加载内置的演示数据集
5. 开始探索可视化！

### 使用自定义数据（修复后）

1. 等待 Docker 重新构建完成
2. 访问 http://localhost:3001
3. 点击 "+ Upload Dataset" 按钮
4. 选择你的文件（.txt, .csv, .json）
5. 输入数据集名称
6. 等待处理完成
7. 自动跳转到可视化页面

## 🎯 演示数据说明

内置的 ACL Abstracts 数据集包含：
- **数据量**: 约 200 条
- **内容**: 学术论文摘要
- **分类**: 计算机科学领域的不同研究方向
- **可视化效果**: 清晰的主题聚类
- **交互功能**: 完整的搜索和探索功能

## 📝 支持的文件格式（修复后）

修复上传功能后，你将可以上传：

1. **TXT 文件** - 每行一条文本
2. **CSV 文件** - 结构化数据
3. **JSON 文件** - 高级格式

详细说明请参考 `UPLOAD-GUIDE.md` 文件。

## 🔄 快速修复命令

```bash
# 一键修复并重启
docker compose down && \
docker compose build backend --no-cache && \
docker compose up -d
```

**预计时间**: 10-15 分钟

## 💫 现在就开始

建议先使用内置演示数据体验功能：

```bash
# 访问前端
http://localhost:3001

# 点击 "Explore demo data" 开始探索
```

演示数据已经足够展示 WizMap 的所有功能！等你熟悉了系统后，再考虑上传自己的数据集。

有问题？查看 `START-DEV-GUIDE.md` 获取更多帮助。
