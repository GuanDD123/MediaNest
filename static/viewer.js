// viewer.js - 媒体查看器 (图片/视频播放、控制、UI自动隐藏)

window.closeViewer = function () {
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
        window.renderList(state.currentFolderData);
        state.thisViewerDeleteFlag = false;
    }
};


window.openMedia = function (index, isSilent = false) {
    const state = window.getState();
    state.currentIndex = index;
    const item = state.mediaList[state.currentIndex];

    document.body.style.backgroundColor = "#000000";

    state.viewerTitle.textContent = item.name;
    state.markBtn.textContent = item.marked ? "⭐" : "☆";

    state.listView.hidden = true;
    state.viewerView.hidden = false;

    if (state.renderListFlag) {
        window.send_playlist(state.currentFolderData);
        state.renderListFlag = false;
    }
    window.send_progress(index + state.fileDeleteNum);

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
    }, 2000);
}


// 初始化 viewer 相关事件 (由 main.js 调用)
window.initViewerEvents = function () {
    const state = window.getState();
    const { viewerView, video, progressBar } = state;

    let isScaling = false;
    let touchStartX = 0;
    let touchStartY = 0;
    viewerView.addEventListener("touchstart", (e) => {
        if (e.touches && e.touches.length > 1) {
            isScaling = true;
        } else if (e.touches && e.touches.length === 1) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }
        if (!state.video.hidden && !isScaling) wakeUpUI();
    }, { passive: true });
    viewerView.addEventListener("touchend", (e) => {
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
            const isUIHidden = viewerView.classList.contains("ui-hidden");
            if (isUIHidden) {
                wakeUpUI();
            } else {
                viewerView.classList.add("ui-hidden");
                clearTimeout(state.uiTimer);
            }
        }
    });

    video.addEventListener("mousemove", () => {
        if (!isScaling) wakeUpUI();
    });
    video.addEventListener("click", (event) => {
        event.stopPropagation();
        window.togglePlayState();
    });
    video.addEventListener("ended", window.nextMedia);

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
    if (state.currentIndex < state.mediaList.length - 1) {
        const isUIHidden = state.viewerView.classList.contains("ui-hidden");
        window.openMedia(state.currentIndex + 1, isUIHidden);
    } else {
        window.closeViewer();
    }
};
