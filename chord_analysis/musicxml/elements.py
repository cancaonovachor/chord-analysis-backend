"""
MusicXML要素の作成関連の関数を提供するモジュール。
"""
from typing import List, Optional
from xml.etree import ElementTree as et

from chord_analysis.core.chord_parser import getChordRootAndBass, convertChordKind


def createHarmonyElement(chord_name: List[str], offset_duration: int) -> et.Element:
    """
    コード情報からMusicXMLのharmony要素を作成する。

    Parameters
    ----------
    chord_name : List[str]
        コード名のリスト（例: ["Cmaj7"]）
    offset_duration : int
        オフセット（位置）の値

    Returns
    -------
    et.Element
        MusicXMLのharmony要素

    Notes
    -----
    MusicXMLのharmony要素の例:
    <harmony print-frame="no" placement="above">
        <root>
            <root-step>B</root-step>
            <root-alter>-1</root-alter>
        </root>
        <kind halign="center" text="M7">major-seventh</kind>
        <bass>
            <bass-step>E</bass-step>
            <bass-alter>0</bass-alter>
        </bass>
        <offset>0</offset>
    </harmony>
    """
    harmony = et.Element("harmony")

    # ルート音の設定
    root = et.SubElement(harmony, "root")
    root_step = et.SubElement(root, "root-step")
    root_alter_elem = et.SubElement(root, "root-alter")
    
    # コード名からルート音とベース音を抽出
    root_name, root_alter, bass_name, bass_alter = getChordRootAndBass(chord_name[0])
    root_step.text = root_name
    root_alter_elem.text = str(root_alter)

    # コードの種類の設定
    kind = et.SubElement(harmony, "kind")
    musicxml_kind, degree_element, standard_chordname_text = convertChordKind(
        chord_name[0]
    )
    kind.text = musicxml_kind

    # ベース音がある場合（分数コード）
    if bass_name is not None:
        bass = et.SubElement(harmony, "bass")
        bass_step = et.SubElement(bass, "bass-step")
        bass_step.text = bass_name
        bass_alter_elem = et.SubElement(bass, "bass-alter")
        bass_alter_elem.text = str(bass_alter)

    # オフセット（位置）の設定
    offset = et.SubElement(harmony, "offset")
    offset.text = str(offset_duration)

    # 追加要素の設定
    if degree_element is not None:
        harmony.insert(list(harmony).index(kind) + 1, degree_element)
    if standard_chordname_text is not None:
        kind.set("text", standard_chordname_text)
        
    return harmony
