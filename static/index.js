const topBar = document.getElementById("topBar");
const listView = document.getElementById("listView");
const list = document.getElementById("list");
const viewerView = document.getElementById("viewerView");
const image = document.getElementById("image");
const video = document.getElementById("video");
const closeBtn = document.getElementById("closeBtn");

let mediaList = [];
let mediaMap = new Map();
let currentIndex = 0;
let currentFolderData = [];
let mouseTimer = null;
let isAutoSwitching = false;

loadFolder("/media/root");

async function loadFolder(path) {
    closeViewer();
    list.innerHTML = "";
    mediaList = [];
    mediaMap.clear();
    document.getElementById("folderActions").style.display = "none";

    if (path === "/media/root") {
        topBar.style.display = "flex";
        listView.style.paddingTop = "10px";
    } else {
        topBar.style.display = "none";
        listView.style.paddingTop = "20px";
    }

    try {
        const response = await fetch(path);
        const data = await response.json();

        currentFolderData = data;
        renderList(currentFolderData);
    } catch (err) {
        console.error("加载目录失败:", err);
    }
}
function renderList(data) {
    list.innerHTML = "";
    mediaList = [];
    mediaMap.clear();

    const hasMedia = data.some(item => item.type !== "folder");
    document.getElementById("folderActions").style.display = hasMedia ? "block" : "none";

    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "item";

        const nameSpan = document.createElement("span");
        nameSpan.className = "item-name";
        nameSpan.textContent = item.type === "folder" ? item.name + " (" + decodeURIComponent(item.path) + ")" : item.name;
        div.appendChild(nameSpan);

        const sizeSpan = document.createElement("span");
        sizeSpan.className = "item-col col-size";
        sizeSpan.textContent = item.type === "folder" ? "Folder (" + item.size + " items )" : formatSize(item.size);
        div.appendChild(sizeSpan);

        const dimSpan = document.createElement("span");
        dimSpan.className = "item-col col-dim";
        dimSpan.textContent = (item.type !== "folder" && item.width && item.height) ? `${item.width} × ${item.height}` : "-";
        div.appendChild(dimSpan);

        const durSpan = document.createElement("span");
        durSpan.className = "item-col col-dur";
        durSpan.textContent = (item.type === "video" && item.duration) ? formatDuration(item.duration) : "-";
        div.appendChild(durSpan);

        if (item.type !== "folder") {
            mediaMap.set(item.path, mediaList.length);
            mediaList.push(item);
        }

        div.onclick = () => {
            if (item.type === "folder") {
                loadFolder("/media/folder" + item.path);
            } else {
                openMedia(mediaMap.get(item.path));
            }
        }

        list.appendChild(div);
    });
}

function formatSize(bytes) {
    if (bytes === undefined || bytes === null || isNaN(bytes)) return "-";
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}
function formatDuration(seconds) {
    if (seconds === undefined || seconds === null || isNaN(seconds)) return "-";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function shufflePlay() {
    if (currentFolderData.length === 0) return;

    const folders = currentFolderData.filter(item => item.type === "folder");
    const medias = currentFolderData.filter(item => item.type !== "folder");

    if (medias.length === 0) return;

    for (let i = medias.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [medias[i], medias[j]] = [medias[j], medias[i]];
    }

    currentFolderData = [...folders, ...medias];

    renderList(currentFolderData);

    openMedia(0);
}


function setViewerUiVisible(visible) {
    if (visible) {
        closeBtn.style.opacity = "1";
        closeBtn.style.pointerEvents = "auto";
        viewerView.classList.remove("hide-cursor");
        if (mediaList[currentIndex]?.type === "video") {
            video.controls = true;
        }
    } else {
        if (!viewerView.hidden) {
            closeBtn.style.opacity = "0";
            closeBtn.style.pointerEvents = "none";
            viewerView.classList.add("hide-cursor");
            video.controls = false;
        }
    }
}

viewerView.addEventListener("mousemove", () => {
    if (isAutoSwitching || viewerView.hidden) return;

    setViewerUiVisible(true);

    clearTimeout(mouseTimer);
    mouseTimer = setTimeout(() => {
        setViewerUiVisible(false);
    }, 1000);
});


function openMedia(index, isSilent = false) {
    currentIndex = index;
    const item = mediaList[currentIndex];

    listView.hidden = true;
    viewerView.hidden = false;

    if (item.type === "image") {
        video.hidden = true;
        video.pause();
        video.controls = false;
        image.hidden = false;
        showImage(currentIndex);
    } else if (item.type === "video") {
        image.hidden = true;
        video.hidden = false;
        playVideo(item.path);
    }

    if (isSilent) {
        setViewerUiVisible(false);
    } else {
        setViewerUiVisible(true);
        clearTimeout(mouseTimer);
        mouseTimer = setTimeout(() => setViewerUiVisible(false), 1000);
    }
}

function showImage(index) {
    const item = mediaList[index];
    image.src = "/media/image" + item.path;
    if (index < mediaList.length - 1) { preloadNextImage(); }
}
function preloadNextImage() {
    const next = mediaList[currentIndex + 1];
    if (next?.type === "image") {
        const img = new Image();
        img.src = "/media/image" + next.path;
    }
}

function playVideo(path) {
    video.src = "/media/video" + path;
    video.onloadeddata = () => {
        video.play().catch(err => console.warn("自动播放被拦截:", err));
    };
}
video.addEventListener("ended", () => {
    if (currentIndex < mediaList.length - 1) {
        openMedia(currentIndex + 1);
    } else {
        closeViewer();
    }
});


viewerView.addEventListener("click", onViewerClick);
function onViewerClick(e) {
    if (mediaList[currentIndex]?.type === "image" && e.target !== document.getElementById('closeBtn')) {
        const x = e.clientX;
        const w = window.innerWidth;
        if (x < w * 0.5) { prevImage(); }
        else { nextImage(); }
    }
}
function prevImage() {
    if (currentIndex > 0) { openMedia(currentIndex - 1); }
}
function nextImage() {
    if (currentIndex < mediaList.length - 1) { openMedia(currentIndex + 1); }
}

video.addEventListener("ended", () => {
    if (currentIndex < mediaList.length - 1) {
        isAutoSwitching = true;

        openMedia(currentIndex + 1, true);

        setTimeout(() => {
            isAutoSwitching = false;
        }, 300);
    } else {
        closeViewer();
    }
});


function closeViewer() {
    viewerView.hidden = true;
    listView.hidden = false;

    image.hidden = true;
    image.src = "";

    video.hidden = true;
    video.pause();
    video.currentTime = 0;
    video.src = "";
}
