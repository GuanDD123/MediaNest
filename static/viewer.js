// viewer.js - 媒体查看器 (图片/视频播放、控制、UI自动隐藏)
window.openMedia = function (index, isSilent = false) {
    const state = window.getState();
    state.currentIndex = index;
    const item = state.currentMediaData[state.currentIndex];

    document.body.style.backgroundColor = "#000000";

    state.viewerTitle.textContent = item.name;
    state.markBtn.textContent = item.marked ? "⭐" : "☆";

    state.listView.hidden = true;
    state.viewerView.hidden = false;

    if (state.renderListBeforeSendPlaylist) {
        window.send_playlist(state.currentMediaData);
        state.renderListBeforeSendPlaylist = false;
        state.progressOffset = 0;
    }
    window.send_progress(index + state.progressOffset);

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
        showImage();
    }

    if (isSilent) {
        state.viewerView.classList.add("ui-hidden");
    } else {
        wakeUpUI();
    }
};

function showImage() {
    const state = window.getState();
    const item = state.currentMediaData[state.currentIndex];
    const path = `${encodeURI(item.parent_path)}/${encodeURIComponent(item.name)}`;
    state.image.src = `/media/image${path}`;
    if (state.currentIndex < state.currentMediaData.length - 1) preloadNextImage();
}
function preloadNextImage() {
    const state = window.getState();
    const next = state.currentMediaData[state.currentIndex + 1];
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
    state.viewerView.classList.remove("ui-hidden");
    clearTimeout(state.uiTimer);

    state.uiTimer = setTimeout(() => {
        // 视频暂停时不自动隐藏，以免干扰
        if (state.video.paused && !state.video.hidden) return;
        state.viewerView.classList.add("ui-hidden");
    }, 2000);
}


// 初始化 viewer 相关事件 (由 main.js 调用)
window.initViewerEvents = function () {
    const state = window.getState();

    let isScaling = false;
    let touchStartX = 0;
    let touchStartY = 0;
    state.viewerView.addEventListener("touchstart", (e) => {
        if (e.touches && e.touches.length > 1) {
            isScaling = true;
        } else if (e.touches && e.touches.length === 1) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }
        if (!state.video.hidden && !isScaling) wakeUpUI();
    }, { passive: true });
    state.viewerView.addEventListener("touchend", (e) => {
        if (e.target.closest('#viewerTopBar') || e.target.closest('#viewerBottomBar')) return;

        if (isScaling) {
            if (e.touches.length === 0) { setTimeout(() => isScaling = false, 150); }
            return;
        }

        let moveDistance = 0;
        let endX = 0;
        if (e.changedTouches && e.changedTouches.length > 0) {
            endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            const dx = endX - touchStartX;
            const dy = endY - touchStartY;
            moveDistance = Math.sqrt(dx * dx + dy * dy);
        }
        if (moveDistance > 15) {
            return;
        }

        if (!state.image.hidden) {
            onImageClick(e, endX);
        } else if (!state.video.hidden) {
            if (e.target.closest('#video')) return;

            e.preventDefault();
            const isUIHidden = state.viewerView.classList.contains("ui-hidden");
            if (isUIHidden) {
                wakeUpUI();
            } else {
                state.viewerView.classList.add("ui-hidden");
                clearTimeout(state.uiTimer);
            }
        }
    });

    state.video.addEventListener("mousemove", () => {
        if (!isScaling) wakeUpUI();
    });
    state.video.addEventListener("click", (event) => {
        event.stopPropagation();
        window.togglePlayState();
    });
    state.video.addEventListener("ended", window.nextMedia);

    state.video.addEventListener("loadedmetadata", () => {
        state.progressBar.max = state.video.duration;
        state.timeTotal.textContent = window.formatTime(state.video.duration);
    });
    state.video.addEventListener("timeupdate", () => {
        if (!state.progressBar.matches(':active')) {
            state.progressBar.value = state.video.currentTime;
            state.timeCurrent.textContent = window.formatTime(state.video.currentTime);
        }
    });
    state.progressBar.addEventListener("input", () => {
        state.video.currentTime = state.progressBar.value;
        state.timeCurrent.textContent = window.formatTime(state.video.currentTime);
        wakeUpUI();
    });
};

// 图片点击/触控左右切换
function onImageClick(event, touchEndX = null) {
    const state = window.getState();
    if (event.target.closest('.viewer-actions')) return;

    const isUIHidden = state.viewerView.classList.contains("ui-hidden");

    let x;
    if (touchEndX !== null) {
        x = touchEndX;
    } else {
        x = event.clientX;
    }

    const w = window.innerWidth;

    if (x < w * 0.382) {
        if (state.currentIndex > 0) {
            window.openMedia(state.currentIndex - 1, isUIHidden);
        }
    } else if (x > w * 0.618) {
        if (state.currentIndex < state.currentMediaData.length - 1) {
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

function togglePlayState() {
    const state = window.getState();
    if (state.video.paused) {
        state.video.play();
        wakeUpUI();
    } else {
        state.video.pause();
        wakeUpUI();
    }
};


function prevMedia() {
    const state = window.getState();
    if (state.currentIndex > 0) {
        const isUIHidden = state.viewerView.classList.contains("ui-hidden");
        window.openMedia(state.currentIndex - 1, isUIHidden);
    } else {
        alert("已经是第一个文件了");
    }
};

function nextMedia() {
    const state = window.getState();
    if (state.currentIndex < state.currentMediaData.length - 1) {
        const isUIHidden = state.viewerView.classList.contains("ui-hidden");
        window.openMedia(state.currentIndex + 1, isUIHidden);
    } else {
        window.closeViewer();
    }
};


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


async function deleteCurrentMedia() {
    const state = window.getState();
    const item = state.currentMediaData[state.currentIndex];
    if (!item) return;

    // if (!confirm(`确定要彻底删除文件 "${item.name}" 吗？\n此操作不可恢复！`)) return;

    try {
        if (item.type === "image") {
            const additional_path_list = [item.thumb_path];
        }
        const response = await fetch(`/admin/delete`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: item.id,
                path: `${item.parent_path}/${item.name}`,
                additional_path_list: additional_path_list
            })
        });
        const data = await response.json();

        if (data.success) {
            state.thisViewerDeleteFlag = true;

            state.progressOffset = state.progressOffset + 1;
            state.currentMediaData.splice(state.currentIndex, 1);

            if (state.currentMediaData.length === 0) {
                window.closeViewer();
            } else {
                const nextIndex = state.currentIndex >= state.currentMediaData.length ? state.currentMediaData.length - 1 : state.currentIndex;
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


function closeViewer() {
    const state = window.getState();
    state.viewerView.hidden = true;
    state.listView.hidden = false;

    document.body.style.backgroundColor = "";

    state.image.hidden = true;
    state.image.src = "";

    state.video.hidden = true;
    state.video.pause();
    state.video.currentTime = 0;
    state.video.src = "";

    if (state.thisViewerDeleteFlag) {
        window.renderList();
        state.thisViewerDeleteFlag = false;

        window.send_playlist(state.currentMediaData);
        state.renderListBeforeSendPlaylist = false;

        state.progressOffset = 0;
        window.send_progress(state.currentIndex);
    }
};


async function toggleCurrentMark() {
    const state = window.getState();
    let item = state.currentMediaData[state.currentIndex];
    const newMarkState = !item.marked;

    state.markBtn.textContent = newMarkState ? "⭐" : "☆";

    // 更新 currentMediaData 中的标记状态
    item.marked = newMarkState;

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
        state.markBtn.textContent = item.marked ? "⭐" : "☆";
        alert("标记同步至服务器失败，请检查网络");
    }
};
