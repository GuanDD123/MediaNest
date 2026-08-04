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


let socket = null;
let panel = null;
async function sync() {
    const button = document.getElementById("sync-btn");
    if (button.disabled) {
        return;
    }
    button.disabled = true;

    try {
        const res = await fetch("/admin/sync", {
            method: "POST"
        });
        const data = await res.json();
        if (!data.success) {
            Toast.error(data.message);
        }
        createTaskPanel();
        connectProgress();
    } catch (err) {
        button.disabled = false;
        console.error("请求失败:", err);
        Toast.error("网络错误，无法连接到服务器");
    }
}
function createTaskPanel() {
    if (panel) return;

    panel = document.createElement("div");
    panel.id = "task-panel";
    panel.innerHTML = `
        <div id="task-title">🔄 Syncing</div>
        <div id="task-text"></div>
        <div id="task-progress-bar">
            <div id="task-bar"></div>
        </div>
    `;

    document.body.appendChild(panel);

    taskTitle = panel.querySelector("#task-title");
    taskText = panel.querySelector("#task-text");
    taskProgressBar = panel.querySelector("#task-progress-bar");
    taskBar = panel.querySelector("#task-bar");
}
function connectProgress() {
    socket = new WebSocket(
        `ws://${location.host}/admin/sync/progress`
    );

    socket.onmessage = (event) => {
        const progress = JSON.parse(event.data);
        updateProgress(progress);
    };

    socket.onclose = () => {
        socket = null;
    };

    socket.onerror = () => {
        if (panel) finishTask("❌ 进度连接错误", false);
    }
}
function updateProgress(progress) {
    let title;
    let percent = 0;
    let text;

    if (progress.current_step === "Scan Library") {
        if (progress.status === "failed") {
            finishTask("❌ 扫描失败", false);
            return;
        }

        title = "🔄 Scan Library";
        text = `
            Root Folder：${progress.completed_root_folders_num} / ${progress.root_folders_num}<br>
            Current：${progress.current_root_folder}<br>
            Completed Scan：${progress.completed_scan_num}
            `;
        percent = progress.root_folders_num === 0 ? 0 : (progress.completed_root_folders_num / progress.root_folders_num) * 100;
    } else if (progress.current_step === "Deal Task") {
        if (progress.status === "failed") {
            finishTask("❌ 处理失败", false);
            return;
        }

        if (progress.status === "finished") {
            if (progress.failed_task_num > 0) {
                finishTask("⚠️ 同步完成（部分失败）", `Failed Tasks：${progress.failed_task_num}`);
            } else {
                finishTask("✅ 同步完成");
            }
            document.getElementById("sync-btn").disabled = false;
            return;
        }

        title = "⚙️ Deal Task";
        const completed = progress.successed_task_num + progress.failed_task_num;
        text = `
            Deal Task：${completed} / ${progress.task_num}<br>
            Successed：${progress.successed_task_num}<br>
            Failed：${progress.failed_task_num}
            `;
        percent = progress.task_num === 0 ? 0 : (completed / progress.task_num) * 100;
    }

    taskTitle.textContent = title;
    taskText.innerHTML = text;
    taskBar.style.width = percent + "%";
}
function finishTask(title, text = null) {
    taskTitle.textContent = title;
    if (text) {
        taskText.innerHTML = text;
    }
    else {
        taskText.remove();
    }
    taskProgressBar.remove();
    window.loadFolder("/media/root");

    setTimeout(() => {
        panel.remove();
        panel = null;
    }, 2000);
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
    state.list.innerHTML = "";
    state.mediaMap.clear();

    const response = await fetch("/media/continue_last_play");
    const [mediaData, index] = await response.json();

    if (mediaData.length) {
        state.pathRecord.push("/media/continue_last_play");

        state.isRoot = false;
        state.topBarRootFolder.style.display = "none";
        state.topBarSubFolder.style.display = "flex";

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
    const btns = document.querySelectorAll(".view-mode-btn");
    btns.forEach(btn => {
        if (mode === "list") {
            btn.innerHTML = "📋";
            btn.title = "切换为网格视图";
        } else {
            btn.innerHTML = "🔲";
            btn.title = "切换为列表视图";
        }
    });
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


function backUpper() {
    const state = window.getState();
    if (state.pathRecord.length > 1) {
        state.pathRecord.pop();
        window.loadFolder(state.pathRecord.pop());
    }
}
