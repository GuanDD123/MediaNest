// listManager.js - 目录加载、列表渲染、随机播放
function renderList(data) {
    const state = window.getState();
    const { list, folderActions, mediaMap, mediaList } = state;
    list.innerHTML = "";
    // 重置媒体列表
    state.mediaList = [];
    state.mediaMap.clear();

    const hasMedia = data.some(item => item.type !== "folder");
    folderActions.style.display = hasMedia ? "block" : "none";

    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "item";

        const nameSpan = document.createElement("span");
        nameSpan.className = "item-name";

        if (item.marked) {
            const star = document.createElement("span");
            star.className = "item-mark";
            star.textContent = "⭐";
            nameSpan.appendChild(star);
        }
        const displayName = item.type === "folder" ? `${item.name} (${decodeURIComponent(item.path)})` : item.name;
        nameSpan.appendChild(document.createTextNode(displayName));
        div.appendChild(nameSpan);

        const sizeSpan = document.createElement("span");
        sizeSpan.className = "item-col col-size";
        sizeSpan.textContent = item.type === "folder" ? `Folder (${item.size} items)` : window.formatSize(item.size);
        div.appendChild(sizeSpan);

        const dimSpan = document.createElement("span");
        dimSpan.className = "item-col col-dim";
        dimSpan.textContent = (item.type !== "folder" && item.width && item.height) ? `${item.width} × ${item.height}` : "-";
        div.appendChild(dimSpan);

        const durSpan = document.createElement("span");
        durSpan.className = "item-col col-dur";
        durSpan.textContent = (item.type === "video" && item.duration) ? window.formatDuration(item.duration) : "-";
        div.appendChild(durSpan);

        if (item.type !== "folder") {
            state.mediaMap.set(item.path, state.mediaList.length);
            state.mediaList.push(item);
        }

        div.onclick = () => {
            if (item.type === "folder") {
                window.loadFolder("/media/folder" + item.path);
            } else {
                window.openMedia(state.mediaMap.get(item.path));
            }
        };

        list.appendChild(div);
    });
}

window.loadFolder = async function (path) {
    window.closeViewer();
    const state = window.getState();
    state.list.innerHTML = "";
    state.mediaList = [];
    state.mediaMap.clear();
    state.folderActions.style.display = "none";

    if (path === "/media/root") {
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

window.shufflePlay = function () {
    const state = window.getState();
    if (state.currentFolderData.length === 0) return;

    const folders = state.currentFolderData.filter(item => item.type === "folder");
    const medias = state.currentFolderData.filter(item => item.type !== "folder");

    if (medias.length === 0) return;

    // Fisher-Yates 随机打乱媒体顺序
    for (let i = medias.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [medias[i], medias[j]] = [medias[j], medias[i]];
    }

    state.currentFolderData = [...folders, ...medias];
    renderList(state.currentFolderData);
    window.openMedia(0);
};