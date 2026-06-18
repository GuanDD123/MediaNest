# MediaNest

<div align="center">

📺 A media file viewer designed for home LANs

</div>

---

## 📚 Project Description

MediaNest is an open-source media management and playback system built with FastAPI and modern web technologies. It provides a web interface for browsing, managing, and playing multimedia files (images, videos, etc.), with support for playlist management, progress tracking, M3U format export, and more.

## ✨ Features

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

## 🚀 Quick Start

### System Requirements

- **Operating System**: Linux, macOS
- **Python Version**: 3.8 or higher
- **Memory**: Minimum 512MB (recommended 2GB or more)
- **Storage**: Depends on media library size

### Detailed Installation Steps

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

## 📁 Project Structure

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
│       │   ├── db_table_info.py         # Each db table corresponds to one dataclass
│       │   ├── video_segment_info.py # Video segment info
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

## 🔌 Detailed API Documentation

### Media Management (`/media`)

#### 1. Get All Media Root Directories
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

#### 2. Get Folder Contents
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

#### 3. Get Image
```
GET /media/image/{path}
```

#### 4. Get Video
```
GET /media/video/{path}
```

#### 5. Get Thumbnail
```
GET /media/thumb/{path}
```

#### 6. Get Marked Files
```
GET /media/filter_marked
```

#### 7. Save Playlist
```
POST /media/playlist
Content-Type: application/json

{
  "playlist": [[list[dict], list[dict]]]
}
```

#### 8. Save Playback Progress
```
POST /media/progress
Content-Type: application/json

{
  "index": 5
}
```

#### 9. Resume Last Playback
```
GET /media/continue_last_play
```

### Admin (`/admin`)

#### 1. Add Media Root Directory
```
POST /admin/add_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```
**Description:** Add a new media library root directory. The system will scan all media files in that directory.

#### 2. Remove Media Root Directory
```
POST /admin/delete_root
Content-Type: application/json

{
  "path": "/path/to/media"
}
```

#### 3. Clear All Root Directories
```
POST /admin/clear_root
```
**Warning:** This will delete all root directory configurations.

#### 4. Sync Media Library
```
POST /admin/sync
```
**Description:** Scan and index all files in the media library, build cache, and generate thumbnails.

#### 5. Clear Cache
```
POST /admin/clear_cache
```
**Description:** Clear all cached media information and thumbnails.

#### 6. Mark File
```
POST /admin/mark
Content-Type: application/json

{
  "id": 1,
  "marked": true
}
```

#### 7. Delete File
```
POST /admin/delete
Content-Type: application/json

{
  "id": 1,
  "path": "/path/to/file"
}
```
**Warning:** This will permanently delete the file from the file system.

### Playlist (`/playlist`)

#### Generate M3U Playlist
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

## 📊 Database Structure

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

## 💡 Usage Guide

### Basic Workflow

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

### Advanced Configuration

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

## 🐛 FAQ

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

## 🔧 Troubleshooting

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

## 🛠️ Development Guide

### Project Architecture

MediaNest uses a layered architecture:

- **Web Layer** (`web/`) - API routes and request handling
- **Service Layer** (`service/`) - Business logic implementation
- **Repository Layer** (`repository/`) - Data persistence
- **Core Layer** (`core/`) - Core utilities and configuration

### Adding New Media Formats

1. Add file suffix in `constant.py`
2. Create corresponding data model in `models/`
3. Add processing logic in `service/`

### Extending API

Create new route files in `web/` directory and register routes in `main.py`.

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI 0.136.0+
- **Web Server**: Uvicorn 0.49.0+
- **Database**: SQLite (built-in)
- **Image Processing**: Pillow 12.0.0+
- **Testing Framework**: Pytest 9.0.0+
- **Frontend**: HTML5 / CSS3 / JavaScript

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🤝 Contributing

Issues and Pull Requests are welcome!

**Contributing Process:**
1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For questions or suggestions, please contact us via GitHub Issues
