// mark.js - 标记功能
window.toggleCurrentMark = async function () {
    const state = window.getState();
    const item = state.mediaList[state.currentIndex];
    const newMarkState = !item.marked;

    item.marked = newMarkState;
    state.markBtn.textContent = newMarkState ? "⭐" : "☆";

    // 同步 currentFolderData 中的标记状态
    const folderItem = state.currentFolderData.find(i => i.path === item.path);
    if (folderItem) folderItem.marked = newMarkState;

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