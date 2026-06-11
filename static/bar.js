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
        .then(data => { Toast.fromResponse(data); })
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
        .then(data => { Toast.fromResponse(data); })
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
        .then(data => { Toast.fromResponse(data); })
        .catch(() => Toast.error());
}


async function continueLastPlay() {
    const state = window.getState();
    const response = await fetch('/media/continue_last_play');
    const [data, index] = await response.json();

    if (data.length) {
        state.currentFolderData = data;
        renderList(state.currentFolderData);
        window.openMedia(index + 1);
    } else {
        alert("No more media files.");
    }
}

async function shufflePlay() {
    const state = window.getState();
    if (!state.mediaList || state.mediaList.length === 0) return;

    if (state.isFiltered) {
        const mediaList = state.currentFolderData[1];
        for (let i = mediaList.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [mediaList[i], mediaList[j]] = [mediaList[j], mediaList[i]];
        }
        renderList(state.currentFolderData);
        window.send_playlist(state.currentFolderData);
        window.send_progress(-1);
        window.openMedia(0);
    } else {
        const folderPath = state.mediaList[0].parent_path;
        await window.loadFolder(`/media/folder${encodeURI(folderPath)}`, true);
        window.send_playlist(state.currentFolderData);
        window.send_progress(-1);
        window.openMedia(0);
    }
}


async function filterMarked() {
    const state = window.getState();
    try {
        const response = await fetch('/media/filter_marked');
        const data = await response.json();

        state.currentFolderData = data;
        state.isFiltered = true;

        state.topBar.style.display = "none";
        state.listView.style.paddingTop = "20px";

        renderList(state.currentFolderData);
    } catch (err) {
        console.error("筛选标记失败:", err);
    }
}
