function sync() {
    fetch("/admin/sync", {
        method: "POST"
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) { alert(data.msg || "OK"); }
            else { alert(data.msg || "Failed"); }
        })
        .catch(err => { alert("Failed"); });
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
        .then(data => {
            if (data.success) { alert(data.msg || "OK"); }
            else { alert(data.msg || "Failed"); }
        })
        .catch(err => { alert("Failed"); });
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
        .then(data => {
            if (data.success) { alert(data.msg || "OK"); }
            else { alert(data.msg || "Failed"); }
        })
        .catch(err => { alert("Failed"); });
}