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


async function sync() {
    try {
        const res = await fetch("/admin/sync", {
            method: "POST"
        });
        const data = await res.json();
        Toast.fromResponse(data);
        window.loadFolder("/media/root");
    } catch (err) {
        console.error("请求失败:", err);
        Toast.error("网络错误，无法连接到服务器");
    }
}


async function addRoot() {
    const path = prompt("请输入新增根目录路径:");
    if (!path) return;

    try {
        const res = await fetch("/admin/add_root", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(path)
        });
        const data = await res.json();
        Toast.fromResponse(data);
        window.loadFolder("/media/root");
    } catch (err) {
        console.error("请求失败:", err);
        Toast.error("网络错误，无法连接到服务器");
    }
}

async function deleteRoot() {
    const path = prompt("请输入要删除的根目录路径:");
    if (!path) return;

    try {
        const res = await fetch("/admin/delete_root", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(path)
        });
        const data = await res.json();
        Toast.fromResponse(data);
        window.loadFolder("/media/root");
    } catch (err) {
        console.error("请求失败:", err);
        Toast.error("网络错误，无法连接到服务器");
    }
}


async function continueLastPlay() {
    const state = window.getState();
    const response = await fetch("/media/continue_last_play");
    const [mediaData, index] = await response.json();

    if (mediaData.length) {
        state.pathRocord.push("/media/continue_last_play");
        state.isRoot = false;
        state.currentFolderData = [];
        state.currentMediaData = mediaData;
        window.renderList();
        window.openMedia(index);
    } else {
        alert("No more media files.");
    }
}


async function filterMarked() {
    window.loadFolder("/media/filter_marked")
}


function toggleViewMode() {
    const state = window.getState();
    state.viewMode = state.viewMode === "list" ? "grid" : "list";
    updateViewModeButtonIcon(state.viewMode);

    if (!state.isRoot && (state.currentFolderData || state.currentMediaData) && (state.currentFolderData.length > 0 || state.currentMediaData.length > 0)) {
        window.renderList();
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

    if (!state.currentMediaData || state.currentMediaData.length === 0) {
        return;
    }

    state.currentMediaData.sort(() => Math.random() - 0.5);
    window.renderList();
    window.openMedia(0);
}
