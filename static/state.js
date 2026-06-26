// state.js - 全局状态与 DOM 引用

window.AppState = {
    // DOM 元素
    topBar: document.getElementById("topBar"),
    listView: document.getElementById("listView"),
    folderActions: document.getElementById("folderActions"),
    list: document.getElementById("list"),
    viewerView: document.getElementById("viewerView"),
    viewerTopBar: document.getElementById("viewerTopBar"),
    viewerTitle: document.getElementById("viewerTitle"),
    markBtn: document.getElementById("markBtn"),
    closeBtn: document.getElementById("closeBtn"),
    image: document.getElementById("image"),
    video: document.getElementById("video"),
    viewerBottomBar: document.getElementById("viewerBottomBar"),
    timeCurrent: document.getElementById("timeCurrent"),
    progressBar: document.getElementById("progressBar"),
    timeTotal: document.getElementById("timeTotal"),

    viewMode: "list",

    // 数据状态
    pathRocord: [],
    isRoot: false,
    currentFolderData: [],
    currentMediaData: [],
    mediaMap: new Map(),    // 路径 -> 索引
    renderListBeforeSendPlaylist: false,
    currentGridColCount: 0,
    currentIndex: 0,
    progressOffset: 0,
    uiTimer: null,
    thisViewerDeleteFlag: false,
};

// 辅助函数，使外部可以访问
window.getState = () => window.AppState;