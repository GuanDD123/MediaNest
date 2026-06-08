from pathlib import Path

from media_nest.core.constant import HLS_MODE
from media_nest.models.node_join_segment import NodeJoinSegment
from media_nest.service.build_m3u import BuildM3u


class FakeRepository:
    def segments_select_many_join_video_id_by_parent_path(self, parent_path):
        return [
            NodeJoinSegment(video_id=7, video_parent_path=Path('/7'), video_name='77', video_dev=777, video_ino=7777, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            NodeJoinSegment(video_id=1, video_parent_path=Path('/1'), video_name='11', video_dev=111, video_ino=1111, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            NodeJoinSegment(video_id=3, video_parent_path=Path('/3'), video_name='33', video_dev=333, video_ino=3333, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            NodeJoinSegment(video_id=1, video_parent_path=Path('/1'), video_name='11', video_dev=111, video_ino=1111, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            NodeJoinSegment(video_id=2, video_parent_path=Path('/2'), video_name='22', video_dev=222, video_ino=2222, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            NodeJoinSegment(video_id=2, video_parent_path=Path('/2'), video_name='22', video_dev=222, video_ino=2222, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            NodeJoinSegment(video_id=3, video_parent_path=Path('/3'), video_name='33', video_dev=333, video_ino=3333, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            NodeJoinSegment(video_id=4, video_parent_path=Path('/4'), video_name='44', video_dev=444, video_ino=4444, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            NodeJoinSegment(video_id=5, video_parent_path=Path('/5'), video_name='55', video_dev=555, video_ino=5555, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            NodeJoinSegment(video_id=5, video_parent_path=Path('/5'), video_name='55', video_dev=555, video_ino=5555, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            NodeJoinSegment(video_id=4, video_parent_path=Path('/4'), video_name='44', video_dev=444, video_ino=4444, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            NodeJoinSegment(video_id=6, video_parent_path=Path('/6'), video_name='66', video_dev=666, video_ino=6666, segment_order=0, segment_duration_ms=8333, segment_name='seg_00000.ts'),
            NodeJoinSegment(video_id=6, video_parent_path=Path('/6'), video_name='66', video_dev=666, video_ino=6666, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts'),
            NodeJoinSegment(video_id=7, video_parent_path=Path('/7'), video_name='77', video_dev=777, video_ino=7777, segment_order=1, segment_duration_ms=4666, segment_name='seg_00001.ts')
        ]


def test_build_m3u():
    build_m3u = BuildM3u(FakeRepository())
    result = build_m3u.run(Path('123'), shuffle_flag=True)
    print(result)
    if HLS_MODE == 'fMP4':
        assert len(result.splitlines()) == 42 + 4
    elif HLS_MODE == 'TS':
        assert len(result.splitlines()) == 28 + 3
    elif not HLS_MODE:
        assert len(result.splitlines()) == 28 + 2
