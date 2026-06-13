# MediaNest

<div align="center">

📺 强大的媒体管理和播放系统

[English](#english) | [中文](#中文)

</div>

---

## 中文

### 📚 项目介绍

MediaNest 是一个功能完整的开源媒体管理和播放系统，基于 FastAPI 和现代 Web 技术构建。它提供了一个强大的 Web 界面，用于浏览、管理和播放多媒体文件（图片、视频等），支持播放列表管理、进度追踪、M3U 格式导出等多种功能。

### ✨ 主要功能

- **媒体浏览**: 支持按文件夹结构浏览图片和视频，实时显示文件信息
- **媒体播放**: 集成的播放器，支持视频和图片的流式播放
- **播放列表管理**: 创建、保存和管理自定义播放列表，支持导入/导出
- **播放进度追踪**: 自动保存播放位置和播放列表，支持继续播放
- **M3U 播放列表支持**: 生成标准的 M3U 格式播放列表，支持随机排序
- **媒体库管理**:
  - 添加/删除媒体根目录
  - 同步和索引媒体文件
  - 智能缓存管理
  - 文件标记和删除功能
- **缩略图生成**: 自动为图片生成缩略图，支持自定义尺寸
- **多并发处理**: 支持多线程处理图片和视频文件

### 🚀 快速开始

#### 系统要求

- **操作系统**: Linux, macOS, Windows
- **Python 版本**: 3.8 或更高版本
- **内存**: 最少 512MB（推荐 2GB 或以上）
- **存储**: 根据媒体库大小而定

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

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. 安装依赖**

```bash
pip install -r requirements.txt
```

必需的依赖包括：
- `fastapi>=0.95.0` - 现代 Web 框架
- `uvicorn>=0.21.0` - ASGI 服务器
- `pydantic>=1.10.0` - 数据验证库

**4. 配置应用**

编辑 `src/media_nest/core/constant.py` 文件，配置以下参数：

```python
# 缩略图设置
THUMB_MODE = True                    # 是否启用缩略图
THUMB_SIZE = (256, 256)             # 缩略图大小
THUMB_SAVE_PATH = Path("/Media/thumbnails")  # 缩略图保存路径

# 并发设置
IMAGE_WORKERS = 16                   # 处理图片的线程数
VIDEO_WORKERS = 4                    # 处理视频的线程数

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

**5. 启动应用**

```bash
# 开发环境
cd src/media_nest
python main.py

# 生产环境
uvicorn media_nest.main:app --host 0.0.0.0 --port 8000 --workers 4
```

应用将在 `http://localhost:8000` 启动

### 📁 项目结构

```
MediaNest/
├── src/
│   └── media_nest/
│       ├── core/                    # 核心模块
│       │   ├── constant.py          # 常量配置
│       │   ├── db_manager.py        # 数据库管理器
│       │   └── __init__.py
│       ├── models/                  # 数据模型
│       │   ├── __init__.py
│       │   ├── root_info.py         # 媒体根目录信息
│       │   ├── node_info.py         # 节点信息（文件/文件夹）
│       │   ├── video_segment_info.py # 视频分段信息
│       │   └── task_segment_info.py # 任务分段信息
│       ├── repository/              # 数据访问层 (DAO)
│       │   ├── __init__.py
│       │   ├── repository.py        # 数据库查询接口
│       │   └── tool.py              # 数据库工具函数
│       ├── service/                 # 业务逻辑层
│       │   ├── __init__.py
│       │   ├── service.py           # 主要服务类
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
│   ├── index.html                   # 主页面
│   ├── css/                         # 样式文件
│   ├── js/                          # JavaScript 文件
│   └── images/                      # 图片资源
├── pyproject.toml                   # 项目配置文件
├── requirements.txt                 # Python 依赖
├── media_info.db                    # SQLite 数据库（首次运行创建）
├── last_playlist.json               # 最后播放的播放列表（自动生成）
├── progress.txt                     # 播放进度记录（自动生成）
└── README.md                        # 本文件
```

### 🔌 详细 API 文档

#### 媒体管理 (`/media`)

##### 1. 获取所有媒体根目录
```
GET /media/root
```
**响应示例:**
```json
{
  "folders": [
    {
      "type": "folder",
      "parent_path": "/",
      "name": "Videos",
      "size": 5368709120
    }
  ],
  "files": []
}
```

##### 2. 获取文件夹内容
```
GET /media/folder/{path}
```
**参数:**
- `path` (string): 文件夹路径

**响应示例:**
```json
{
  "folders": [
    {
      "id": 1,
      "type": "folder",
      "parent_path": "/Videos",
      "name": "Movies",
      "size": 1073741824,
      "marked": false
    }
  ],
  "files": [
    {
      "id": 2,
      "type": "video",
      "parent_path": "/Videos",
      "name": "example.mp4",
      "size": 536870912,
      "width": 1920,
      "height": 1080,
      "duration": 3600,
      "marked": false
    }
  ]
}
```

##### 3. 获取图片
```
GET /media/image/{path}
```

##### 4. 获取视频
```
GET /media/video/{path}
```

##### 5. 获取缩略图
```
GET /media/thumb/{path}
```

##### 6. 获取标记的文件
```
GET /media/filter_marked
```

##### 7. 保存播放列表
```
POST /media/playlist
Content-Type: application/json

{
  "playlist": [[list[dict], list[dict]]]
}
```

##### 8. 保存播放进度
```
POST /media/progress
Content-Type: application/json

{
  "index": 5
}
```

##### 9. 继续上次播放
```
GET /media/continue_last_play
```

#### 管理 (`/admin`)

##### 1. 添加媒体根目录
```
POST /admin/add_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```
**说明:** 添加新的媒体库根目录，系统将扫描该目录下的所有媒体文件

##### 2. 删除媒体根目录
```
POST /admin/delete_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```

##### 3. 清空所有根目录
```
POST /admin/clear_root
```
**警告:** 这会删除所有根目录配置

##### 4. 同步媒体库
```
POST /admin/sync
```
**说明:** 扫描并索引媒体库中的所有文件，建立缓存，生成缩略图

##### 5. 清空缓存
```
POST /admin/clear_cache
```
**说明:** 清除所有缓存的媒体信息和缩略图

##### 6. 标记文件
```
POST /admin/mark
Content-Type: application/json

{
  "id": 1,
  "marked": true
}
```

##### 7. 删除文件
```
POST /admin/delete
Content-Type: application/json

{
  "id": 1,
  "path": "/path/to/file"
}
```
**警告:** 这将永久删除文件系统中的文件

#### 播放列表 (`/playlist`)

##### 生成 M3U 播放列表
```
GET /playlist/{path}?shuffle_flag=false
```
**参数:**
- `path` (string): 文件夹路径
- `shuffle_flag` (boolean): 是否随机排序 (可选，默认 false)

**响应类型:** `application/vnd.apple.mpegurl`

**M3U 格式示例:**
```
#EXTM3U
#EXT-INF:3600,example.mp4
http://192.168.0.110:8000/media/video/Videos/example.mp4
#EXT-INF:1800,example2.mp4
http://192.168.0.110:8000/media/video/Videos/example2.mp4
```

### 📊 数据库结构

MediaNest 使用 SQLite 数据库存储媒体信息，包含以下主要表：

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
width               INTEGER              # 图片/视频宽度
height              INTEGER              # 图片/视频高度
marked              BOOLEAN              # 是否标记
```

### 💡 使用指南

#### 基本工作流程

1. **添加媒体库**
   ```bash
   # 通过 API 或 Web 界面添加媒体根目录
   curl -X POST http://localhost:8000/admin/add_root \
     -H "Content-Type: application/json" \
     -d '{"path": "/home/user/Videos"}'
   ```

2. **同步媒体库**
   ```bash
   # 扫描并索引媒体文件
   curl -X POST http://localhost:8000/admin/sync
   ```

3. **浏览媒体**
   - 访问 Web 界面：`http://localhost:8000`
   - 浏览文件夹结构
   - 点击播放媒体文件

4. **管理播放列表**
   - 在播放器中创建自定义播放列表
   - 播放列表会自动保存
   - 支持导出为 M3U 格式

5. **导出播放列表**
   ```bash
   # 获取 M3U 格式的播放列表
   curl http://localhost:8000/playlist/path/to/folder > playlist.m3u
   ```

#### 高级配置

**启用随机播放**
```
GET /playlist/path/to/folder?shuffle_flag=true
```

**自定义缩略图尺寸**
在 `constant.py` 中修改：
```python
THUMB_SIZE = (512, 512)  # 更大的缩略图
```

**调整并发处理**
```python
IMAGE_WORKERS = 32   # 增加图片处理线程
VIDEO_WORKERS = 8    # 增加视频处理线程
```

### 🐛 常见问题

**Q: 添加了媒体目录后看不到文件？**
A: 需要运行同步操作。调用 `/admin/sync` 端点扫描并索引文件。

**Q: 缩略图生成失败？**
A: 检查 `THUMB_SAVE_PATH` 目录是否存在且有写入权限。

**Q: 支持哪些文件格式？**
A: 
- 图片: JPG, JPEG, PNG, GIF, WebP
- 视频: MP4, AVI, MOV, MKV
可在 `constant.py` 中修改 `IMAGE_SUFFIX` 和 `VIDEO_SUFFIX` 配置。

**Q: 如何清除所有数据重新开始？**
A: 调用 `/admin/clear_cache` 清空缓存，然后重新同步。

### 🔧 故障排除

**数据库错误**
```
如果遇到数据库锁定错误，删除 media_info.db 文件并重新启动应用即可重建数据库。
```

**端口已被占用**
```bash
# 使用不同的端口启动
uvicorn media_nest.main:app --port 8080
```

**内存不足**
```
减少并发处理数：
IMAGE_WORKERS = 8    # 原为 16
VIDEO_WORKERS = 2    # 原为 4
```

### 🛠️ 开发指南

#### 项目架构

MediaNest 采用分层架构：

- **Web 层** (`web/`) - API 路由和请求处理
- **Service 层** (`service/`) - 业务逻辑实现
- **Repository 层** (`repository/`) - 数据持久化
- **Core 层** (`core/`) - 核心工具和配置

#### 添加新的媒体格式

1. 在 `constant.py` 中添加文件后缀
2. 在 `models/` 中创建对应的数据模型
3. 在 `service/` 中添加处理逻辑

#### 扩展 API

在 `web/` 目录中创建新的路由文件，并在 `main.py` 中注册路由。

### 🛠️ 技术栈

- **后端框架**: FastAPI 0.95.0+
- **Web 服务器**: Uvicorn 0.21.0+
- **数据库**: SQLite (内置)
- **数据验证**: Pydantic 1.10.0+
- **前端**: HTML5 / CSS3 / JavaScript

### 📝 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**贡献流程:**
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 📧 联系方式

如有问题或建议，欢迎通过 GitHub Issues 联系我们

---

## English

### 📚 Project Description

MediaNest is a feature-rich, open-source media management and playback system built with FastAPI and modern web technologies. It provides a powerful web interface for browsing, managing, and playing multimedia files (images, videos, etc.), with support for playlist management, progress tracking, M3U format export, and more.

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

- **Operating System**: Linux, macOS, Windows
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

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install Dependencies**

```bash
pip install -r requirements.txt
```

Required packages include:
- `fastapi>=0.95.0` - Modern web framework
- `uvicorn>=0.21.0` - ASGI server
- `pydantic>=1.10.0` - Data validation library

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
│       │   ├── root_info.py         # Media root directory info
│       │   ├── node_info.py         # Node info (files/folders)
│       │   ├── video_segment_info.py # Video segment info
│       │   └── task_segment_info.py # Task segment info
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
│   ├── index.html                   # Main page
│   ├── css/                         # Style files
│   ├── js/                          # JavaScript files
│   └── images/                      # Image resources
├── pyproject.toml                   # Project configuration
├── requirements.txt                 # Python dependencies
├── media_info.db                    # SQLite database (created on first run)
├── last_playlist.json               # Last played playlist (auto-generated)
├── progress.txt                     # Playback progress record (auto-generated)
└── README.md                        # This file
```

### 🔌 Detailed API Documentation

#### Media Management (`/media`)

##### 1. Get All Media Root Directories
```
GET /media/root
```
**Response Example:**
```json
{
  "folders": [
    {
      "type": "folder",
      "parent_path": "/",
      "name": "Videos",
      "size": 5368709120
    }
  ],
  "files": []
}
```

##### 2. Get Folder Contents
```
GET /media/folder/{path}
```
**Parameters:**
- `path` (string): Folder path

**Response Example:**
```json
{
  "folders": [
    {
      "id": 1,
      "type": "folder",
      "parent_path": "/Videos",
      "name": "Movies",
      "size": 1073741824,
      "marked": false
    }
  ],
  "files": [
    {
      "id": 2,
      "type": "video",
      "parent_path": "/Videos",
      "name": "example.mp4",
      "size": 536870912,
      "width": 1920,
      "height": 1080,
      "duration": 3600,
      "marked": false
    }
  ]
}
```

##### 3. Get Image
```
GET /media/image/{path}
```

##### 4. Get Video
```
GET /media/video/{path}
```

##### 5. Get Thumbnail
```
GET /media/thumb/{path}
```

##### 6. Get Marked Files
```
GET /media/filter_marked
```

##### 7. Save Playlist
```
POST /media/playlist
Content-Type: application/json

{
  "playlist": [[list[dict], list[dict]]]
}
```

##### 8. Save Playback Progress
```
POST /media/progress
Content-Type: application/json

{
  "index": 5
}
```

##### 9. Resume Last Playback
```
GET /media/continue_last_play
```

#### Admin (`/admin`)

##### 1. Add Media Root Directory
```
POST /admin/add_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```
**Description:** Add a new media library root directory. The system will scan all media files in that directory.

##### 2. Remove Media Root Directory
```
POST /admin/delete_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```

##### 3. Clear All Root Directories
```
POST /admin/clear_root
```
**Warning:** This will delete all root directory configurations.

##### 4. Sync Media Library
```
POST /admin/sync
```
**Description:** Scan and index all files in the media library, build cache, and generate thumbnails.

##### 5. Clear Cache
```
POST /admin/clear_cache
```
**Description:** Clear all cached media information and thumbnails.

##### 6. Mark File
```
POST /admin/mark
Content-Type: application/json

{
  "id": 1,
  "marked": true
}
```

##### 7. Delete File
```
POST /admin/delete
Content-Type: application/json

{
  "id": 1,
  "path": "/path/to/file"
}
```
**Warning:** This will permanently delete the file from the file system.

#### Playlist (`/playlist`)

##### Generate M3U Playlist
```
GET /playlist/{path}?shuffle_flag=false
```
**Parameters:**
- `path` (string): Folder path
- `shuffle_flag` (boolean): Enable random shuffle (optional, default false)

**Response Type:** `application/vnd.apple.mpegurl`

**M3U Format Example:**
```
#EXTM3U
#EXT-INF:3600,example.mp4
http://192.168.0.110:8000/media/video/Videos/example.mp4
#EXT-INF:1800,example2.mp4
http://192.168.0.110:8000/media/video/Videos/example2.mp4
```

### 📊 Database Structure

MediaNest uses SQLite database to store media information with the following main tables:

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
   # Add media root directory via API or Web interface
   curl -X POST http://localhost:8000/admin/add_root \
     -H "Content-Type: application/json" \
     -d '{"path": "/home/user/Videos"}'
   ```

2. **Sync Media Library**
   ```bash
   # Scan and index media files
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

5. **Export Playlist**
   ```bash
   # Get M3U format playlist
   curl http://localhost:8000/playlist/path/to/folder > playlist.m3u
   ```

#### Advanced Configuration

**Enable Shuffle Playback**
```
GET /playlist/path/to/folder?shuffle_flag=true
```

**Custom Thumbnail Size**
Modify in `constant.py`:
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
Modify `IMAGE_SUFFIX` and `VIDEO_SUFFIX` in `constant.py` to add more formats.

**Q: How to clear all data and start fresh?**
A: Call `/admin/clear_cache` to clear cache, then resync.

### 🔧 Troubleshooting

**Database Error**
```
If you encounter database lock errors, delete the media_info.db file and restart the application to rebuild the database.
```

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

- **Backend Framework**: FastAPI 0.95.0+
- **Web Server**: Uvicorn 0.21.0+
- **Database**: SQLite (built-in)
- **Data Validation**: Pydantic 1.10.0+
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
