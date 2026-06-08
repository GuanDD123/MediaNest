from pathlib import Path
from datetime import datetime as Datetime
from collections import namedtuple

from media_nest.core.constant import NODE_KEY, ROOT_KEY, TASK_KEY, SEGMENT_KEY
from media_nest.models.node_info import FolderInfo, VideoInfo, ImageInfo
from media_nest.models.root_task_segment_info import RootInfo, TaskInfo, SegmentInfo

Node = namedtuple('Node', NODE_KEY)
Root = namedtuple('Root', ROOT_KEY)
Task = namedtuple('Task', TASK_KEY)
Segment = namedtuple('Segment', SEGMENT_KEY)


def model_to_row(info: FolderInfo | VideoInfo | ImageInfo | RootInfo | TaskInfo | SegmentInfo, table: str) -> tuple:
    if table == 'root':
        return (str(info.path), int(info.last_sync_at.timestamp()))
    elif table == 'task':
        return (info.type_, str(info.path), info.dev, info.ino, info.duration_ms_flag,
                info.width_height_flag, info.hls_flag, info.thumb_flag)
    elif table == 'segment':
        return (info.video_id, info.segment_order, info.duration_ms, str(info.segment_name))
    else:  # node
        if info.type_ == 'folder':
            duration_ms = None
            width, height = None, None
        elif info.type_ == 'video':
            duration_ms = info.duration_ms
            width, height = info.width, info.height
        else:  # image
            duration_ms = None
            width, height = info.width, info.height
        return (info.dev, info.ino, info.root_id, str(info.parent_path), info.name, info.type_, info.size,
                int(info.mtime.timestamp()), duration_ms, width, height)


def row_to_model(row: tuple, table: str) -> RootInfo | TaskInfo | FolderInfo | VideoInfo | ImageInfo | SegmentInfo:
    if table == 'root':
        root = Root(*row)
        return RootInfo(id=root.id, path=Path(root.path), last_sync_at=Datetime.fromtimestamp(root.last_sync_at))
    elif table == 'task':
        task = Task(*row)
        return TaskInfo(id=task.id, type_=task.type_, path=Path(task.path), dev=task.dev,
                        ino=task.ino, duration_ms_flag=bool(task.duration_ms_flag),
                        width_height_flag=bool(task.width_height_flag), hls_flag=bool(task.hls_flag),
                        thumb_flag=bool(task.thumb_flag))
    elif table == 'segment':
        segment = Segment(*row)
        return SegmentInfo(video_id=segment.video_id, segment_order=segment.segment_order,
                           duration_ms=segment.duration_ms, segment_name=segment.segment_name)
    else:  # node
        node = Node(*row)
        if node.type_ == 'folder':
            return FolderInfo(id=node.id, dev=node.dev, ino=node.ino, root_id=node.root_id,
                              parent_path=Path(node.parent_path), name=node.name,
                              type_=node.type_, size=node.size, mtime=Datetime.fromtimestamp(node.mtime))
        elif node.type_ == 'video':
            return VideoInfo(id=node.id, dev=node.dev, ino=node.ino, root_id=node.root_id,
                             parent_path=Path(node.parent_path), name=node.name,
                             type_=node.type_, size=node.size, mtime=Datetime.fromtimestamp(node.mtime),
                             width=node.width, height=node.height, duration_ms=node.duration_ms)
        else:  # image
            return ImageInfo(id=node.id, dev=node.dev, ino=node.ino, root_id=node.root_id,
                             parent_path=Path(node.parent_path), name=node.name,
                             type_=node.type_, size=node.size, mtime=Datetime.fromtimestamp(node.mtime),
                             width=node.width, height=node.height)
