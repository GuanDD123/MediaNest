from pathlib import Path
from datetime import datetime as Datetime
from collections import namedtuple

from media_nest.core.constant import NODE_KEYS, ROOT_KEYS, TASK_KEYS, SEGMENT_KEYS
from media_nest.models import NodeInfo, RootInfo, TaskInfo, SegmentInfo

Node = namedtuple("Node", NODE_KEYS)
Root = namedtuple("Root", ROOT_KEYS)
Task = namedtuple("Task", TASK_KEYS)
Segment = namedtuple("Segment", SEGMENT_KEYS)


def model_to_row(
    table: str, info: NodeInfo | RootInfo | TaskInfo | SegmentInfo
) -> tuple[int | str, ...]:
    if table == "root":
        return (str(info.path), int(info.last_sync_time.timestamp()), info.size)
    elif table == "node":
        return (
            info.dev,
            info.ino,
            info.root_id,
            str(info.parent_path),
            info.name,
            info.type_,
            info.size,
            int(info.mtime.timestamp()),
            info.duration_ms,
            info.width,
            info.height,
            int(info.marked),
        )
    elif table == "task":
        return (
            info.type_,
            str(info.path),
            info.dev,
            info.ino,
            int(info.duration_ms_flag),
            int(info.width_height_flag),
            int(info.hls_flag),
            int(info.thumb_flag),
        )
    else:  # segment
        return (
            info.video_id,
            info.order_,
            info.duration_ms,
            info.name,
        )


def row_to_model(
    table: str, row: tuple[int | str, ...]
) -> RootInfo | TaskInfo | NodeInfo | SegmentInfo:
    if table == "root":
        root = Root(*row)
        return RootInfo(
            id=root.id,
            path=Path(root.path),
            last_sync_time=Datetime.fromtimestamp(root.last_sync_time),
            size=root.size,
        )
    elif table == "node":
        node = Node(*row)
        return NodeInfo(
            id=node.id,
            dev=node.dev,
            ino=node.ino,
            root_id=node.root_id,
            parent_path=Path(node.parent_path),
            name=node.name,
            type_=node.type_,
            size=node.size,
            mtime=Datetime.fromtimestamp(node.mtime),
            width=node.width,
            height=node.height,
            duration_ms=node.duration_ms,
            marked=bool(node.marked),
        )
    elif table == "task":
        task = Task(*row)
        return TaskInfo(
            id=task.id,
            type_=task.type_,
            path=Path(task.path),
            dev=task.dev,
            ino=task.ino,
            duration_ms_flag=bool(task.duration_ms_flag),
            width_height_flag=bool(task.width_height_flag),
            hls_flag=bool(task.hls_flag),
            thumb_flag=bool(task.thumb_flag),
        )
    else:  # segment
        segment = Segment(*row)
        return SegmentInfo(
            video_id=segment.video_id,
            order_=segment.order_,
            duration_ms=segment.duration_ms,
            name=segment.name,
        )
