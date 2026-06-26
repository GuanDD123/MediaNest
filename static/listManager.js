// listManager.js - 目录加载、列表渲染与视图管理

// UI 渲染
const DOMBuilder = {
    baseCssOverhead: 32, // CSS 额外消耗: .grid-item padding(8*2=16) + .grid-column gap(16)

    createBackBtn(effectiveMode, actualColWidth, onClick) {
        const div = document.createElement("div");
        div.className = effectiveMode === "grid" ? "grid-item" : "item";
        div.style.borderLeft = "4px solid #ffd700";
        let estHeight = 60;

        if (effectiveMode === "grid") {
            const thumbWrap = document.createElement("div");
            thumbWrap.className = "grid-thumb-wrap";
            thumbWrap.style.aspectRatio = "1 / 1";
            thumbWrap.innerHTML = `<img class="grid-thumb" src="data:image/svg+xml;utf8,<svg viewBox='0 0 24 24' fill='%23ffd700' xmlns='http://www.w3.org/2000/svg'><path d='M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z'/></svg>">`;
            div.appendChild(thumbWrap);
            estHeight = actualColWidth + this.baseCssOverhead;
        } else {
            div.innerHTML = `<span class="item-name">⬅️ 返回上一页</span>`;
        }

        div.onclick = onClick;
        return { el: div, estHeight };
    },

    createFolder(item, effectiveMode, actualColWidth, onClick) {
        const div = document.createElement("div");
        div.className = effectiveMode === "grid" ? "grid-item" : "item";
        let estHeight = 60;

        if (effectiveMode === "grid") {
            const thumbWrap = document.createElement("div");
            thumbWrap.className = "grid-thumb-wrap";
            thumbWrap.style.aspectRatio = "1 / 1";
            thumbWrap.innerHTML = `<img class="grid-thumb" src="data:image/svg+xml;utf8,<svg viewBox='0 0 24 24' fill='%23ffd700' xmlns='http://www.w3.org/2000/svg'><path d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/></svg>">`;
            div.appendChild(thumbWrap);

            const title = document.createElement("div");
            title.className = "grid-title";
            title.textContent = item.name;
            div.appendChild(title);

            estHeight = actualColWidth + this.baseCssOverhead + 26; // 缩略图 + 标题空间
        } else {
            div.innerHTML = `
                <div class="item-text-container">
                    <div class="item-name">${item.name}</div>
                    <div class="item-subtitle">${item.parent_path}/${item.name}</div>
                </div>
                <span class="item-col col-size">${item.size} files</span>
            `;
        }

        div.onclick = onClick;
        return { el: div, estHeight };
    },

    createMedia(item, effectiveMode, actualColWidth, onClick) {
        const div = document.createElement("div");
        div.className = effectiveMode === "grid" ? "grid-item" : "item";
        let estHeight = 60;

        if (effectiveMode === "grid") {
            const thumbWrap = document.createElement("div");
            thumbWrap.className = "grid-thumb-wrap";

            let ratio = (item.width && item.height) ? (item.width / item.height) : (item.type === "video" ? 16 / 9 : 1);
            thumbWrap.style.aspectRatio = `${ratio}`;
            estHeight = (actualColWidth / ratio) + this.baseCssOverhead;

            const img = document.createElement("img");
            img.className = "grid-thumb";
            img.loading = "lazy";

            if (item.type === "video") {
                img.src = `data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" fill="%23ccbfbf" xmlns="http://www.w3.org/2000/svg"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/></svg>`;
            } else {
                img.src = `/media/thumb${item.thumb_path}`;
                img.onerror = () => img.src = `data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" fill="%23555" xmlns="http://www.w3.org/2000/svg"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>`;
            }
            thumbWrap.appendChild(img);

            if (item.marked) {
                thumbWrap.innerHTML += `<span class="grid-mark">⭐</span>`;
            }
            div.appendChild(thumbWrap);
        } else {
            const markHtml = item.marked ? `<span class="item-mark">⭐</span>` : "";
            const dimStr = (item.width && item.height) ? `${item.width} × ${item.height}` : "-";
            const durStr = (item.type === "video" && item.duration) ? window.formatDuration(item.duration) : "-";

            div.innerHTML = `
                <span class="item-name">${markHtml}${item.name}</span>
                <span class="item-col col-size">${window.formatSize(item.size)}</span>
                <span class="item-col col-dim">${dimStr}</span>
                <span class="item-col col-dur">${durStr}</span>
            `;
        }

        div.onclick = onClick;
        return { el: div, estHeight };
    }
};

// 瀑布流布局管理器
class MasonryLayout {
    constructor(container, effectiveMode) {
        this.container = container;
        this.effectiveMode = effectiveMode;
        this.columns = [];
        this.colHeights = [];
        this.colBaseWidth = 140;
        this.gap = 16;  // CSS 中的 .grid-container gap
        this.actualColWidth = this.colBaseWidth;

        if (effectiveMode === "grid") {
            const listWidth = container.clientWidth || window.innerWidth - 40;
            this.colCount = Math.max(1, Math.floor((listWidth + this.gap) / (this.colBaseWidth + this.gap)));
            this.actualColWidth = (listWidth - (this.colCount - 1) * this.gap) / this.colCount;

            // 初始化 DOM 列
            for (let i = 0; i < this.colCount; i++) {
                const col = document.createElement("div");
                col.className = "grid-column";
                this.columns.push(col);
                this.colHeights.push(0);
                this.container.appendChild(col);
            }
        }
    }

    append(el, estHeight) {
        if (this.effectiveMode === "grid") {
            let minIdx = 0;
            let minH = this.colHeights[0];
            for (let i = 1; i < this.colCount; i++) {
                if (this.colHeights[i] < minH) {
                    minH = this.colHeights[i];
                    minIdx = i;
                }
            }
            this.columns[minIdx].appendChild(el);
            this.colHeights[minIdx] += estHeight;
        } else {
            this.container.appendChild(el);
        }
    }
}


// 加载与协调渲染
window.loadFolder = async function (path) {
    const state = window.getState();
    state.pathRocord.push(path);
    state.folderActions.style.display = "none";
    state.list.innerHTML = "";
    state.mediaList = [];
    state.mediaMap.clear();

    if (path === "/media/root") {
        state.isRoot = true;
        state.topBar.style.display = "flex";
        state.listView.style.paddingTop = "10px";
    } else {
        state.isRoot = false;
        state.topBar.style.display = "none";
        state.listView.style.paddingTop = "calc(20px + env(safe-area-inset-top, 0px))";
    }

    try {
        const response = await fetch(path);
        const data = await response.json();
        state.currentFolderData = data;
        window.renderList(state.currentFolderData);
        state.fileDeleteNum = 0;
    } catch (err) {
        console.error("加载目录失败:", err);
        state.pathRocord.pop();
    }
};

window.renderList = function (data) {
    const state = window.getState();
    const { folderActions, list } = state;

    // 重置全局索引
    state.mediaList = [];
    state.mediaMap.clear();
    state.renderListFlag = true;

    const [folderList = [], mediaList = []] = data;
    folderActions.style.display = mediaList.length ? "block" : "none";
    list.innerHTML = "";

    const effectiveMode = state.isRoot ? 'list' : state.viewMode;

    // 检测是否需要执行 Root 界面分组
    const uniquePaths = [...new Set([...folderList, ...mediaList].map(item => item.parent_path).filter(Boolean))];
    const shouldGroup = state.isRoot && uniquePaths.length > 1;

    if (!shouldGroup) {
        // --- 纯平铺模式 ---
        list.className = effectiveMode === "grid" ? "grid-container" : "list-container";
        renderSubTask(folderList, mediaList, list, effectiveMode, state);
        if (effectiveMode === "grid") state.currentGridColCount = list.children.length; // 更新自适应状态
    } else {
        // --- 折叠分组模式 ---
        list.className = "grouped-container";

        uniquePaths.forEach(path => {
            const groupFolders = folderList.filter(item => item.parent_path === path);
            const groupMedia = mediaList.filter(item => item.parent_path === path);
            if (groupFolders.length === 0 && groupMedia.length === 0) return;

            // 构建外壳
            const groupWrapper = document.createElement("div");
            groupWrapper.className = "group-wrapper";

            const header = document.createElement("div");
            header.className = "group-header"; // 默认展开
            header.innerHTML = `
                <span class="group-arrow">▼</span>
                <span class="group-title">${path}</span>
                <span class="group-count">(${groupFolders.length + groupMedia.length})</span>
            `;

            const contentContainer = document.createElement("div");
            contentContainer.className = effectiveMode === "grid" ? "grid-container" : "list-container";
            contentContainer.style.display = effectiveMode === "grid" ? "flex" : "block";

            // 折叠控制逻辑
            let isCollapsed = false;
            header.onclick = (e) => {
                e.preventDefault();
                isCollapsed = !isCollapsed;
                contentContainer.style.display = isCollapsed ? "none" : (effectiveMode === "grid" ? "flex" : "block");
                header.querySelector(".group-arrow").textContent = isCollapsed ? "▶" : "▼";
                header.classList.toggle("collapsed", isCollapsed);
            };

            groupWrapper.appendChild(header);
            groupWrapper.appendChild(contentContainer);
            list.appendChild(groupWrapper);

            // 渲染组内内容
            renderSubTask(groupFolders, groupMedia, contentContainer, effectiveMode, state);
        });
    }
};

// 辅助渲染协调器：把数据送进工场加工，然后丢给布局器排版
function renderSubTask(folders, media, container, effectiveMode, state) {
    const layout = new MasonryLayout(container, effectiveMode);

    // 1. 返回按钮
    if (!state.isRoot) {
        const { el, estHeight } = DOMBuilder.createBackBtn(effectiveMode, layout.actualColWidth, () => {
            state.pathRocord.pop();
            window.loadFolder(state.pathRocord.pop());
        });
        layout.append(el, estHeight);
    }

    // 2. 文件夹
    folders.forEach(item => {
        const { el, estHeight } = DOMBuilder.createFolder(item, effectiveMode, layout.actualColWidth, () => {
            window.loadFolder(`/media/folder${encodeURI(`${item.parent_path}/${item.name}`)}`);
        });
        layout.append(el, estHeight);
    });

    // 3. 媒体文件
    media.forEach(item => {
        const { el, estHeight } = DOMBuilder.createMedia(item, effectiveMode, layout.actualColWidth, () => {
            window.openMedia(state.mediaMap.get(`${item.parent_path}/${item.name}`));
        });

        // 推入全局状态，打通分组界限，保证图片浏览器的左右顺滑切换
        state.mediaMap.set(`${item.parent_path}/${item.name}`, state.mediaList.length);
        state.mediaList.push(item);

        layout.append(el, estHeight);
    });
}