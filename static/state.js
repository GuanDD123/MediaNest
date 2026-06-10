// state.js - 全局状态与 DOM 引用
window.AppState = {
    // DOM 元素
    topBar: document.getElementById("topBar"),
    listView: document.getElementById("listView"),
    list: document.getElementById("list"),
    viewerView: document.getElementById("viewerView"),
    viewerBottomBar: document.getElementById("viewerBottomBar"),
    progressBar: document.getElementById("progressBar"),
    timeCurrent: document.getElementById("timeCurrent"),
    timeTotal: document.getElementById("timeTotal"),
    image: document.getElementById("image"),
    video: document.getElementById("video"),
    viewerTopBar: document.getElementById("viewerTopBar"),
    viewerTitle: document.getElementById("viewerTitle"),
    markBtn: document.getElementById("markBtn"),
    closeBtn: document.getElementById("closeBtn"),
    folderActions: document.getElementById("folderActions"),

    // 数据状态
    mediaList: [],          // 当前目录媒体文件列表
    mediaMap: new Map(),    // 路径 -> 索引
    currentIndex: 0,
    currentFolderData: [],  // 原始目录数据（含文件夹）
    uiTimer: null,
};

// 辅助函数，使外部可以访问
window.getState = () => window.AppState;