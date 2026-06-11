// main.js - 初始化入口

(function () {
    // 初始化全局事件
    window.initViewerEvents();

    // 加载默认根目录
    window.loadFolder("/media/root");

    // 可选: 处理全局未捕获的错误友好提示
    window.addEventListener("error", (e) => {
        console.error("运行时错误:", e.error);
    });
})();