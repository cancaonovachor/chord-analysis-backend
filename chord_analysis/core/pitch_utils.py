"""
音程計算関連のユーティリティ関数を提供するモジュール。
"""
from typing import Dict

# 音階と数値の対応辞書
PITCH_SCALE_DICT: Dict[str, int] = {
    "C": 0,
    "B#": 0,
    "D--": 0,
    "C#": 1,
    "D-": 1,
    "B##": 1,
    "D": 2,
    "C##": 2,
    "E--": 2,
    "D#": 3,
    "E-": 3,
    "F--": 3,
    "E": 4,
    "F-": 4,
    "D##": 4,
    "F": 5,
    "E#": 5,
    "G--": 5,
    "F#": 6,
    "G-": 6,
    "E##": 6,
    "G": 7,
    "F##": 7,
    "A--": 7,
    "G#": 8,
    "A-": 8,
    "A": 9,
    "G##": 9,
    "B--": 9,
    "A#": 10,
    "B-": 10,
    "C--": 10,
    "B": 11,
    "C-": 11,
    "A##": 11,
}


def find_pitch_interval(root: str, add_note: str) -> int:
    """
    ルート音と追加音の音程間隔を計算する。

    Parameters
    ----------
    root : str
        ルート音の名前（例: "C", "F#"）
    add_note : str
        追加音の名前（例: "G", "B-"）

    Returns
    -------
    int
        ルート音と追加音の間の半音数
    """
    interval = PITCH_SCALE_DICT[add_note] - PITCH_SCALE_DICT[root]
    return interval


def pitch_scale(pitch: str, alter: int) -> str:
    """
    音名と変化記号から変更後の音名を取得する。

    Parameters
    ----------
    pitch : str
        基本音名（例: "C", "D"）
    alter : int
        変化記号の値（シャープ: 1, フラット: -1, なし: 0）

    Returns
    -------
    str
        変更後の音名（例: "C#", "D-"）
    """
    pitch_scale_list = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    ind = pitch_scale_list.index(pitch)
    return pitch_scale_list[(ind + alter) % 12]  # 12音を超える場合に対応


def get_alteration(note: str) -> int:
    """
    音符の変更記号を返す。

    Parameters
    ----------
    note : str
        音符名（例: "C", "F#", "Bb"）

    Returns
    -------
    int
        変更記号の値（シャープ: 1, フラット: -1, なし: 0）
    """
    if len(note) == 1:
        return 0
    elif note[1] == "#":
        return 1
    elif note[1] in {"b", "-"}:  # bとハイフンの両方に対応
        return -1
    else:
        return 0
