from pathlib import Path
from datetime import datetime as Datetime

from media_nest.core.constant import HLS_MODE
from media_nest.models import VideoSegmentInfo, VideoInfo
from media_nest.service.build_m3u import BuildM3u


class FakeRepository:
    def node_select_by_parent_path(self, parent_path):
        return [
            VideoInfo(id=1,dev=111,ino=1111,root_id=1,parent_path=Path("/1"),name="11",type_="video",size=2048,mtime=Datetime(2026, 6, 1, 12, 0, 0),width=111,height=1111,duration_ms=11111),
            VideoInfo(id=2,dev=222,ino=2222,root_id=1,parent_path=Path("/2"),name="22",type_="video",size=2048,mtime=Datetime(2026, 6, 1, 12, 0, 0),width=222,height=2222,duration_ms=22222),
            VideoInfo(id=3,dev=333,ino=3333,root_id=1,parent_path=Path("/3"),name="33",type_="video",size=2048,mtime=Datetime(2026, 6, 1, 12, 0, 0),width=333,height=3333,duration_ms=33333),
            VideoInfo(id=4,dev=444,ino=4444,root_id=1,parent_path=Path("/4"),name="44",type_="video",size=2048,mtime=Datetime(2026, 6, 1, 12, 0, 0),width=444,height=4444,duration_ms=44444),
            VideoInfo(id=5,dev=555,ino=5555,root_id=1,parent_path=Path("/5"),name="55",type_="video",size=2048,mtime=Datetime(2026, 6, 1, 12, 0, 0),width=555,height=5555,duration_ms=55555),
            VideoInfo(id=6,dev=666,ino=6666,root_id=1,parent_path=Path("/6"),name="66",type_="video",size=2048,mtime=Datetime(2026, 6, 1, 12, 0, 0),width=666,height=6666,duration_ms=66666),
            VideoInfo(id=7,dev=777,ino=7777,root_id=1,parent_path=Path("/7"),name="77",type_="video",size=2048,mtime=Datetime(2026, 6, 1, 12, 0, 0),width=777,height=7777,duration_ms=77777),
        ]

    def segments_select_join_node_id_by_parent_path(self, parent_path):
        return [
            VideoSegmentInfo(video_id=7, video_parent_path=Path('/7'), video_name='77', video_dev=777, video_ino=7777, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            VideoSegmentInfo(video_id=1, video_parent_path=Path('/1'), video_name='11', video_dev=111, video_ino=1111, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            VideoSegmentInfo(video_id=3, video_parent_path=Path('/3'), video_name='33', video_dev=333, video_ino=3333, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            VideoSegmentInfo(video_id=1, video_parent_path=Path('/1'), video_name='11', video_dev=111, video_ino=1111, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            VideoSegmentInfo(video_id=2, video_parent_path=Path('/2'), video_name='22', video_dev=222, video_ino=2222, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            VideoSegmentInfo(video_id=2, video_parent_path=Path('/2'), video_name='22', video_dev=222, video_ino=2222, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            VideoSegmentInfo(video_id=3, video_parent_path=Path('/3'), video_name='33', video_dev=333, video_ino=3333, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            VideoSegmentInfo(video_id=4, video_parent_path=Path('/4'), video_name='44', video_dev=444, video_ino=4444, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            VideoSegmentInfo(video_id=5, video_parent_path=Path('/5'), video_name='55', video_dev=555, video_ino=5555, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            VideoSegmentInfo(video_id=5, video_parent_path=Path('/5'), video_name='55', video_dev=555, video_ino=5555, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            VideoSegmentInfo(video_id=4, video_parent_path=Path('/4'), video_name='44', video_dev=444, video_ino=4444, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            VideoSegmentInfo(video_id=6, video_parent_path=Path('/6'), video_name='66', video_dev=666, video_ino=6666, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            VideoSegmentInfo(video_id=6, video_parent_path=Path('/6'), video_name='66', video_dev=666, video_ino=6666, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            VideoSegmentInfo(video_id=7, video_parent_path=Path('/7'), video_name='77', video_dev=777, video_ino=7777, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts')
        ]


def test_build_m3u():
    build_m3u = BuildM3u(FakeRepository())
    result = build_m3u.run(Path('123'), shuffle_flag=False)
    print(result)
    print()
    result = build_m3u.run(Path('123'), shuffle_flag=True)
    print(result)
    if HLS_MODE == 'fMP4':
        assert len(result.splitlines()) == 42 + 4
    elif HLS_MODE == 'TS':
        assert len(result.splitlines()) == 28 + 3
    elif not HLS_MODE:
        assert len(result.splitlines()) == 14 + 2
