"""
MusicXMLファイルの書き込み関連の関数を提供するモジュール。
"""
from typing import List, Union, BinaryIO
from xml.etree import ElementTree as et
from fractions import Fraction as frac
from io import BytesIO

from chord_analysis.musicxml.reader import getDivisions
from chord_analysis.musicxml.elements import createHarmonyElement


def writeChord(
    file_obj: BinaryIO, 
    chord_list: List[List[Union[int, float, str]]], 
    head: int, 
    tail: int, 
    overwrite_chords: bool = True
) -> str:
    """
    MusicXMLファイルオブジェクトにコード情報を記入して返す。

    Parameters
    ----------
    file_obj : BinaryIO
        MusicXMLファイルオブジェクト
    chord_list : List[List[Union[int, float, str]]]
        getChordMinimumUnit()で取得したコード情報のリスト
        各要素は [小節番号, 拍位置, コード名] の形式
    head : int
        書き込む小節の開始番号
    tail : int
        書き込む小節の終了番号（-1の場合は最後まで）
    overwrite_chords : bool, optional
        既存のコード情報を上書きするかどうか（デフォルト: True）

    Returns
    -------
    str
        コード情報が記入されたMusicXMLファイルの内容（文字列）
    """
    # ファイルオブジェクトの位置を先頭に戻す
    file_obj.seek(0)
    
    # MusicXMLファイルを解析し、ルート要素を取得
    tree = et.parse(file_obj)
    root = tree.getroot()

    # 最初のpart要素とその中のmeasure要素を取得
    first_part = root.find("part")
    first_part_measures = first_part.findall("measure")

    # overwrite_chordsがTrueの場合、既存のharmony要素を削除
    if overwrite_chords:
        for i in range(head, tail + 1):
            for harmony in first_part_measures[i - 1].findall("harmony"):
                first_part_measures[i - 1].remove(harmony)

    # コードリストを反復処理し、各コードを適切な位置に追加
    for chord_info in chord_list:
        measure_number, chord_position, chord_name = chord_info
        total_duration = frac(0)
        divisions = getDivisions(first_part_measures, measure_number)
        measure_elements = first_part_measures[measure_number - 1]

        for j, element in enumerate(measure_elements):
            element_tag = element.tag
            if element_tag not in ["note", "rest", "harmony"]:
                continue

            if (chord_position - total_duration) <= 0:
                offset_duration = (chord_position - total_duration) * divisions
                measure_elements.insert(
                    j, createHarmonyElement(chord_name, offset_duration)
                )
                break
            else:
                if element.findtext("duration") is not None:
                    element_duration = frac(element.findtext("duration")) / divisions
                    total_duration += element_duration

    # 結果のXMLを文字列として出力
    output_buffer = BytesIO()
    tree.write(output_buffer, encoding="UTF-8", xml_declaration=True)
    output_buffer.seek(0)
    return output_buffer.read().decode("UTF-8")


def writeChordsToScore(
    score_file: str, 
    chord_list: List[List[Union[int, float, str]]], 
    start_measure: int, 
    end_measure: int, 
    overwrite_chords: bool = True
) -> str:
    """
    MusicXMLファイルにコード情報を記入して返す。

    Parameters
    ----------
    score_file : str
        MusicXMLファイルのパス
    chord_list : List[List[Union[int, float, str]]]
        getChordMinimumUnit()で取得したコード情報のリスト
        各要素は [小節番号, 拍位置, コード名] の形式
        例: [[13, 1, 'B'], [14, 1.5, 'Bsus2'], [14, 2.5, 'B']]
    start_measure : int
        書き込む小節の開始番号
    end_measure : int
        書き込む小節の終了番号（-1の場合は最後まで）
    overwrite_chords : bool, optional
        既存のコード情報を上書きするかどうか（デフォルト: True）

    Returns
    -------
    str
        コード情報が記入されたMusicXMLファイルの内容（文字列）
    """
    # MusicXMLファイルを解析し、ルート要素を取得
    tree = et.parse(score_file)
    root = tree.getroot()

    # 最初のpart要素とその中のmeasure要素を取得
    first_part = root.find("part")
    first_part_measures = first_part.findall("measure")

    # overwrite_chordsがTrueの場合、既存のharmony要素を削除
    if overwrite_chords:
        for i in range(start_measure, end_measure + 1):
            for harmony in first_part_measures[i - 1].findall("harmony"):
                first_part_measures[i - 1].remove(harmony)

    # コードリストを反復処理し、各コードを適切な位置に追加
    for chord_info in chord_list:
        measure_number, chord_position, chord_name = chord_info
        total_duration = frac(0)
        divisions = getDivisions(first_part_measures, measure_number)
        measure_elements = first_part_measures[measure_number - 1]

        for j, element in enumerate(measure_elements):
            element_tag = element.tag
            if element_tag not in ["note", "rest", "harmony"]:
                continue

            if (chord_position - total_duration) <= 0:
                offset_duration = (chord_position - total_duration) * divisions
                measure_elements.insert(
                    j, createHarmonyElement(chord_name, offset_duration)
                )
                break
            else:
                if element.findtext("duration") is not None:
                    element_duration = frac(element.findtext("duration")) / divisions
                    total_duration += element_duration

    # 結果のXMLを文字列として出力
    output_buffer = BytesIO()
    tree.write(output_buffer, encoding="UTF-8", xml_declaration=True)
    output_buffer.seek(0)
    return output_buffer.read().decode("UTF-8")
