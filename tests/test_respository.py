from pathlib import Path
from datetime import datetime as Datetime

from media_nest.models import FolderInfo, ImageInfo, VideoInfo, TaskInfo, SegmentInfo


class TestInsert:
    def setup_method(self):
        fake_data_list = [
            FolderInfo(
                id=1,
                dev=100,
                ino=2001,
                root_id=1,
                parent_path=Path("/"),
                name="media",
                type_="folder",
                size=0,
                mtime=Datetime(2026, 6, 1, 12, 0, 1),
            ),
            FolderInfo(
                id=None,
                dev=100,
                ino=2002,
                root_id=1,
                parent_path=Path("/media"),
                name="photos",
                type_="folder",
                size=1000,
                mtime=Datetime(2026, 6, 1, 12, 0, 1),
            ),
            ImageInfo(
                id=7,
                dev=100,
                ino=2004,
                root_id=1,
                parent_path=Path("/media/photos"),
                name="a.jpg",
                type_="image",
                size=1024,
                mtime=Datetime(2026, 6, 1, 12, 0, 0),
                width=None,
                height=None,
            ),
            VideoInfo(
                id=99,
                dev=100,
                ino=2005,
                root_id=1,
                parent_path=Path("/media/photos"),
                name="b.mp4",
                type_="video",
                size=2048,
                mtime=Datetime(2026, 6, 1, 12, 0, 0),
                width=None,
                height=None,
                duration_ms=None,
            ),
        ]
        self.repository.node_insert_many(fake_data_list)

    def teardown_method(self):
        self.repository.node_delete_all()

    def test_insert_select_delete(self):
        assert len(self.repository.node_select_all()) == 4
        assert self.repository.node_select_by_id(1).ino == 2001
        assert self.repository.node_select_by_dev_ino(100, 2001).id == 1
        assert len(self.repository.node_select_by_parent_path("/media/photos")) == 2
        assert len(self.repository.node_select_in_id([1, 3, 4])) == 3
        assert (
            len(self.repository.node_select_in_dev_ino([(100, 2004), (100, 2005)])) == 2
        )

        self.repository.task_insert(
            TaskInfo(
                id=None,
                type_="image",
                path=Path("/media/photos/a.jpg"),
                dev=100,
                ino=2004,
                duration_ms_flag=0,
                width_height_flag=1,
                hls_flag=1,
                thumb_flag=1,
            )
        )
        assert self.repository.node_select_id_join_task_dev_ino_by_hlsflag() == {
            "100_2004": 3
        }
        self.repository.segment_insert_many(
            [
                SegmentInfo(
                    video_id=4, order_num=1, duration_ms=1000, name="Segment 1"
                ),
                SegmentInfo(video_id=4, order_num=2, duration_ms=800, name="Segment 2"),
            ]
        )
        assert (
            len(
                self.repository.segments_select_join_node_id_by_parent_path(
                    "/media/photos"
                )
            )
            == 2
        )

        self.repository.node_delete_by_id(1)
        assert self.repository.node_select_by_id(1) is None
        self.repository.node_delete_in_id([2, 4])
        assert self.repository.node_select_by_id(2) is None
        assert self.repository.node_select_by_id(4) is None
        assert len(self.repository.node_select_all()) == 1
        self.repository.segment_delete_all()
        assert self.repository.segment_select_all() == []
        self.repository.task_delete_all()

    def test_update_one(self):
        wait_to_update = FolderInfo(
            id=1,
            dev=100,
            ino=2001,
            root_id=1,
            parent_path=Path("/"),
            name="Updated Media",
            type_="folder",
            size=0,
            mtime=Datetime(2000, 6, 1, 12, 0, 1),
        )
        self.repository.node_update_by_id(1, wait_to_update)
        assert self.repository.node_select_by_id(1) == wait_to_update

    def test_update_many(self):
        wait_to_update = [
            FolderInfo(
                id=1,
                dev=100,
                ino=2001,
                root_id=1,
                parent_path=Path("/mine"),
                name="media",
                type_="folder",
                size=0,
                mtime=Datetime(2026, 6, 1, 12, 0, 1),
            ),
            ImageInfo(
                id=3,
                dev=100,
                ino=2004,
                root_id=2,
                parent_path=Path("/mine/photos"),
                name="a.jpg",
                type_="image",
                size=1024,
                mtime=Datetime(2026, 6, 1, 12, 0, 0),
                width=None,
                height=None,
            ),
            VideoInfo(
                id=4,
                dev=100,
                ino=2005,
                root_id=1,
                parent_path=Path("/mine/photos"),
                name="b.mp4",
                type_="video",
                size=2048,
                mtime=Datetime(2026, 6, 1, 12, 0, 0),
                width=None,
                height=None,
                duration_ms=None,
            ),
        ]
        update_list = [(info.id, info) for info in wait_to_update]
        self.repository.node_update_many_by_id(update_list)
        assert self.repository.node_select_by_id(1) == wait_to_update[0]
        assert self.repository.node_select_by_id(3) == wait_to_update[1]
        assert self.repository.node_select_by_id(4) == wait_to_update[2]

        self.repository.node_update_many_width_height_by_dev_ino([((100, 2004), 200, 300)])
        self.repository.node_update_many_width_height_duration_by_dev_ino(
            [((100, 2005), 1000, 2000, 12000)]
        )
        assert self.repository.node_select_by_id(3).width == 200
        assert self.repository.node_select_by_id(4).duration_ms == 12000
