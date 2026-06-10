// viewer.js - 媒体查看器 (图片/视频播放、控制、全屏、UI自动隐藏)
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

function preloadNextImage() {
    const state = window.getState();
    const next = state.mediaList[state.currentIndex + 1];
    if (next?.type === "image") {
        const img = new Image();
        img.src = "/media/image" + next.path;
    }
}

function showImage(index) {
    const state = window.getState();
    const item = state.mediaList[index];
    state.image.src = "/media/image" + item.path;
    if (index < state.mediaList.length - 1) preloadNextImage();
}

function playVideo(path) {
    const state = window.getState();
    state.video.src = "/media/video" + path;
    state.video.play().catch(e => console.warn("自动播放拦截", e));
}

window.openMedia = function (index, isSilent = false) {
    const state = window.getState();
    state.currentIndex = index;
    const item = state.mediaList[state.currentIndex];

    state.viewerTitle.textContent = item.name;
    state.markBtn.textContent = item.marked ? "⭐" : "☆";

    state.listView.hidden = true;
    state.viewerView.hidden = false;

    if (item.type === "image") {
        state.video.hidden = true;
        state.video.pause();
        state.viewerBottomBar.hidden = true;
        state.image.hidden = false;
        showImage(state.currentIndex);
    } else if (item.type === "video") {
        state.image.hidden = true;
        state.viewerBottomBar.hidden = false;
        state.video.hidden = false;
        playVideo(item.path);
    }

    if (isSilent) {
        state.viewerView.classList.add("ui-hidden");
    } else {
        wakeUpUI();
    }
};

function nextMedia() {
    const state = window.getState();
    if (state.currentIndex < state.mediaList.length - 1) {
        window.openMedia(state.currentIndex + 1, true);
    } else {
        window.closeViewer();
    }
}

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

window.toggleCustomFullScreen = function () {
    const state = window.getState();
    const isFull = document.fullscreenElement || document.webkitFullscreenElement;
    if (!isFull) {
        const elem = state.viewerView;
        (elem.requestFullscreen || elem.webkitRequestFullscreen)?.call(elem);
    } else {
        (document.exitFullscreen || document.webkitExitFullscreen)?.call(document);
    }
};

// 图片点击左右切换
function onViewerClick(e) {
    const state = window.getState();
    if (state.mediaList[state.currentIndex]?.type === "image" && !e.target.closest('.viewer-actions')) {
        const x = e.clientX;
        const w = window.innerWidth;
        if (x < w * 0.5) {
            if (state.currentIndex > 0) window.openMedia(state.currentIndex - 1);
        } else {
            if (state.currentIndex < state.mediaList.length - 1) window.openMedia(state.currentIndex + 1);
        }
    }
}

// 初始化 viewer 相关事件 (由 main.js 调用)
window.initViewerEvents = function () {
    const state = window.getState();
    const { viewerView, video, progressBar } = state;

    viewerView.addEventListener("mousemove", wakeUpUI);
    viewerView.addEventListener("touchstart", wakeUpUI);
    viewerView.addEventListener("click", onViewerClick);

    video.addEventListener("click", (e) => {
        e.stopPropagation();
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