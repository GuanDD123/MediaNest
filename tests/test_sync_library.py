from pathlib import Path
from datetime import datetime as Datetime
from PIL import Image
import subprocess
import pytest

from media_nest.core.settings import Settings
from media_nest.service.sync_library import SyncLibrary
from media_nest.models import RootInfo
from media_nest.repository import Repository
from tests.tool.run_collect_info import run_collect_info
from tests.fake.fake_folder_file import create_folder_file


ROOT = Path(__file__).parents[1] / "Untitled Folder"
VIDEO_NUM = 7
IMAGE_NUM = 11


@pytest.mark.usefixtures("get_repository")
class TestSyncLibrary:
    repository: Repository
    settings: Settings

    def teardown_method(self):
        self.repository.task_delete_all()

    @pytest.mark.run(order=1)
    def test_setup_class_data(self):
        create_folder_file(video_num=VIDEO_NUM, image_num=IMAGE_NUM)
        self.repository.root_insert(RootInfo(None, ROOT, Datetime.now(), 0), )

    @pytest.mark.run(order=2)
    def test_initialization(self):
        run_collect_info(SyncLibrary(self.repository, self.settings).run, (), "1: ")
        assert len(self.repository.node_select_all()) == 53
        assert len(self.repository.task_select_all()) == IMAGE_NUM + 2 + VIDEO_NUM

    @pytest.mark.run(order=3)
    def test_no_addition(self):
        run_collect_info(SyncLibrary(self.repository, self.settings).run, (), "2: ")
        assert len(self.repository.node_select_all()) == 53
        task_list = [
            task for task in self.repository.task_select_all() if task.width_height_flag
        ]
        assert len(task_list) == 0

    @pytest.mark.run(order=4)
    def test_addition(self):
        (Image.new("RGB", (100, 100)).save(ROOT / "图片" / "风景" / "new.jpg"))
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                "testsrc=size=640x480",
                "-t",
                "1",
                "-y",
                str(ROOT / "视频" / "new.mp4"),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        run_collect_info(SyncLibrary(self.repository, self.settings).run, (), "3: ")
        assert len(self.repository.node_select_all()) == 55
        task_list = [
            task for task in self.repository.task_select_all() if task.width_height_flag
        ]
        assert len(task_list) == 2

    @pytest.mark.run(order=5)
    def test_update(self):
        # print(self.repository.node_select_all())
        img_path = ROOT / "图片" / "风景" / "img_0.jpg"
        Image.new("RGB", (4000, 3000)).save(img_path)
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                "testsrc=size=3840x2160",
                "-t",
                "3",
                "-y",
                str(ROOT / "视频" / "video_0.mp4"),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        run_collect_info(SyncLibrary(self.repository, self.settings).run, (), "4: ")
        assert len(self.repository.node_select_all()) == 55
        task_list = [
            task for task in self.repository.task_select_all() if task.width_height_flag
        ]
        # print(self.repository.node_select_all())
        assert len(task_list) == 2

    @pytest.mark.run(order=6)
    def test_delete(self):
        (ROOT / "图片" / "风景" / "img_1.jpg").unlink()
        (ROOT / "视频" / "video_1.mp4").unlink()

        run_collect_info(SyncLibrary(self.repository, self.settings).run, (), "5: ")
        assert len(self.repository.node_select_all()) == 53
        task_list = [
            task for task in self.repository.task_select_all() if task.width_height_flag
        ]
        assert len(task_list) == 0

    @pytest.mark.run(order=7)
    def test_rename(self):
        (ROOT / "图片" / "风景" / "img_2.jpg").rename(
            ROOT / "图片" / "风景" / "img_2_renamed.jpg"
        )
        (ROOT / "视频" / "video_2.mp4").rename(ROOT / "视频" / "video_2_renamed.mp4")

        run_collect_info(SyncLibrary(self.repository, self.settings).run, (), "6: ")
        assert len(self.repository.node_select_all()) == 53
        task_list = [
            task for task in self.repository.task_select_all() if task.width_height_flag
        ]
        assert len(task_list) == 0

    @pytest.mark.run(order=8)
    def test_move(self):
        (ROOT / "图片" / "风景" / "img_3.jpg").rename(
            ROOT / "图片" / "人物" / "img_3.jpg"
        )
        (ROOT / "视频" / "video_3.mp4").rename(ROOT / "视频" / "电影" / "video_3.mp4")
        run_collect_info(SyncLibrary(self.repository, self.settings).run, (), "7: ")
        assert len(self.repository.node_select_all()) == 53
        task_list = [
            task for task in self.repository.task_select_all() if task.width_height_flag
        ]
        assert len(task_list) == 0

    @pytest.mark.run(order=9)
    def test_chinese_files(self):
        (ROOT / "中文测试").mkdir()
        (ROOT / "中文测试" / "测试图片.jpg").touch()
        (ROOT / "中文测试" / "空 格.txt").touch()
        (ROOT / "中文测试" / "[特殊]#文件.txt").touch()
        (ROOT / "中文测试" / "😊emoji.txt").touch()

        run_collect_info(SyncLibrary(self.repository, self.settings).run, (), "8: ")
        assert len(self.repository.node_select_all()) == 55
        task_list = [
            task for task in self.repository.task_select_all() if task.width_height_flag
        ]
        assert len(task_list) == 1
