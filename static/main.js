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

    // 监听窗口大小改变，防抖处理并重新渲染瀑布流
    let resizeTimeout;
    window.addEventListener("resize", () => {
        const state = window.getState();
        // 仅在网格视图且列表可见时触发重新计算
        if (state.viewMode === "grid" && (state.currentFolderData || state.currentMediaData) && !state.listView.hidden) {
            const listWidth = state.list.clientWidth || window.innerWidth - 40;
            // 预估列数 (140为基础宽, 16为gap)
            const newColCount = Math.max(1, Math.floor((listWidth + 16) / (140 + 16)));

            // 只有当列数真的发生改变时，才重新渲染布局，提升性能
            if (newColCount !== state.currentGridColCount) {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {
                    window.renderList();
                }, 200);
            }
        }
    });
})();