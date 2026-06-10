const listView = document.getElementById("listView");
const list = document.getElementById("list");
const viewerView = document.getElementById("viewerView");
const image = document.getElementById("image");
const video = document.getElementById("video");

let mediaList = [];
let mediaMap = new Map();
let currentIndex = 0;

loadFolder("/media/root");

async function loadFolder(path) {
    closeViewer();
    list.innerHTML = "";
    mediaList = [];
    mediaMap.clear();

    try {
        const response = await fetch(path);
        const data = await response.json();

        data.forEach(item => {
            const div = document.createElement("div");
            div.className = "item";
            div.textContent = item.name;

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
    } catch (err) {
        console.error("加载目录失败:", err);
    }
}

function openMedia(index) {
    currentIndex = index;
    const item = mediaList[currentIndex];

    listView.hidden = true;
    viewerView.hidden = false;

    if (item.type === "image") {
        video.hidden = true;
        video.pause();
        image.hidden = false;
        showImage(currentIndex);
    } else if (item.type === "video") {
        image.hidden = true;
        video.hidden = false;
        playVideo(item.path);
    }
}

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
        video.play().catch(err => console.warn("自动播放被浏览器拦截:", err));
    };
}
video.addEventListener("ended", () => {
    if (currentIndex < mediaList.length - 1) {
        openMedia(currentIndex + 1);
    } else {
        closeViewer();
    }
});