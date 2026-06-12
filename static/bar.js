const Toast = {
    success(msg) { alert(msg || "OK"); },
    error(msg) { alert(msg || "Failed"); },
    fromResponse(data) {
        if (data.success) {
            this.success(data.msg);
        } else {
            this.error(data.msg);
        }
    }
};


function sync() {
    fetch("/admin/sync", {
        method: "POST"
    })
        .then(res => res.json())
        .then(data => Toast.fromResponse(data))
        .catch(() => Toast.error());
}


function addRoot() {
    const path = prompt("请输入新增根目录路径:");
    if (!path) return;

    fetch("/admin/add_root", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(path)
    })
        .then(res => res.json())
        .then(data => Toast.fromResponse(data))
        .catch(() => Toast.error());
}

function deleteRoot() {
    const path = prompt("请输入要删除的根目录路径:");
    if (!path) return;

    fetch("/admin/delete_root", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(path)
    })
        .then(res => res.json())
        .then(data => Toast.fromResponse(data))
        .catch(() => Toast.error());
}


async function continueLastPlay() {
    const state = window.getState();
    const response = await fetch('/media/continue_last_play');
    const [data, index] = await response.json();

    if (data.length) {
        state.currentFolderData = data;
        window.renderList(state.currentFolderData);
        window.openMedia(index + 1);
    } else {
        alert("No more media files.");
    }
}


async function filterMarked() {
    const state = window.getState();
    try {
        const response = await fetch('/media/filter_marked');
        const data = await response.json();

        state.currentFolderData = data;
        state.isRoot = false

        state.topBar.style.display = "none";
        state.listView.style.paddingTop = "20px";

        window.renderList(state.currentFolderData);
    } catch (err) {
        console.error("筛选标记失败:", err);
    }
}


function toggleViewMode() {
    const state = window.getState();
    state.viewMode = state.viewMode === "list" ? "grid" : "list";
    updateViewModeButtonIcon(state.viewMode);

    if (!state.isRoot && state.currentFolderData && state.currentFolderData.length > 0) {
        window.renderList(state.currentFolderData);
    }
}
function updateViewModeButtonIcon(mode) {
    const btn = document.querySelector('#rightTopBar button:last-child'); // 假设按钮位置固定
    if (!btn) return;
    if (mode === 'list') {
        btn.innerHTML = '📋';
        btn.title = '切换为网格视图';
    } else {
        btn.innerHTML = '🔲';
        btn.title = '切换为列表视图';
    }
}


function shufflePlay() {
    const state = window.getState();

    if (!state.currentFolderData || !state.currentFolderData[1] || state.currentFolderData[1].length === 0) {
        return;
    }

    state.currentFolderData[1].sort(() => Math.random() - 0.5);
    window.renderList(state.currentFolderData);
    window.send_playlist(state.currentFolderData);
    window.send_progress(-1);
    window.openMedia(0);
}


function toggleCustomFullScreen() {
    const state = window.getState();
    const isFull = !!(document.fullscreenElement || document.webkitFullscreenElement);
    if (!isFull) {
        const elem = state.viewerView;
        (elem.requestFullscreen || elem.webkitRequestFullscreen)?.call(elem);
    } else {
        (document.exitFullscreen || document.webkitExitFullscreen)?.call(document);
    }
};


async function toggleCurrentMark() {
    const state = window.getState();
    const item = state.mediaList[state.currentIndex];
    const newMarkState = !item.marked;

    state.markBtn.textContent = newMarkState ? "⭐" : "☆";

    // 更新 currentFolderData、mediaList 中的标记状态
    const mList = state.currentFolderData[1];
    const idx = mList.findIndex(i => i.parent_path === item.parent_path && i.name === item.name);
    if (idx !== -1) mList[idx].marked = newMarkState;
    item.marked = newMarkState;

    // 重新渲染列表以更新星标显示
    window.renderList(state.currentFolderData);

    try {
        const res = await fetch("/admin/mark", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: item.id, marked: newMarkState })
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.msg || "标记失败");
    } catch (err) {
        console.error("标记同步失败:", err);
        // 回滚状态
        item.marked = !newMarkState;
        if (folderItem) folderItem.marked = !newMarkState;
        state.markBtn.textContent = item.marked ? "⭐" : "☆";
        window.renderList(state.currentFolderData);
        alert("标记同步至服务器失败，请检查网络");
    }
};


async function deleteCurrentMedia() {
    const state = window.getState();
    const item = state.mediaList[state.currentIndex];
    if (!item) return;

    // if (!confirm(`确定要彻底删除文件 "${item.name}" 吗？\n此操作不可恢复！`)) return;

    try {
        const response = await fetch(`/admin/delete`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: item.id,
                path: `${item.parent_path}/${item.name}`
            })
        });
        const data = await response.json();

        if (data.success) {
            const deletedIndex = state.currentIndex;

            state.fileDeleteNum = state.fileDeleteNum + 1
            state.mediaList.splice(deletedIndex, 1);

            if (state.currentFolderData && state.currentFolderData[1]) {
                const mList = state.currentFolderData[1];
                const idx = mList.findIndex(i => i.parent_path === item.parent_path && i.name === item.name);
                if (idx !== -1) mList.splice(idx, 1);
            }

            window.renderList(state.currentFolderData);

            if (state.mediaList.length === 0) {
                window.closeViewer();
            } else {
                const nextIndex = deletedIndex >= state.mediaList.length ? state.mediaList.length - 1 : deletedIndex;
                const isUIHidden = state.viewerView.classList.contains("ui-hidden");
                window.openMedia(nextIndex, isUIHidden);
            }
        } else {
            alert(data.msg || "删除失败");
        }
    } catch (err) {
        console.error("删除文件请求失败:", err);
        alert("网络错误，无法连接到服务器");
    }
};