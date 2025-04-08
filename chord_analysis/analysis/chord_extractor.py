"""
コード情報の抽出関連の関数を提供するモジュール。
"""
import os
import urllib.parse
from typing import List, Union
from fractions import Fraction as frac

from music21 import converter, stream, chord, harmony


# 環境変数
ENV = os.getenv("ENV", "local")


def getChordMinimumUnit(score_url: str, head: int, tail: int, sameChordPass: int = 1) -> List[List[Union[int, float, str]]]:
    """
    指定された楽譜の一部を抽出し、コードリストを取得する。

    Parameters
    ----------
    score_url : str
        楽譜のURL。"local"が指定された場合はローカルのファイルパス
    head : int
        抽出する先頭小節番号
    tail : int
        抽出する末尾小節番号。-1が指定された場合は、全小節を対象にする
    sameChordPass : int, optional
        同じ和音が連続した場合はパスする（1）か否か（0）を設定する（デフォルト: 1）

    Returns
    -------
    List[List[Union[int, float, str]]]
        抽出した和音リスト
        各要素は [小節番号, 拍位置, コード名] の形式
        例: [[13, 1, 'B'], [14, 1.5, 'Bsus2'], [14, 2.5, 'B']]
    
    Notes
    -----
    この関数は、楽譜から和音情報を抽出し、小節番号、拍位置、コード名のリストとして返します。
    構成音が3つ未満のコードや識別できないコードはスキップされます。
    sameChordPassが1の場合、同じコードが連続する場合は最初の1つだけが含まれます。
    """
    full_score = (
        converter.parse(score_url)
        if ENV == "local"
        else converter.parse(urllib.parse.quote(score_url, safe="/:"))
    )

    if tail == -1:
        tail = len(
            full_score.getElementsByClass(stream.Part)[0].getElementsByClass(
                stream.Measure
            )
        )
    excerpt = full_score.measures(head, tail)
    chfy = excerpt.chordify()
    chord_list = []
    for c in chfy.flat.getElementsByClass(chord.Chord):
        # 構成音が3つ未満の場合はスキップする
        if len(c.normalOrder) < 3:
            continue
        chord_name = harmony.chordSymbolFigureFromChord(c, True)
        beat = (frac(c.beat) - 1) * c.beatDuration.quarterLength
        if chord_name[0] == "Chord Symbol Cannot Be Identified":
            continue
        if sameChordPass == 1:
            if not chord_list or chord_list[-1][2] != chord_name:
                chord_list.append([c.measureNumber, beat, chord_name])
        else:
            chord_list.append([c.measureNumber, beat, chord_name])
    return chord_list
