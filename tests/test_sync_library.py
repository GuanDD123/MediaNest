from pathlib import Path
from datetime import datetime as Datetime
from PIL import Image
import subprocess

from media_nest.service.sync_library import SyncLibrary
from media_nest.models.root_task_segment_info import RootInfo
from tests.tool.run_collect_info import run_collect_info
from tests.fake.fake_folder_file import create_folder_file


ROOT = Path(__file__).parents[1] / 'Untitled Folder'


def test_sync_library(repository):
    video_num, image_num = 7, 11
    create_folder_file(video_num, image_num)
    repository.root_insert(RootInfo(None, ROOT, Datetime.now()))

    num = 1
    do = '数据库写入全部图片和视频'
    run_collect_info(SyncLibrary(repository).run, (), do)
    file_num = 33 + image_num + 2 + video_num
    assert len(repository.select_all()) == file_num
    assert len(repository.task_select_all()) == image_num + 2 + video_num
    repository.task_delete_all()

    num += 1
    do = '新增0，删除0，更新0'
    run_collect_info(SyncLibrary(repository).run, (), do)
    assert len(repository.select_all()) == file_num
    task_list = [task for task in repository.task_select_all() if task.width_height_flag]
    assert len(task_list) == 0
    repository.task_delete_all()

    num += 1
    do = '新增1张图片，新增1条视频'
    # 新增图片
    (Image.new('RGB', (100, 100)).save(ROOT / '图片' / '风景' / 'new.jpg'))
    # 新增视频
    subprocess.run(['ffmpeg', '-f', 'lavfi', '-i', 'testsrc=size=640x480', '-t', '1', '-y',
                    str(ROOT / '视频' / 'new.mp4')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_collect_info(SyncLibrary(repository).run, (), do)
    file_num += 2
    assert len(repository.select_all()) == file_num
    task_list = [task for task in repository.task_select_all() if task.width_height_flag]
    assert len(task_list) == 2
    repository.task_delete_all()

    num += 1
    do = '更新img_0.jpg元数据，更新video_0.mp4元数据'
    # 修改图片内容
    img_path = ROOT / '图片' / '风景' / 'img_0.jpg'
    Image.new('RGB', (4000, 3000)).save(img_path)
    # 修改视频内容
    subprocess.run(['ffmpeg', '-f', 'lavfi', '-i', 'testsrc=size=3840x2160', '-t', '3', '-y',
                    str(ROOT / '视频' / 'video_0.mp4')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_collect_info(SyncLibrary(repository).run, (), do)
    assert len(repository.select_all()) == file_num
    task_list = [task for task in repository.task_select_all() if task.width_height_flag]
    assert len(task_list) == 2
    repository.task_delete_all()

    num += 1
    do = '删除1张图片，删除1条视频'
    (ROOT / '图片' / '风景' / 'img_1.jpg').unlink()
    (ROOT / '视频' / 'video_1.mp4').unlink()
    run_collect_info(SyncLibrary(repository).run, (), do)
    file_num -= 2
    assert len(repository.select_all()) == file_num
    task_list = [task for task in repository.task_select_all() if task.width_height_flag]
    assert len(task_list) == 0
    repository.task_delete_all()

    num += 1
    do = '路径更新，而非删除+新增'
    # 图片重命名
    (ROOT / '图片' / '风景' / 'img_2.jpg').rename(ROOT / '图片' / '风景' / 'img_2_renamed.jpg')
    # 视频重命名
    (ROOT / '视频' / 'video_2.mp4').rename(ROOT / '视频' / 'video_2_renamed.mp4')
    run_collect_info(SyncLibrary(repository).run, (), do)
    assert len(repository.select_all()) == file_num
    task_list = [task for task in repository.task_select_all() if task.width_height_flag]
    assert len(task_list) == 0
    repository.task_delete_all()

    num += 1
    do = '路径更新，parent_path更新'
    # 图片移动目录
    (ROOT / '图片' / '风景' / 'img_3.jpg').rename(ROOT / '图片' / '人物' / 'img_3.jpg')
    # 视频移动目录
    (ROOT / '视频' / 'video_3.mp4').rename(ROOT / '视频' / '电影' / 'video_3.mp4')
    run_collect_info(SyncLibrary(repository).run, (), do)
    assert len(repository.select_all()) == file_num
    task_list = [task for task in repository.task_select_all() if task.width_height_flag]
    assert len(task_list) == 0
    repository.task_delete_all()

    num += 1
    do = '中文图片入库，txt不入库'
    (ROOT / '中文测试').mkdir()
    (ROOT / '中文测试' / '测试图片.jpg').touch()
    (ROOT / '中文测试' / '空 格.txt').touch()
    (ROOT / '中文测试' / '[特殊]#文件.txt').touch()
    (ROOT / '中文测试' / '😊emoji.txt').touch()
    run_collect_info(SyncLibrary(repository).run, (), do)
    file_num += 2
    assert len(repository.select_all()) == file_num
    task_list = [task for task in repository.task_select_all() if task.width_height_flag]
    assert len(task_list) == 1
    repository.task_delete_all()
