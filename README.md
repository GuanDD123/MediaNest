# MediaNest

<div align="center">

Media Playback & Library Management System | 媒体播放与库管理系统

[English](#english) | [中文](#中文)

</div>

---

## English

# MediaNest

MediaNest is a FastAPI-based local media browser and playback web app. It focuses on browsing local media folders, serving images and videos in the browser, preserving playlist state, tracking the last playback position, and synchronizing media libraries with a small SQLite-backed backend.

## Features

- Folder and file browsing with media metadata
- Auto-generate thumbnails for images with customizable sizes
- Web playback for images and videos
- Playlist save/restore and continue-last-play support
- M3U playlist export for external playback clients
- Background library sync with progress reporting
- WebSocket progress stream for sync status
- Console + rotating file logging

## Core workflow

1. Start the app with Python:

```bash
python run.py
```

2. Open the web UI at:

```text
http://localhost:8001
```

3. Add one or more media roots through the admin API.

4. Trigger a library sync to scan files, build the database index, and process media tasks.

5. Use the media UI to browse, play, mark, and manage files.

## Project layout

```text
MediaNest/
├── src/media_nest/
│   ├── core/          # settings, constants, DB connection
│   ├── logs/          # logs
│   ├── models/        # data models
│   ├── repository/    # database access layer
│   ├── service/       # business logic
│   ├── web/           # API + WebSocket routes
│   └── main.py        # FastAPI application entry point
├── static/            # frontend assets
├── run.py             # launch script
└── README.md
```

## Main interface and endpoints

- `/` and `/index` — frontend entry page
- `/media/root` — list configured media roots
- `/media/folder/{path}` — list folder contents
- `/media/image/{path}` — serve an image
- `/media/video/{path}` — serve a video stream
- `/media/thumb/{path}` — serve a thumbnail
- `/media/filter_marked` — list marked media
- `/media/playlist` — save playlist state
- `/media/progress` — save current playback index
- `/media/continue_last_play` — restore the previous playback state
- `/admin/add_root` — add a root directory
- `/admin/delete_root` — remove a root directory
- `/admin/clear_root` — clear all roots
- `/admin/sync` — start a sync job
- `/admin/clear_cache` — clear cached metadata and generated assets
- `/admin/mark` — mark or unmark a file
- `/admin/delete` — delete a file and related artifacts

## Tech Stack

- **Backend Framework**: FastAPI
- **Web Server**: Uvicorn
- **Database**: SQLite (built-in)
- **Image Processing**: Pillow
- **Video Processing**: ffmpeg (ffprobe)
- **Testing Framework**: Pytest
- **Frontend**: HTML / CSS / JavaScript

## Notes

- The app stores local data in SQLite and creates the database on first run.
- Frontend assets are served from the `static/` folder.
- Core configuration is defined in `src/media_nest/core/settings.py`.

---

## 中文

# MediaNest

MediaNest 是一个基于 FastAPI 的本地媒体浏览与播放 Web 应用。它的核心能力包括：浏览本地媒体目录、在浏览器中直接查看图片与视频、保存播放列表状态、记录最后一次播放位置，并通过 SQLite 后端对媒体库进行同步与索引。

## 主要功能

- 文件夹与文件浏览，包含媒体元数据展示
- 自动为图像生成缩略图，支持自定义尺寸
- 图片与视频的 Web 播放
- 播放列表保存/恢复与继续上次播放支持
- 生成 M3U 播放列表，供外部播放器使用
- 后台媒体库同步，并提供同步进度反馈
- 提供 WebSocket 同步进度流
- 控制台日志 + 轮转文件日志

## 核心流程

1. 使用 Python 启动应用：

```bash
python run.py
```

2. 在浏览器打开：

```text
http://localhost:8001
```

3. 通过管理接口添加一个或多个媒体根目录。

4. 执行同步任务，对文件进行扫描、建立数据库索引，并处理媒体任务。

5. 然后在前端页面中浏览、播放、标记和管理媒体。

## 项目结构

```text
MediaNest/
├── src/media_nest/
│   ├── core/          # 设置、常量、数据库连接
│   ├── logs/          # 日志
│   ├── models/        # 数据模型
│   ├── repository/    # 数据库访问层
│   ├── service/       # 业务逻辑
│   ├── web/           # API 与 WebSocket 路由
│   └── main.py        # FastAPI 应用入口
├── static/            # 前端静态资源
├── run.py             # 启动脚本
└── README.md
```

## 主要接口与页面入口

- `/` 与 `/index` — 前端入口页面
- `/media/root` — 获取已配置的媒体根目录
- `/media/folder/{path}` — 获取目录内容
- `/media/image/{path}` — 返回图像内容
- `/media/video/{path}` — 返回视频流
- `/media/thumb/{path}` — 返回缩略图
- `/media/filter_marked` — 获取已标记媒体
- `/media/playlist` — 保存播放列表状态
- `/media/progress` — 保存当前播放索引
- `/media/continue_last_play` — 恢复上一次播放状态
- `/admin/add_root` — 添加媒体根目录
- `/admin/delete_root` — 删除媒体根目录
- `/admin/clear_root` — 清空所有根目录
- `/admin/sync` — 启动同步任务
- `/admin/clear_cache` — 清理缓存与生成文件
- `/admin/mark` — 标记或取消标记文件
- `/admin/delete` — 删除文件及相关附件

## 技术栈

- **后端框架**：FastAPI
- **网络服务器**：Uvicorn
- **数据库**：SQLite（内置）
- **图像处理**：Pillow
- **视频处理**：ffmpeg (ffprobe)
- **测试框架**：Pytest
- **前端**：HTML / CSS / JavaScript

## 说明

- 应用使用 SQLite，本地数据库会在首次运行时自动创建。
- 前端资源位于 `static/` 目录。
- 核心配置文件位于 `src/media_nest/core/settings.py`。
