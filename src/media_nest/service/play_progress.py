import json

from media_nest.core.constant import LAST_PLAYLIST, LAST_PROGRESS

__all__ = ["save_playlist", "save_progress", "continue_last_play"]


def save_playlist(playlist: tuple[list[dict], list[dict]]) -> None:
    with open(LAST_PLAYLIST, "w", encoding="utf-8") as f:
        json.dump(playlist, f, indent=4, ensure_ascii=False)


def save_progress(index: int) -> None:
    LAST_PROGRESS.write_text(str(index))


def continue_last_play() -> tuple[
    tuple[list[dict[str, str | int]], list[dict[str, str | int]]], int
]:
    if not LAST_PLAYLIST.exists() or not LAST_PROGRESS.exists():
        return [], 0

    with open(LAST_PLAYLIST, "r", encoding="utf-8") as f:
        last_playlist = json.load(f)
    with open(LAST_PROGRESS, "r", encoding="utf-8") as f:
        index = int(f.read().strip())
    if index + 1 >= len(last_playlist[1]):
        return [], 0

    return (last_playlist, index)
