from pathlib import Path
from datetime import datetime as Datetime

from media_nest.models.node_info import FolderInfo, ImageInfo, VideoInfo


def _insert_data(repository):
    fake_data_list = [FolderInfo(id=1, dev=100, ino=2001, root_id=1, parent_path=Path('/'), name='media',
                                 type_='folder', size=0, mtime=Datetime(2026, 6, 1, 12, 0, 1)),
                      FolderInfo(id=None, dev=100, ino=2002, root_id=1, parent_path=Path('/media'), name='photos',
                                 type_='folder', size=1000, mtime=Datetime(2026, 6, 1, 12, 0, 1)),
                      ImageInfo(id=7, dev=100, ino=2004, root_id=1, parent_path=Path('/media/photos'),
                                name='a.jpg', type_='image', size=1024, mtime=Datetime(2026, 6, 1, 12, 0, 0),
                                width=None, height=None),]
    fake_data = VideoInfo(id=99, dev=100, ino=2005, root_id=1, parent_path=Path('/media/photos'),
                          name='b.mp4', type_='video', size=2048, mtime=Datetime(2026, 6, 1, 12, 0, 0),
                          width=None, height=None, duration_ms=None)
    repository.insert_many(fake_data_list)
    repository.insert_one(fake_data)


def test_insert_select(repository):
    _insert_data(repository)
    result = [FolderInfo(id=1, dev=100, ino=2001, root_id=1, parent_path=Path('/'), name='media',
                         type_='folder', size=0, mtime=Datetime(2026, 6, 1, 12, 0, 1)),
              FolderInfo(id=2, dev=100, ino=2002, root_id=1, parent_path=Path('/media'), name='photos',
                         type_='folder', size=1000, mtime=Datetime(2026, 6, 1, 12, 0, 1)),
              ImageInfo(id=3, dev=100, ino=2004, root_id=1, parent_path=Path('/media/photos'),
                        name='a.jpg', type_='image', size=1024, mtime=Datetime(2026, 6, 1, 12, 0, 0),
                        width=None, height=None),
              VideoInfo(id=4, dev=100, ino=2005, root_id=1, parent_path=Path('/media/photos'),
                        name='b.mp4', type_='video', size=2048, mtime=Datetime(2026, 6, 1, 12, 0, 0),
                        width=None, height=None, duration_ms=None)]
    assert repository.select_all() == result
    assert repository.select_one_by_id(1) == result[0]
    assert repository.select_one_by_dev_ino(100, 2001) == result[0]
    assert repository.select_all_by_parent_path(Path('/media/photos')) == result[2:4]
    assert repository.select_many_in_id([1, 3, 4]) == [result[0], result[2], result[3]]
    assert repository.select_many_in_dev_ino([(100, 2004), (100, 2005)]) == [result[2], result[3]]


def test_update_one(repository):
    _insert_data(repository)

    wait_to_update = FolderInfo(id=1, dev=100, ino=2001, root_id=1, parent_path=Path('/'), name='Updated Media',
                                type_='folder', size=0, mtime=Datetime(2000, 6, 1, 12, 0, 1))
    repository.update_one_by_id(1, wait_to_update)
    assert repository.select_one_by_id(1) == wait_to_update


def test_update_many(repository):
    _insert_data(repository)

    wait_to_update = [FolderInfo(id=1, dev=100, ino=2001, root_id=1, parent_path=Path('/mine'), name='media',
                                 type_='folder', size=0, mtime=Datetime(2026, 6, 1, 12, 0, 1)),
                      ImageInfo(id=3, dev=100, ino=2004, root_id=2, parent_path=Path('/mine/photos'),
                                name='a.jpg', type_='image', size=1024, mtime=Datetime(2026, 6, 1, 12, 0, 0),
                                width=None, height=None),
                    VideoInfo(id=4, dev=100, ino=2005, root_id=1, parent_path=Path('/mine/photos'),
                          name='b.mp4', type_='video', size=2048, mtime=Datetime(2026, 6, 1, 12, 0, 0),
                          width=None, height=None, duration_ms=None)]
    update_list = [(info.id, info) for info in wait_to_update]
    repository.update_many_by_id(update_list)
    assert repository.select_one_by_id(1) == wait_to_update[0]
    assert repository.select_one_by_id(3) == wait_to_update[1]
    assert repository.select_one_by_id(4) == wait_to_update[2]

    repository.update_many_image_specific_info_by_dev_ino([((100, 2004), 200, 300)])
    repository.update_many_video_specific_info_by_dev_ino([((100, 2005), 1000, 2000, 12000)])
    assert repository.select_one_by_id(3).width == 200
    assert repository.select_one_by_id(4).duration_ms == 12000


def test_delete_one_many(repository):
    _insert_data(repository)

    repository.delete_one_by_id(1)
    assert repository.select_one_by_id(1) is None

    result = ImageInfo(id=3, dev=100, ino=2004, root_id=1, parent_path=Path('/media/photos'),
                       name='a.jpg', type_='image', size=1024, mtime=Datetime(2026, 6, 1, 12, 0, 0),
                       width=None, height=None)
    repository.delete_many_in_id([2, 4])
    assert repository.select_one_by_id(2) is None
    assert repository.select_one_by_id(4) is None
    assert repository.select_all() == [result]


def test_delete_all(repository):
    _insert_data(repository)
    repository.delete_all()
    assert repository.select_all() == []
