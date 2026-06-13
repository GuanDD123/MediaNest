// listManager.js - 目录加载、列表渲染

window.loadFolder = async function (path) {
    window.closeViewer();
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
        state.listView.style.paddingTop = "20px";
    }

    try {
        const response = await fetch(path);
        const data = await response.json();
        state.currentFolderData = data;
        state.fileDeleteNum = 0;
        window.renderList(state.currentFolderData);
    } catch (err) {
        console.error("加载目录失败:", err);
        state.pathRocord.pop();
    }
};

window.renderList = function (data) {
    const state = window.getState();
    const { folderActions, list } = state;
    state.mediaList = [];
    state.mediaMap.clear();
    state.renderListFlag = true;

    const [folderList, mediaList] = data;
    folderActions.style.display = mediaList?.length ? "block" : "none";
    list.innerHTML = "";

    const effectiveMode = state.isRoot ? 'list' : state.viewMode;
    list.className = effectiveMode === "grid" ? "grid-container" : "list-container";

    let columns = [];
    let colHeights = [];
    let colCount = 1;
    const colBaseWidth = 140;
    const gap = 16;  // CSS 中的 .grid-container gap
    let actualColWidth = colBaseWidth;

    if (effectiveMode === "grid") {
        const listWidth = list.clientWidth || window.innerWidth - 40;
        colCount = Math.max(1, Math.floor((listWidth + gap) / (colBaseWidth + gap)));
        state.currentGridColCount = colCount;

        actualColWidth = (listWidth - (colCount - 1) * gap) / colCount;

        for (let i = 0; i < colCount; i++) {
            const col = document.createElement("div");
            col.className = "grid-column";
            columns.push(col);
            colHeights.push(0);
            list.appendChild(col);
        }
    }

    function appendToGrid(el, estHeight) {
        if (effectiveMode === "grid") {
            let minIdx = 0;
            let minH = colHeights[0];
            for (let i = 1; i < colCount; i++) {
                if (colHeights[i] < minH) {
                    minH = colHeights[i];
                    minIdx = i;
                }
            }
            columns[minIdx].appendChild(el);
            colHeights[minIdx] += estHeight;
        } else {
            list.appendChild(el);
        }
    }

    const baseCssOverhead = 32;  // 预估 CSS 额外高度: .grid-item padding(8*2=16) + .grid-column gap(16)

    if (!state.isRoot) {
        const backDiv = document.createElement("div");
        backDiv.className = effectiveMode === "grid" ? "grid-item" : "item";
        backDiv.style.borderLeft = "4px solid #ffd700";

        let estHeight = 60;

        if (effectiveMode === "grid") {
            const thumbWrap = document.createElement("div");
            thumbWrap.className = "grid-thumb-wrap";
            thumbWrap.style.aspectRatio = "1 / 1";
            const img = document.createElement("img");
            img.className = "grid-thumb";
            img.src = `data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" fill="%23ffd700" xmlns="http://www.w3.org/2000/svg"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>`;
            thumbWrap.appendChild(img);
            backDiv.appendChild(thumbWrap);
            estHeight = actualColWidth + baseCssOverhead;
        } else {
            const nameSpan = document.createElement("span");
            nameSpan.className = "item-name";
            nameSpan.textContent = "⬅️ 返回上一页";
            backDiv.appendChild(nameSpan);
        }

        backDiv.onclick = () => {
            state.pathRocord.pop();
            window.loadFolder(state.pathRocord.pop());
        }
        appendToGrid(backDiv, estHeight);
    }

    if (folderList) {
        folderList.forEach(item => {
            const div = document.createElement("div");
            div.className = effectiveMode === "grid" ? "grid-item" : "item";
            let estHeight = 60;

            if (effectiveMode === "grid") {
                const thumbWrap = document.createElement("div");
                thumbWrap.className = "grid-thumb-wrap";
                thumbWrap.style.aspectRatio = "1 / 1";
                const img = document.createElement("img");
                img.className = "grid-thumb";
                img.src = `data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" fill="%23ffd700" xmlns="http://www.w3.org/2000/svg"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>`;
                thumbWrap.appendChild(img);
                div.appendChild(thumbWrap);

                const title = document.createElement("div");
                title.className = "grid-title";
                title.textContent = item.name;
                div.appendChild(title);

                estHeight = actualColWidth + baseCssOverhead + 26;  //thumb包裹器下边距(8) + 标题高度(~18)
            } else {
                const textContainer = document.createElement("div");
                textContainer.className = "item-text-container";

                const nameSpan = document.createElement("div");
                nameSpan.className = "item-name";
                nameSpan.textContent = item.name;
                textContainer.appendChild(nameSpan);

                const subSpan = document.createElement("div");
                subSpan.className = "item-subtitle";
                subSpan.textContent = `${item.parent_path}/${item.name}`;
                textContainer.appendChild(subSpan);

                div.appendChild(textContainer);

                const sizeSpan = document.createElement("span");
                sizeSpan.className = "item-col col-size";
                sizeSpan.textContent = `${item.size} files`;
                div.appendChild(sizeSpan);
            }

            div.onclick = () => {
                const path = `${item.parent_path}/${item.name}`;
                window.loadFolder(`/media/folder${encodeURI(path)}`);
            };

            appendToGrid(div, estHeight);
        });
    }

    if (mediaList) {
        mediaList.forEach(item => {
            const div = document.createElement("div");
            div.className = effectiveMode === "grid" ? "grid-item" : "item";
            let estHeight = 60;

            if (effectiveMode === "grid") {
                const thumbWrap = document.createElement("div");
                thumbWrap.className = "grid-thumb-wrap";

                let ratio = 1;
                if (item.width && item.height) {
                    ratio = item.width / item.height;
                    thumbWrap.style.aspectRatio = `${item.width} / ${item.height}`;
                } else if (item.type === "video") {
                    ratio = 16 / 9;
                    thumbWrap.style.aspectRatio = "16 / 9";
                } else {
                    thumbWrap.style.aspectRatio = "1 / 1";
                }

                estHeight = (actualColWidth / ratio) + baseCssOverhead;

                const img = document.createElement("img");
                img.className = "grid-thumb";
                img.loading = "lazy";

                if (item.type === "video") {
                    img.src = `data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" fill="%23ccbfbf" xmlns="http://www.w3.org/2000/svg"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/></svg>`;
                } else {
                    img.src = `/media/thumb${item.thumb_path}`;
                    img.onerror = () => {
                        img.src = `data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" fill="%23555" xmlns="http://www.w3.org/2000/svg"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>`;
                    };
                }

                thumbWrap.appendChild(img);

                if (item.marked) {
                    const star = document.createElement("span");
                    star.className = "grid-mark";
                    star.textContent = "⭐";
                    thumbWrap.appendChild(star);
                }
                div.appendChild(thumbWrap);
            } else {
                const nameSpan = document.createElement("span");
                nameSpan.className = "item-name";
                if (item.marked) {
                    const star = document.createElement("span");
                    star.className = "item-mark";
                    star.textContent = "⭐";
                    nameSpan.appendChild(star);
                }
                nameSpan.appendChild(document.createTextNode(item.name));
                div.appendChild(nameSpan);

                const sizeSpan = document.createElement("span");
                sizeSpan.className = "item-col col-size";
                sizeSpan.textContent = window.formatSize(item.size);
                div.appendChild(sizeSpan);

                const dimSpan = document.createElement("span");
                dimSpan.className = "item-col col-dim";
                dimSpan.textContent = (item.width && item.height) ? `${item.width} × ${item.height}` : "-";
                div.appendChild(dimSpan);

                const durSpan = document.createElement("span");
                durSpan.className = "item-col col-dur";
                durSpan.textContent = (item.type === "video" && item.duration) ? window.formatDuration(item.duration) : "-";
                div.appendChild(durSpan);
            }

            state.mediaMap.set(`${item.parent_path}/${item.name}`, state.mediaList.length);
            state.mediaList.push(item);

            div.onclick = () => {
                if (state.renderListFlag) {
                    window.send_playlist(state.currentFolderData);
                    window.send_progress(-1);
                    state.renderListFlag = false;
                }
                window.openMedia(state.mediaMap.get(`${item.parent_path}/${item.name}`));
            };

            appendToGrid(div, estHeight);
        });
    }
}
