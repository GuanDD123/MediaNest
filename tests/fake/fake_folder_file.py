import shutil
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parents[2] / "Untitled Folder"


def create_folder_file(video_num=5, image_num=10):
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir()

    (ROOT / "图片").mkdir()
    (ROOT / "视频").mkdir()
    (ROOT / "文档").mkdir()
    (ROOT / "图片" / "风景").mkdir()
    (ROOT / "图片" / "人物").mkdir()
    (ROOT / "视频" / "电影").mkdir()
    (ROOT / "视频" / "短片").mkdir()
    (ROOT / "空目录").mkdir()
    (ROOT / "深层" / "a" / "b" / "c" / "d").mkdir(parents=True)

    for i in range(10):
        (ROOT / "文档" / f"file_{i}.txt").write_text(f"hello {i}", encoding="utf8")

    for i in range(image_num):
        img = Image.new("RGB", (1920, 1080))
        img.save(ROOT / "图片" / "风景" / f"img_{i}.jpg")
    for fmt in ["png", "webp"]:
        Image.new("RGB", (500, 500)).save(ROOT / "图片" / f"test.{fmt}")

    video_dir = ROOT / "视频"
    for i in range(video_num):
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                "testsrc=size=1280x720:rate=30",
                "-t",
                "2",
                "-y",
                str(video_dir / f"video_{i}.mp4"),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

    long_dir = ROOT
    for i in range(20):
        long_dir /= f"folder_{i}"
    long_dir.mkdir(parents=True)
    (long_dir / "long.txt").touch()
