# MediaNest

<div align="center">

📺 One Media Playback and Management System | 一个媒体播放和管理系统

[English](#english) | [中文](#中文)

</div>

---

## 中文

# MediaNest

### 📚 项目介绍

MediaNest 是一个开源媒体管理和播放系统，基于 FastAPI 和现代网络技术构建。它提供了一个网络界面，用于浏览、管理和播放多媒体文件（图像、视频等），支持播放列表管理、进度跟踪、M3U 格式导出等功能。

### ✨ 主要功能

- **媒体浏览**：支持按文件夹结构浏览图像和视频，实时显示文件信息
- **媒体播放**：集成播放器支持视频和图像流媒体
- **播放列表管理**：创建、保存和管理自定义播放列表，支持导入/导出
- **播放进度跟踪**：自动保存播放位置和播放列表，支持继续播放功能
- **M3U 播放列表支持**：生成标准 M3U 格式播放列表，支持随机播放
- **媒体库管理**：
  - 添加/删除媒体根目录
  - 同步和索引媒体文件
  - 智能缓存管理
  - 文件标记和删除
- **缩略图生成**：自动为图像生成缩略图，支持自定义尺寸
- **多线程处理**：支持图像和视频文件的并发处理

### 🚀 快速开始

#### 系统需求

- **操作系统**：Linux、macOS
- **Python 版本**：3.8 或更高
- **内存**：最少 512MB（建议 2GB 或更多）
- **存储**：取决于媒体库大小

#### 详细安装步骤

**1. 克隆仓库**

```bash
git clone <repository-url>
cd MediaNest
```

**2. 创建虚拟环境（可选但推荐）**

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

**3. 安装依赖**

```bash
pip install -r requirements.txt
```

必需的包包括：
- `fastapi>=0.136.0` - 现代网络框架
- `uvicorn>=0.49.0` - ASGI 服务器
- `Pillow>=12.0.0` - 图像处理库
- `pytest>=9.0.0` - 测试框架

**4. 配置应用程序**

编辑 `src/media_nest/core/constant.py` 文件配置参数：

```python
# 缩略图设置
THUMB_MODE = True                    # 启用缩略图
THUMB_SIZE = (256, 256)             # 缩略图尺寸
THUMB_SAVE_PATH = Path("/Media/thumbnails")  # 缩略图保存路径

# 并发设置
IMAGE_WORKERS = 16                   # 图像处理线程数
VIDEO_WORKERS = 4                    # 视频处理线程数

# 数据库和路径配置
DB_PATH = ROOT_PATH / "media_info.db"  # 数据库文件路径
STATIC_PATH = ROOT_PATH / "static"     # 静态资源路径
LAST_PLAYLIST = ROOT_PATH / "last_playlist.json"  # 最后播放列表
LAST_PROGRESS = ROOT_PATH / "progress.txt"       # 播放进度文件

# M3U 播放列表配置
BASE_URL = "http://192.168.0.110:8000"  # 服务器地址
M3U_ITEM_NUM_LIMIT = 3000          # M3U 播放列表项目限制

# 支持的文件格式
IMAGE_SUFFIX = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_SUFFIX = {".mp4", ".avi", ".mov", ".mkv"}
```

**5. 启动应用程序**

```bash
# 开发环境
cd src/media_nest
python main.py

# 生产环境
uvicorn media_nest.main:app --host 0.0.0.0 --port 8000 --workers 4
```

应用程序将在 `http://localhost:8000` 启动

### 📁 项目结构

```
MediaNest/
├── src/
│   └── media_nest/
│       ├── core/                    # 核心模块
│       │   ├── constant.py          # 配置常数
│       │   ├── db_manager.py        # 数据库管理器
│       │   └── __init__.py
│       ├── models/                  # 数据模型
│       │   ├── __init__.py
│       │   ├── db_table_info.py         # db 表对应的 models
│       │   └─── video_segment_info.py # 视频段信息
│       ├── repository/              # 数据访问层（DAO）
│       │   ├── __init__.py
│       │   ├── repository.py        # 数据库查询接口
│       │   └── tool.py              # 数据库工具函数
│       ├── service/                 # 业务逻辑层
│       │   ├── __init__.py
│       │   ├── service.py           # 主服务类
│       │   ├── sync_library.py      # 媒体库同步
│       │   ├── deal_task.py         # 任务处理
│       │   ├── build_m3u.py         # M3U 播放列表生成
│       │   └── play_progress.py     # 播放进度管理
│       ├── web/                     # API 路由
│       │   ├── __init__.py
│       │   ├── media.py             # 媒体相关路由
│       │   ├── admin.py             # 管理操作路由
│       │   └── playlist.py           # 播放列表路由
│       └── main.py                  # FastAPI 应用入口
├── static/                          # 前端静态资源
├── pyproject.toml                   # 项目配置
├── requirements.txt                 # Python 依赖
├── media_info.db                    # SQLite 数据库（首次运行时创建）
├── last_playlist.json               # 最后播放列表（自动生成）
├── progress.txt                     # 播放进度记录（自动生成）
└── README.md                        # 本文件
```

### 🔌 详细 API 文档

#### 媒体管理 (`/media`)

**1. 获取所有媒体根目录**
```
GET /media/root
```

**2. 获取文件夹内容**
```
GET /media/folder/{path}
```

**3. 获取图像**
```
GET /media/image/{path}
```

**4. 获取视频**
```
GET /media/video/{path}
```

**5. 获取缩略图**
```
GET /media/thumb/{path}
```

**6. 获取标记文件**
```
GET /media/filter_marked
```

**7. 保存播放列表**
```
POST /media/playlist
Content-Type: application/json

{
  "playlist": [[list[dict], list[dict]]]
}
```

**8. 保存播放进度**
```
POST /media/progress
Content-Type: application/json

{
  "index": 5
}
```

**9. 继续最后播放**
```
GET /media/continue_last_play
```

#### 管理员 (`/admin`)

**1. 添加媒体根目录**
```
POST /admin/add_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```

**2. 删除媒体根目录**
```
POST /admin/delete_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```

**3. 清除所有根目录**
```
POST /admin/clear_root
```

**4. 同步媒体库**
```
POST /admin/sync
```

**5. 清除缓存**
```
POST /admin/clear_cache
```

**6. 标记文件**
```
POST /admin/mark
Content-Type: application/json

{
  "id": 1,
  "marked": true
}
```

**7. 删除文件**
```
POST /admin/delete
Content-Type: application/json

{
  "id": 1,
  "path": "/path/to/file"
}
```

#### 播放列表 (`/playlist`)

**生成 M3U 播放列表**
```
GET /playlist/{path}?shuffle_flag=false
```

**参数：**
- `path` (string)：文件夹路径
- `shuffle_flag` (boolean)：启用随机播放（可选，默认 false）

### 📊 数据库结构

**root_info 表** - 媒体根目录
```
id                  INTEGER PRIMARY KEY
path                TEXT UNIQUE NOT NULL
last_sync_time      TIMESTAMP
size                INTEGER
```

**node_info 表** - 文件和文件夹节点
```
id                  INTEGER PRIMARY KEY
dev                 INTEGER              # 设备号
ino                 INTEGER              # inode 号
root_id             INTEGER FOREIGN KEY
parent_path         TEXT NOT NULL
name                TEXT NOT NULL
type_               TEXT NOT NULL        # 'file', 'folder', 'video', 'image'
size                INTEGER
mtime               INTEGER              # 修改时间
duration_ms         INTEGER              # 视频时长（毫秒）
width               INTEGER              # 图像/视频宽度
height              INTEGER              # 图像/视频高度
marked              BOOLEAN              # 是否标记
```

### 💡 使用指南

#### 基本工作流

1. **添加媒体库**
   ```bash
   curl -X POST http://localhost:8000/admin/add_root \
     -H "Content-Type: application/json" \
     -d '{"path": "/home/user/Videos"}'
   ```

2. **同步媒体库**
   ```bash
   curl -X POST http://localhost:8000/admin/sync
   ```

3. **浏览媒体**
   - 访问网页界面：`http://localhost:8000`
   - 浏览文件夹结构
   - 点击播放媒体文件

4. **管理播放列表**
   - 在播放器中创建自定义播放列表
   - 播放列表自动保存
   - 支持导出为 M3U 格式

#### 高级配置

**启用随机播放**
```
GET /playlist/path/to/folder?shuffle_flag=true
```

**自定义缩略图大小**
```python
THUMB_SIZE = (512, 512)  # 更大的缩略图
```

**调整并发处理**
```python
IMAGE_WORKERS = 32   # 增加图像处理线程
VIDEO_WORKERS = 8    # 增加视频处理线程
```

### 🐛 常见问题

**问：添加媒体目录后看不到文件？**
答：运行同步操作。调用 `/admin/sync` 端点扫描和索引文件。

**问：缩略图生成失败？**
答：检查 `THUMB_SAVE_PATH` 目录是否存在且有写入权限。

**问：支持哪些文件格式？**
答：
- 图像：JPG, JPEG, PNG, GIF, WebP
- 视频：MP4, AVI, MOV, MKV

**问：如何清除所有数据并重新开始？**
答：调用 `/admin/clear_cache` 清除缓存，然后重新同步。

### 🔧 故障排除

**数据库错误**
如果遇到数据库锁定错误，删除 media_info.db 文件并重启应用程序以重建数据库。

**端口已在使用**
```bash
uvicorn media_nest.main:app --port 8080
```

**内存不足**
```
减少并发处理：
IMAGE_WORKERS = 8    # 原为 16
VIDEO_WORKERS = 2    # 原为 4
```

### 🛠️ 开发指南

#### 项目架构

MediaNest 使用分层架构：

- **网络层** (`web/`) - API 路由和请求处理
- **服务层** (`service/`) - 业务逻辑实现
- **存储库层** (`repository/`) - 数据持久化
- **核心层** (`core/`) - 核心工具和配置

#### 添加新媒体格式

1. 在 `constant.py` 中添加文件后缀
2. 在 `models/` 中创建相应的数据模型
3. 在 `service/` 中添加处理逻辑

#### 扩展 API

在 `web/` 目录中创建新的路由文件，并在 `main.py` 中注册路由。

### 🛠️ 技术栈

- **后端框架**：FastAPI 0.136.0+
- **网络服务器**：Uvicorn 0.49.0+
- **数据库**：SQLite（内置）
- **图像处理**：Pillow 12.0.0+
- **测试框架**：Pytest 9.0.0+
- **前端**：HTML5 / CSS3 / JavaScript

### 📝 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

### 🤝 贡献

欢迎提交 Issues 和 Pull Requests！

**贡献流程：**
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 📧 联系方式

如有问题或建议，请通过 GitHub Issues 与我们联系

---

## English

# MediaNest

### 📚 Project Description

MediaNest is an open-source media management and playback system built with FastAPI and modern web technologies. It provides a web interface for browsing, managing, and playing multimedia files (images, videos, etc.), with support for playlist management, progress tracking, M3U format export, and more.

### ✨ Features

- **Media Browsing**: Support for browsing images and videos by folder structure with real-time file information
- **Media Playback**: Integrated player supporting video and image streaming
- **Playlist Management**: Create, save, and manage custom playlists with import/export support
- **Playback Progress Tracking**: Automatically save playback position and playlist with resume capability
- **M3U Playlist Support**: Generate standard M3U format playlists with shuffle option
- **Media Library Management**:
  - Add/remove media root directories
  - Sync and index media files
  - Intelligent cache management
  - File marking and deletion
- **Thumbnail Generation**: Auto-generate thumbnails for images with customizable sizes
- **Multi-threaded Processing**: Support concurrent processing of images and video files

### 🚀 Quick Start

#### System Requirements

- **Operating System**: Linux, macOS
- **Python Version**: 3.8 or higher
- **Memory**: Minimum 512MB (recommended 2GB or more)
- **Storage**: Depends on media library size

#### Detailed Installation Steps

**1. Clone the Repository**

```bash
git clone <repository-url>
cd MediaNest
```

**2. Create Virtual Environment (Optional but Recommended)**

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**

```bash
pip install -r requirements.txt
```

Required packages include:
- `fastapi>=0.136.0` - Modern web framework
- `uvicorn>=0.49.0` - ASGI server
- `Pillow>=12.0.0` - Image processing library
- `pytest>=9.0.0` - Testing framework

**4. Configure Application**

Edit the `src/media_nest/core/constant.py` file to configure parameters:

```python
# Thumbnail settings
THUMB_MODE = True                    # Enable thumbnails
THUMB_SIZE = (256, 256)             # Thumbnail size
THUMB_SAVE_PATH = Path("/Media/thumbnails")  # Thumbnail save path

# Concurrency settings
IMAGE_WORKERS = 16                   # Image processing threads
VIDEO_WORKERS = 4                    # Video processing threads

# Database and path configuration
DB_PATH = ROOT_PATH / "media_info.db"  # Database file path
STATIC_PATH = ROOT_PATH / "static"     # Static resources path
LAST_PLAYLIST = ROOT_PATH / "last_playlist.json"  # Last played playlist
LAST_PROGRESS = ROOT_PATH / "progress.txt"       # Playback progress file

# M3U playlist configuration
BASE_URL = "http://192.168.0.110:8000"  # Server address
M3U_ITEM_NUM_LIMIT = 3000          # M3U playlist item limit

# Supported file formats
IMAGE_SUFFIX = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_SUFFIX = {".mp4", ".avi", ".mov", ".mkv"}
```

**5. Start Application**

```bash
# Development environment
cd src/media_nest
python main.py

# Production environment
uvicorn media_nest.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Application will start at `http://localhost:8000`

### 📁 Project Structure

```
MediaNest/
├── src/
│   └── media_nest/
│       ├── core/                    # Core modules
│       │   ├── constant.py          # Configuration constants
│       │   ├── db_manager.py        # Database manager
│       │   └── __init__.py
│       ├── models/                  # Data models
│       │   ├── __init__.py
│       │   ├── db_table_info.py         # Database table models
│       │   └── video_segment_info.py # Video segment info
│       ├── repository/              # Data Access Layer (DAO)
│       │   ├── __init__.py
│       │   ├── repository.py        # Database query interface
│       │   └── tool.py              # Database utility functions
│       ├── service/                 # Business Logic Layer
│       │   ├── __init__.py
│       │   ├── service.py           # Main service class
│       │   ├── sync_library.py      # Media library sync
│       │   ├── deal_task.py         # Task processing
│       │   ├── build_m3u.py         # M3U playlist generation
│       │   └── play_progress.py     # Playback progress management
│       ├── web/                     # API routes
│       │   ├── __init__.py
│       │   ├── media.py             # Media-related routes
│       │   ├── admin.py             # Admin operation routes
│       │   └── playlist.py           # Playlist routes
│       └── main.py                  # FastAPI application entry point
├── static/                          # Frontend static resources
├── pyproject.toml                   # Project configuration
├── requirements.txt                 # Python dependencies
├── media_info.db                    # SQLite database (created on first run)
├── last_playlist.json               # Last played playlist (auto-generated)
├── progress.txt                     # Playback progress record (auto-generated)
└── README.md                        # This file
```

### 🔌 Detailed API Documentation

#### Media Management (`/media`)

**1. Get All Media Root Directories**
```
GET /media/root
```

**2. Get Folder Contents**
```
GET /media/folder/{path}
```

**3. Get Image**
```
GET /media/image/{path}
```

**4. Get Video**
```
GET /media/video/{path}
```

**5. Get Thumbnail**
```
GET /media/thumb/{path}
```

**6. Get Marked Files**
```
GET /media/filter_marked
```

**7. Save Playlist**
```
POST /media/playlist
Content-Type: application/json

{
  "playlist": [[list[dict], list[dict]]]
}
```

**8. Save Playback Progress**
```
POST /media/progress
Content-Type: application/json

{
  "index": 5
}
```

**9. Resume Last Playback**
```
GET /media/continue_last_play
```

#### Admin (`/admin`)

**1. Add Media Root Directory**
```
POST /admin/add_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```

**2. Remove Media Root Directory**
```
POST /admin/delete_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```

**3. Clear All Root Directories**
```
POST /admin/clear_root
```

**4. Sync Media Library**
```
POST /admin/sync
```

**5. Clear Cache**
```
POST /admin/clear_cache
```

**6. Mark File**
```
POST /admin/mark
Content-Type: application/json

{
  "id": 1,
  "marked": true
}
```

**7. Delete File**
```
POST /admin/delete
Content-Type: application/json

{
  "id": 1,
  "path": "/path/to/file"
}
```

#### Playlist (`/playlist`)

**Generate M3U Playlist**
```
GET /playlist/{path}?shuffle_flag=false
```

**Parameters:**
- `path` (string): Folder path
- `shuffle_flag` (boolean): Enable random shuffle (optional, default false)

### 📊 Database Structure

**root_info Table** - Media root directories
```
id                  INTEGER PRIMARY KEY
path                TEXT UNIQUE NOT NULL
last_sync_time      TIMESTAMP
size                INTEGER
```

**node_info Table** - File and folder nodes
```
id                  INTEGER PRIMARY KEY
dev                 INTEGER              # Device number
ino                 INTEGER              # inode number
root_id             INTEGER FOREIGN KEY
parent_path         TEXT NOT NULL
name                TEXT NOT NULL
type_               TEXT NOT NULL        # 'file', 'folder', 'video', 'image'
size                INTEGER
mtime               INTEGER              # Modification time
duration_ms         INTEGER              # Video duration (milliseconds)
width               INTEGER              # Image/video width
height              INTEGER              # Image/video height
marked              BOOLEAN              # Whether marked
```

### 💡 Usage Guide

#### Basic Workflow

1. **Add Media Library**
   ```bash
   curl -X POST http://localhost:8000/admin/add_root \
     -H "Content-Type: application/json" \
     -d '{"path": "/home/user/Videos"}'
   ```

2. **Sync Media Library**
   ```bash
   curl -X POST http://localhost:8000/admin/sync
   ```

3. **Browse Media**
   - Visit Web interface: `http://localhost:8000`
   - Browse folder structure
   - Click to play media files

4. **Manage Playlists**
   - Create custom playlists in the player
   - Playlists are auto-saved
   - Support export to M3U format

#### Advanced Configuration

**Enable Shuffle Playback**
```
GET /playlist/path/to/folder?shuffle_flag=true
```

**Custom Thumbnail Size**
```python
THUMB_SIZE = (512, 512)  # Larger thumbnails
```

**Adjust Concurrent Processing**
```python
IMAGE_WORKERS = 32   # Increase image processing threads
VIDEO_WORKERS = 8    # Increase video processing threads
```

### 🐛 FAQ

**Q: Can't see files after adding media directory?**
A: Run the sync operation. Call the `/admin/sync` endpoint to scan and index files.

**Q: Thumbnail generation fails?**
A: Check if the `THUMB_SAVE_PATH` directory exists and has write permissions.

**Q: What file formats are supported?**
A: 
- Images: JPG, JPEG, PNG, GIF, WebP
- Videos: MP4, AVI, MOV, MKV

**Q: How to clear all data and start fresh?**
A: Call `/admin/clear_cache` to clear cache, then resync.

### 🔧 Troubleshooting

**Database Error**
If you encounter database lock errors, delete the media_info.db file and restart the application to rebuild the database.

**Port Already in Use**
```bash
# Start on a different port
uvicorn media_nest.main:app --port 8080
```

**Out of Memory**
```
Reduce concurrent processing:
IMAGE_WORKERS = 8    # Originally 16
VIDEO_WORKERS = 2    # Originally 4
```

### 🛠️ Development Guide

#### Project Architecture

MediaNest uses a layered architecture:

- **Web Layer** (`web/`) - API routes and request handling
- **Service Layer** (`service/`) - Business logic implementation
- **Repository Layer** (`repository/`) - Data persistence
- **Core Layer** (`core/`) - Core utilities and configuration

#### Adding New Media Formats

1. Add file suffix in `constant.py`
2. Create corresponding data model in `models/`
3. Add processing logic in `service/`

#### Extending API

Create new route files in `web/` directory and register routes in `main.py`.

### 🛠️ Tech Stack

- **Backend Framework**: FastAPI 0.136.0+
- **Web Server**: Uvicorn 0.49.0+
- **Database**: SQLite (built-in)
- **Image Processing**: Pillow 12.0.0+
- **Testing Framework**: Pytest 9.0.0+
- **Frontend**: HTML5 / CSS3 / JavaScript

### 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

### 🤝 Contributing

Issues and Pull Requests are welcome!

**Contributing Process:**
1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📧 Contact

For questions or suggestions, please contact us via GitHub Issues
