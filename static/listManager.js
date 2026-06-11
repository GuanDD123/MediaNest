// listManager.js - 目录加载、列表渲染

window.loadFolder = async function (path, shuffleFlag = false) {
    window.closeViewer();
    const state = window.getState();
    state.folderActions.style.display = "none";
    state.list.innerHTML = "";
    state.mediaList = [];
    state.mediaMap.clear();
    state.isFiltered = false;

    if (path === "/media/root") {
        state.topBar.style.display = "flex";
        state.listView.style.paddingTop = "10px";
    } else {
        state.topBar.style.display = "none";
        state.listView.style.paddingTop = "20px";
    }

    try {
        const response = await fetch(`${path}?shuffle_flag=${shuffleFlag}`);
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

    folderList.forEach(item => {
        const div = document.createElement("div");
        div.className = "item";

        const textContainer = document.createElement("div");
        textContainer.className = "item-text-container";

        const nameSpan = document.createElement("span");
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
        sizeSpan.textContent = `${item.size} items`;
        div.appendChild(sizeSpan);

        div.onclick = () => {
            const path = `${item.parent_path}/${item.name}`;
            window.loadFolder(`/media/folder${encodeURI(path)}`);
        };

        list.appendChild(div);
    });

    mediaList.forEach(item => {
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
