"""
コード名の解析関連の関数を提供するモジュール。
"""
from typing import Tuple, Optional, List
from xml.etree import ElementTree as et

from chord_analysis.core.pitch_utils import get_alteration, find_pitch_interval


def getChordRoot(chord_name: str) -> str:
    """
    コード名からルート音（根音）を抽出する。

    Parameters
    ----------
    chord_name : str
        コード名（例: "G#power", "G--dim"）

    Returns
    -------
    str
        ルート音（根音）の文字列（例: "G#", "G--"）
    
    Notes
    -----
    ルート音は最初の文字と、続く変化記号（#または-）を含む。
    最大3文字まで検索する。
    """
    result = chord_name[0]
    # 先頭3文字 or chord root要素と関係ないものが来るまで繰り返し
    for i in range(1, min(3, len(chord_name))):
        # - or # が来たらそれも追加
        if chord_name[i] in {"#", "-"}:
            result += chord_name[i]
        else:
            break
    return result


def getChordKind(chord_name: str) -> str:
    """
    コード名からコードの種類（ルート音以外の部分）を抽出する。

    Parameters
    ----------
    chord_name : str
        コード名（例: "G#maj7", "Cm7/E-"）

    Returns
    -------
    str
        コードの種類（例: "maj7", "m7"）
        1文字のコード名（ルート音のみ）の場合は空文字列を返す。
    
    Notes
    -----
    ルート音（最初の文字と変化記号）を除いた部分を返す。
    分数コード（/以降）は削除される。
    """
    # 1文字の場合は空で返す（ルート音のみの場合）
    if len(chord_name) == 1:
        return ""
    
    # ルート音以外を切り出す
    chord_kind = chord_name[1:]
    
    # ルート音の変化記号（#か-）がある場合はそれも除く
    if chord_kind and chord_kind[0] in {"#", "-"}:
        chord_kind = chord_kind[1:]

    # 分数コード（/以降）を削除
    chord_kind = chord_kind.split("/")[0]
    
    return chord_kind


def getChordRootAndBass(chord_name: str) -> Tuple[str, int, Optional[str], Optional[int]]:
    """
    コード名からルート音とベース音を抽出する。

    Parameters
    ----------
    chord_name : str
        コード名（例: "G#maj7", "Cm7/E-"）

    Returns
    -------
    Tuple[str, int, Optional[str], Optional[int]]
        ルート音の文字, ルート音の変化記号の値, ベース音の文字（ない場合はNone）, ベース音の変化記号の値（ない場合はNone）
        例: ("C", 0, None, None) - Cメジャーコード
        例: ("F", 0, "G", 0) - F on G
    
    Notes
    -----
    分数コード（/以降）がある場合はベース音として解析する。
    """
    splitted_chord_name = chord_name.split("/")
    
    # chord_name に Bassがない場合 ex. F#, Bb
    if len(splitted_chord_name) == 1:
        chord_root = splitted_chord_name[0]
        root_alter = get_alteration(chord_root)
        return chord_root[0], root_alter, None, None
    else:
        # chord_name に Bass がある場合 ex. F/B-
        chord_root, chord_bass = splitted_chord_name
        root_alter = get_alteration(chord_root)
        bass_alter = get_alteration(chord_bass)
        return chord_root[0], root_alter, chord_bass[0], bass_alter


def convertChordKind(chord_name: str) -> Tuple[str, Optional[et.Element], Optional[str]]:
    """
    コード名からMusicXML形式のコード種類情報を生成する。

    Parameters
    ----------
    chord_name : str
        コード名（例: "G#maj7", "Cm7/E-", "GpoweraddF"）

    Returns
    -------
    Tuple[str, Optional[et.Element], Optional[str]]
        - musicxml_kind: MusicXML形式のコード種類（例: "major-seventh", "power"）
        - degree_element: 追加音や変更音を表すXML要素（ない場合はNone）
        - standard_chordname_text: 標準的なコード表記（例: "M7"）（ない場合はNone）
    
    Notes
    -----
    コード名を解析し、MusicXML形式のコード種類情報を生成する。
    特殊なコード（augmented, power, dim, maj7, mM7など）や追加音（add9, add♭7など）に対応。
    """
    # Chord Kind（コードの種類）を切り出す
    chord_kind = getChordKind(chord_name)
    
    result = ""
    degree = None
    standard_chordname_text = None

    # 特殊なコードの処理
    if "+" in chord_kind:
        if chord_kind == "+":  # "+"のみの場合は"aug"とする
            result = "aug"
        else:
            chord_kind = chord_kind.replace("+", "")
            if chord_kind == "7":
                result = "aug7"
            else:
                result = "aug"
    elif "power" in chord_kind:
        result = "power"
    elif "dim" in chord_kind:
        result = "dim"
    elif chord_kind == "maj7":
        result = "major-seventh"
        standard_chordname_text = "M7"
    elif chord_kind == "mM7":
        result = "major-minor"
        standard_chordname_text = "mM7"

    # 追加音の処理
    if "add" in chord_kind:
        add_note = chord_kind.split("add")[1]
        root = chord_name.split("add")[0]

        # chordroot要素だけを切り出し
        root = getChordRoot(root)

        add_note_list = [add_note]
        if "," in add_note:
            add_note_list = add_note.split(",")
            result += "(add"
        else:
            result += "add"

        # 追加音の処理
        length = len(add_note_list)
        for i, an in enumerate(add_note_list):
            if find_pitch_interval(root, an) == 2:
                result += "9"
            elif find_pitch_interval(root, an) == 1:
                result += "♭9"
            elif find_pitch_interval(root, an) == 3:
                result += "#9"
            elif find_pitch_interval(root, an) == -1:  # 3音省略のpowerコードの場合などで発生
                result += "#7"
            elif find_pitch_interval(root, an) == -2:  # 3音省略のpowerコードの場合などで発生
                result += "♭7"
            if i == length - 1:
                if i != 0:
                    result += ")"
            else:
                result += ","
    else:
        result = chord_kind

    return result, degree, standard_chordname_text
