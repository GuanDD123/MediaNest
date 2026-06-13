// utils.js - 工具函数

window.formatSize = function (bytes) {
    if (bytes === undefined || bytes === null || isNaN(bytes)) return "-";
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

window.formatDuration = function (seconds) {
    if (seconds === undefined || seconds === null || isNaN(seconds)) return "-";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
};

window.formatTime = function (seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
};


window.send_playlist = function (playlist) {
    fetch('/media/playlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(playlist)
    }).catch(err => console.warn("后台播放列表同步失败，忽略:", err));
};
window.send_progress = function (index) {
    fetch('/media/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(index)
    }).catch(err => console.warn("后台进度同步失败，忽略:", err));
};
