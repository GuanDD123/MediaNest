// listManager.js - 目录加载、列表渲染

window.loadFolder = async function (path) {
    window.closeViewer();
    const state = window.getState();
    state.folderActions.style.display = "none";
    state.list.innerHTML = "";
    state.mediaList = [];
    state.mediaMap.clear();
    state.isRoot = false;

    if (path === "/media/root") {
        state.isRoot = true;
        state.topBar.style.display = "flex";
        state.listView.style.paddingTop = "10px";
    } else {
        state.topBar.style.display = "none";
        state.listView.style.paddingTop = "20px";
    }

    try {
        const response = await fetch(path);
        const data = await response.json();
        state.currentFolderData = data;
        renderList(state.currentFolderData);
    } catch (err) {
        console.error("加载目录失败:", err);
    }
};

function renderList(data) {
    const state = window.getState();
    const { folderActions, list } = state;
    state.mediaList = [];
    state.mediaMap.clear();
    state.renderListFlag = true;

    const [folderList, mediaList] = data;
    folderActions.style.display = mediaList?.length ? "block" : "none";
    list.innerHTML = "";

    list.className = state.viewMode === "grid" ? "grid-container" : "list-container";

    if (!state.isRoot) {
        const backDiv = document.createElement("div");
        backDiv.className = state.viewMode === "grid" ? "grid-item" : "item";
        backDiv.style.borderLeft = "4px solid #ffd700";

        if (state.viewMode === "grid") {
            const thumbWrap = document.createElement("div");
            thumbWrap.className = "grid-thumb-wrap";
            thumbWrap.style.aspectRatio = "1 / 1";
            const img = document.createElement("img");
            img.className = "grid-thumb";
            img.src = `data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" fill="%23ffd700" xmlns="http://www.w3.org/2000/svg"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>`;
            thumbWrap.appendChild(img);
            backDiv.appendChild(thumbWrap);

            const title = document.createElement("div");
            title.className = "grid-title";
            title.textContent = "返回主页";
            backDiv.appendChild(title);
        } else {
            const nameSpan = document.createElement("span");
            nameSpan.className = "item-name";
            nameSpan.textContent = "⬅️ 返回主页";
            backDiv.appendChild(nameSpan);
        }

        backDiv.onclick = () => window.loadFolder("/media/root");
        list.appendChild(backDiv);
    }

    if (folderList) {
        folderList.forEach(item => {
            const div = document.createElement("div");
            div.className = state.viewMode === "grid" ? "grid-item" : "item";

            if (state.viewMode === "grid") {
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

            list.appendChild(div);
        });
    }

    if (mediaList) {
        mediaList.forEach(item => {
            const div = document.createElement("div");
            div.className = state.viewMode === "grid" ? "grid-item" : "item";

            if (state.viewMode === "grid") {
                const thumbWrap = document.createElement("div");
                thumbWrap.className = "grid-thumb-wrap";
                if (item.width && item.height) {
                    thumbWrap.style.aspectRatio = `${item.width} / ${item.height}`;
                } else if (item.type === "video") {
                    thumbWrap.style.aspectRatio = "16 / 9";
                } else {
                    thumbWrap.style.aspectRatio = "1 / 1";
                }
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

                const title = document.createElement("div");
                title.className = "grid-title";
                title.textContent = item.name;
                title.title = item.name;
                div.appendChild(title);

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

            list.appendChild(div);
        });
    }
}
