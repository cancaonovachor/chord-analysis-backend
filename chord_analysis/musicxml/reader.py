"""
MusicXMLファイルの読み込み関連の関数を提供するモジュール。
"""
import os
from typing import List, Optional, Union
from xml.etree import ElementTree as et

from chord_analysis.core.pitch_utils import pitch_scale


def getMusicxmlPitch(score_name: str) -> List[List[Union[float, str]]]:
    """
    MusicXMLファイルからピッチと休符の情報を取得する。

    Parameters
    ----------
    score_name : str
        MusicXMLファイルのパス

    Returns
    -------
    List[List[Union[float, str]]]
        各音符の拍とピッチ（または休符）のリスト
        各要素は [拍位置, ピッチ文字列] の形式
        例: [[1.0, "C4"], [2.0, "rest"], [3.0, "G4"]]
    
    Notes
    -----
    この関数は、MusicXMLファイルから音符と休符の情報を抽出し、
    各音符の拍位置とピッチ（または休符）をリストとして返します。
    """
    tree = et.parse(score_name)
    root = tree.getroot()
    parts = root.findall("part")
    
    result = []
    
    # 各パートをループ処理
    for p in range(len(parts)):
        part_measures = parts[p].findall("measure")
        
        # 各小節をループ処理
        for i in range(len(part_measures)):
            # divisionsを取得
            divisions = None
            if part_measures[i].find("attributes") is not None and part_measures[i].find("attributes").findtext("divisions") is not None:
                divisions = int(part_measures[i].find("attributes").findtext("divisions"))
            else:
                # 前の小節からdivisionsを探す
                divisions = getDivisions(part_measures, i + 1)
                if divisions is None:
                    continue  # divisionsが見つからない場合はスキップ
            
            note_list = part_measures[i].findall("note")
            chord_list = []
            
            # 各音符をループ処理
            for j in range(len(note_list)):
                rest = note_list[j].find("rest")
                pitch = note_list[j].find("pitch")
                
                if note_list[j].findtext("duration") is None:
                    continue  # durationがない場合はスキップ
                    
                duration = int(note_list[j].findtext("duration"))
                bar = duration / divisions  # 拍位置を計算
                
                # ピッチがある場合
                if pitch is not None:
                    raw_pitch = pitch.findtext("step")
                    alter = pitch.findtext("alter")
                    octave = pitch.findtext("octave")
                    
                    # 変化記号がある場合
                    if alter is not None:
                        pitch_str = pitch_scale(raw_pitch, int(alter)) + octave
                    else:
                        pitch_str = raw_pitch + octave
                        
                    chord_list.append([bar, pitch_str])
                
                # 休符がある場合
                if rest is not None:
                    chord_list.append([bar, "rest"])
            
            result.extend(chord_list)
    
    return result


def getDivisions(measures: List[et.Element], measure_num: int) -> Optional[int]:
    """
    指定された小節から、遡ってdivisionsを特定する。

    Parameters
    ----------
    measures : List[et.Element]
        小節のXMLエレメントのリスト
    measure_num : int
        divisionsを特定する小節の番号

    Returns
    -------
    Optional[int]
        divisionsの値。見つからない場合はNone
    
    Notes
    -----
    divisionsは4分音符を何分割して数えるかを示す値。
    指定された小節にdivisionsがない場合は、前の小節を遡って探す。
    """
    divisions = None
    for i in range(measure_num, 0, -1):
        attributes = measures[i - 1].find("attributes")
        if attributes is not None:
            divisions = attributes.findtext("divisions")
        if divisions is None:
            continue
        else:
            break
    return int(divisions) if divisions is not None else None
