from pathlib import Path

from media_nest.service.deal_task import DealTask
from media_nest.models.root_task_info import TaskInfo
from tests.tool.run_collect_info import run_collect_info
from tests.fake.fake_folder_file import create_folder_file


class FakeRepository:
    def __init__(self):
        self.task_info_list = [TaskInfo(id=1, type_='video', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/视频/video_3.mp4'), dev=66312, ino=2693, duration_ms_flag=True, width_height_flag=True, thumb_flag=False),
                               TaskInfo(id=2, type_='video', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/视频/video_0.mp4'), dev=66312, ino=2690, duration_ms_flag=True, width_height_flag=True, thumb_flag=False),
                               TaskInfo(id=3, type_='video', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/视频/video_5.mp4'), dev=66312, ino=2695, duration_ms_flag=True, width_height_flag=True, thumb_flag=False),
                               TaskInfo(id=4, type_='video', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/视频/video_2.mp4'), dev=66312, ino=2692, duration_ms_flag=True, width_height_flag=True, thumb_flag=False),
                               TaskInfo(id=5, type_='video', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/视频/video_4.mp4'), dev=66312, ino=2694, duration_ms_flag=True, width_height_flag=True, thumb_flag=False),
                               TaskInfo(id=6, type_='video', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/视频/video_6.mp4'), dev=66312, ino=2696, duration_ms_flag=True, width_height_flag=True, thumb_flag=False),
                               TaskInfo(id=7, type_='video', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/视频/video_1.mp4'), dev=66312, ino=2691, duration_ms_flag=True, width_height_flag=True, thumb_flag=False),
                               TaskInfo(id=8, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/test.webp'), dev=66312, ino=2689, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=9, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/test.png'), dev=66312, ino=2688, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=10, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_7.jpg'), dev=66312, ino=2684, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=11, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_9.jpg'), dev=66312, ino=2686, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=12, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_1.jpg'), dev=66312, ino=2678, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=13, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_10.jpg'), dev=66312, ino=2687, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=14, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_3.jpg'), dev=66312, ino=2680, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=15, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_6.jpg'), dev=66312, ino=2683, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=16, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_4.jpg'), dev=66312, ino=2681, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=17, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_2.jpg'), dev=66312, ino=2679, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=18, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_8.jpg'), dev=66312, ino=2685, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=19, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_0.jpg'), dev=66312, ino=2677, duration_ms_flag=False, width_height_flag=True, thumb_flag=True),
                               TaskInfo(id=20, type_='image', path=Path('/MEGA/Vscode/ProjectsWeb/MediaNest/Untitled Folder/图片/风景/img_5.jpg'), dev=66312, ino=2682, duration_ms_flag=False, width_height_flag=True, thumb_flag=True)]

    def task_select_all(self):
        return self.task_info_list

    def update_many_video_specific_info_by_dev_ino(self, video_update_list):
        print(video_update_list)

    def update_many_image_specific_info_by_dev_ino(self, image_update_list):
        print(image_update_list)

    def task_delete_all(self):
        self.task_info_list = []


def test_deal_task():
    repository = FakeRepository()
    create_folder_file(video_num=7, image_num=11)

    do = 'deal task'
    run_collect_info(DealTask(repository).run, (), do)
    assert repository.task_select_all() == []
