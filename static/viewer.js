// viewer.js - 媒体查看器 (图片/视频播放、控制、全屏、UI自动隐藏)

window.closeViewer = function () {
    const state = window.getState();
    state.viewerView.hidden = true;
    state.listView.hidden = false;

    state.image.hidden = true;
    state.image.src = "";

    state.video.hidden = true;
    state.video.pause();
    state.video.currentTime = 0;
    state.video.src = "";
};


window.openMedia = function (index, isSilent = false) {
    const state = window.getState();
    state.currentIndex = index;
    const item = state.mediaList[state.currentIndex];

    state.viewerTitle.textContent = item.name;
    state.markBtn.textContent = item.marked ? "⭐" : "☆";

    state.listView.hidden = true;
    state.viewerView.hidden = false;

    if (item.type === "video") {
        state.image.hidden = true;
        state.viewerBottomBar.hidden = false;
        state.video.hidden = false;
        playVideo(`${encodeURI(item.parent_path)}/${encodeURIComponent(item.name)}`);
    } else if (item.type === "image") {
        state.video.hidden = true;
        state.video.pause();
        state.video.src = "";
        state.video.load();
        state.viewerBottomBar.hidden = true;
        state.image.hidden = false;
        showImage(state.currentIndex);
    }

    if (isSilent) {
        state.viewerView.classList.add("ui-hidden");
    } else {
        wakeUpUI();
    }
};

function showImage(index) {
    const state = window.getState();
    const item = state.mediaList[index];
    const path = `${encodeURI(item.parent_path)}/${encodeURIComponent(item.name)}`;
    state.image.src = `/media/image${path}`;
    if (index < state.mediaList.length - 1) preloadNextImage();
}
function preloadNextImage() {
    const state = window.getState();
    const next = state.mediaList[state.currentIndex + 1];
    if (next?.type === "image") {
        const img = new Image();
        const path = `${encodeURI(next.parent_path)}/${encodeURIComponent(next.name)}`;
        img.src = `/media/image${path}`;
    }
}

function playVideo(path) {
    const state = window.getState();
    state.video.src = `/media/video${path}`;
    state.video.play().catch(e => console.warn("自动播放拦截", e));
}

function wakeUpUI() {
    const state = window.getState();
    const { viewerView, video } = state;
    viewerView.classList.remove("ui-hidden");
    clearTimeout(state.uiTimer);

    state.uiTimer = setTimeout(() => {
        // 视频暂停时不自动隐藏，以免干扰
        if (video.paused && !video.hidden) return;
        viewerView.classList.add("ui-hidden");
    }, 1000);
}


// 初始化 viewer 相关事件 (由 main.js 调用)
window.initViewerEvents = function () {
    const state = window.getState();
    const { viewerView, video, progressBar } = state;

    viewerView.addEventListener("touchstart", (e) => {
        if (!state.video.hidden) wakeUpUI();
    }, { passive: true });
    viewerView.addEventListener("touchend", (e) => {
        if (e.target.closest('#viewerTopBar') || e.target.closest('#viewerBottomBar')) return;

        if (!state.image.hidden) {
            e.preventDefault();
            onImageClick(e);
        } else if (!state.video.hidden) {
            if (e.target.closest('#video')) return;

            e.preventDefault();
            const isUIHidden = viewerView.classList.contains("ui-hidden");
            if (isUIHidden) {
                wakeUpUI();
            } else {
                viewerView.classList.add("ui-hidden");
                clearTimeout(state.uiTimer);
            }
        }
    });

    viewerView.addEventListener("mousemove", wakeUpUI);
    viewerView.addEventListener("click", (e) => {
        if (!state.image.hidden) {
            onImageClick(e);
        } else if (!state.video.hidden) {
            if (e.target.closest('#viewerTopBar') || e.target.closest('#viewerBottomBar') || e.target.closest('#video')) return;
            const isUIHidden = viewerView.classList.contains("ui-hidden");
            if (isUIHidden) wakeUpUI();
            else {
                viewerView.classList.add("ui-hidden");
                clearTimeout(state.uiTimer);
            }
        }
    });

    video.addEventListener("click", (event) => {
        event.stopPropagation();
        window.togglePlayState();
    });
    video.addEventListener("ended", nextMedia);

    video.addEventListener("loadedmetadata", () => {
        progressBar.max = video.duration;
        state.timeTotal.textContent = window.formatTime(video.duration);
    });
    video.addEventListener("timeupdate", () => {
        if (!progressBar.matches(':active')) {
            progressBar.value = video.currentTime;
            state.timeCurrent.textContent = window.formatTime(video.currentTime);
        }
    });
    progressBar.addEventListener("input", () => {
        video.currentTime = progressBar.value;
        state.timeCurrent.textContent = window.formatTime(video.currentTime);
        wakeUpUI();
    });
};

// 图片点击/触控左右切换
function onImageClick(event) {
    const state = window.getState();
    if (event.target.closest('.viewer-actions')) return;

    window.send_progress(state.currentIndex);

    const isUIHidden = state.viewerView.classList.contains("ui-hidden");

    let x;
    if (event.type === 'touchend') {
        x = event.changedTouches[0].clientX;
    } else {
        x = event.clientX;
    }

    const w = window.innerWidth;

    if (x < w * 0.382) {
        if (state.currentIndex > 0) {
            window.openMedia(state.currentIndex - 1, isUIHidden);
        }
    } else if (x > w * 0.618) {
        if (state.currentIndex < state.mediaList.length - 1) {
            window.openMedia(state.currentIndex + 1, isUIHidden);
        }
    } else {
        if (isUIHidden) {
            wakeUpUI();
        } else {
            state.viewerView.classList.add("ui-hidden");
            clearTimeout(state.uiTimer);
        }
    }
}

window.togglePlayState = function () {
    const state = window.getState();
    if (state.video.paused) {
        state.video.play();
        wakeUpUI();
    } else {
        state.video.pause();
        wakeUpUI();
    }
};

function nextMedia() {
    const state = window.getState();
    window.send_progress(state.currentIndex);
    if (state.currentIndex < state.mediaList.length - 1) {
        window.openMedia(state.currentIndex + 1, true);
    } else {
        window.closeViewer();
    }
}


window.prevMedia = function () {
    const state = window.getState();
    if (state.currentIndex > 0) {
        window.send_progress(state.currentIndex);
        const isUIHidden = state.viewerView.classList.contains("ui-hidden");
        window.openMedia(state.currentIndex - 1, isUIHidden);
    } else {
        alert("已经是第一个文件了");
    }
};

window.nextMedia = function () {
    const state = window.getState();
    window.send_progress(state.currentIndex);
    if (state.currentIndex < state.mediaList.length - 1) {
        const isUIHidden = state.viewerView.classList.contains("ui-hidden");
        window.openMedia(state.currentIndex + 1, isUIHidden);
    } else {
        window.closeViewer();
    }
};


window.toggleCustomFullScreen = function () {
    const state = window.getState();
    const isFull = !!(document.fullscreenElement || document.webkitFullscreenElement);
    if (!isFull) {
        const elem = state.viewerView;
        (elem.requestFullscreen || elem.webkitRequestFullscreen)?.call(elem);
    } else {
        (document.exitFullscreen || document.webkitExitFullscreen)?.call(document);
    }
};


window.toggleCurrentMark = async function () {
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
    renderList(state.currentFolderData);

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
        renderList(state.currentFolderData);
        alert("标记同步至服务器失败，请检查网络");
    }
};


window.deleteCurrentMedia = async function () {
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

            state.mediaList.splice(deletedIndex, 1);

            if (state.currentFolderData && state.currentFolderData[1]) {
                const mList = state.currentFolderData[1];
                const idx = mList.findIndex(i => i.parent_path === item.parent_path && i.name === item.name);
                if (idx !== -1) mList.splice(idx, 1);
            }

            renderList(state.currentFolderData);

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