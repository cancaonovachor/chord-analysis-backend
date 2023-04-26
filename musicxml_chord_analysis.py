#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from music21 import *
from xml.etree import ElementTree as et  # mxlは非対応
from fractions import Fraction as frac
from io import BytesIO
import urllib.parse
import typing

# INITIAL SETUP
# musescore directory : /Applications/MuseScore 3.app/Contents/MacOS/mscore
# us = environment.UserSettings()
# us.create()
# us['musicxmlPath'] = '/Applications/MuseScore 3.app/Contents/MacOS/mscore'
# us['musescoreDirectPNGPath'] = '/Applications/MuseScore 3.app/Contents/MacOS/mscore'

ENV = os.getenv("ENV")

pitch_scale_dict = {
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
    "A##": 11
}


def find_pitch_interval(root, add_note):
    pitch_scale_dict = {
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
        "A##": 11

    }
    interval = pitch_scale_dict[add_note] - pitch_scale_dict[root]
    # 絶対値を出す
    # 12を越えることが存在しないので不要？
    # return interval % 12
    return interval


def pitch_scale(pitch, alter):
    pitch_scale = ["C", "C#", "D", "D#", "E",
                   "F", "F#", "G", "G#", "A", "A#", "B"]
    ind = pitch_scale.index(pitch)
    return pitch_scale[ind+alter]


def getChordRoot(s):  # -> tuple[str]:
    # ex) G#power -> G#
    # ex) G--dim -> G--
    # 戻り値： 根音+変位の文字列、（root,alterの２つを返すわけではない）
    # TODO: 後々、根音の戻り値を統一しておく必要がある。

    result = s[0]
    # 先頭3文字 or chord root要素と関係ないものが来るまで繰り返し
    for i in range(1, min(3, len(s))):
        # - or # が来たらそれも追加
        if s[i] in {"#", "-"}:
            result += s[i]
        else:
            break
    return result


def getChordKind(chord_name: str):  # -> tuple[str, str]:
    # root以外を切り出す
    # 1文字の場合は空で返す
    if len(chord_name) == 1:
        return ''
    # 1文字目以外を切り出す

    chord_kind = chord_name[1:]
    # 1文字目が#か-の場合は2文字目も切り出す
    if chord_kind[0] == '#':
        chord_kind = chord_kind[1:]
    elif chord_kind[0] == '-':
        chord_kind = chord_kind[1:]

    chord_kind = chord_kind.split("/")[0]  # 分数コードを削除
    return chord_kind


def get_alteration(note: str) -> int:
    # 音符の変更記号を返す関数（シャープ: 1, フラット: -1, なし: 0）
    if len(note) == 1:
        return 0
    elif note[1] == "#":
        return 1
    elif note[1] == "b":
        return -1
    else:
        return 0


def getChordRootAndBass(chord_name: str) -> tuple[str, int, str | None, int | None]:
    # コード名からルート音とベース音を抽出する関数
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


def convertChordKind(chord_name: str):
    # 戻り値：musicxml_kind, degree_element, standard_chordname_text
    # musicxml_kind: chord_kind、コードの種類
    # degree_element:
    # standard_chordname_text: musicxmlの表記
    # ex)
    # GpoweraddF -> chord_kind:poweraddF, standard_chordname_text:G5add-7
    print("chord_name: "+chord_name)

    # Chord Kind（コードの種類）を切り出す
    chord_kind = getChordKind(chord_name)
    print("chord_kind: "+chord_kind)

    result = ''
    degree = None
    standard_chordname_text = None

    if '+' in chord_kind:
        if chord_kind == '+':  # "+"のみの場合は"aug"とする
            result = 'aug'
        else:
            chord_kind = chord_kind.replace('+', '')
            if chord_kind == '7':
                result = 'aug7'
            else:
                result = 'aug'  # TODO: augの他のパターンがあれば追加必要
    elif 'power' in chord_kind:
        result = 'power'
    elif 'dim' in chord_kind:
        result = 'dim'
    elif chord_kind == 'maj7':
        result = 'major-seventh'
        standard_chordname_text = 'M7'
    elif chord_kind == 'mM7':
        result = 'major-minor'
        standard_chordname_text = 'mM7'

    if 'add' in chord_kind:
        add_note = chord_kind.split("add")[1]
        root = chord_name.split("add")[0]
        print("root: "+root)

        # chordroot要素だけを切り出し
        root = getChordRoot(root)

        add_note_list = [add_note]
        if "," in add_note:
            add_note_list = add_note.split(",")
            result += '(add'
        else:
            result += 'add'

        # TODO addが複数ある場合、ソートが必要
        # ex) add♭9,♭7 になるが、add♭7,♭9 にしたい
        length = len(add_note_list)
        for i, an in enumerate(add_note_list):
            if find_pitch_interval(root, an) == 2:
                result += '9'
            elif find_pitch_interval(root, an) == 1:
                result += '♭9'
            elif find_pitch_interval(root, an) == 3:
                result += '#9'
            elif find_pitch_interval(root, an) == -1:  # 3音省略のpowerコードの場合などで発生
                result += '#7'
            elif find_pitch_interval(root, an) == -2:  # 3音省略のpowerコードの場合などで発生
                result += '♭7'
            if i == length - 1:
                if i != 0:
                    result += ')'
            else:
                result += ','
    else:
        result = chord_kind

    return result, degree, standard_chordname_text

    # if chord_kind == 'seventh-flat-five':
    #     musicxml_kind = 'dominant'
    #     '''
    #     <degree>
    #       <degree-value>5</degree-value>
    #       <degree-alter>-1</degree-alter>
    #       <degree-type>alter</degree-type>
    #     </degree>
    #     '''
    #     degree = et.Element('degree')
    #     degree_value = et.SubElement(degree, 'degree-value')
    #     degree_value.text = '5'
    #     degree_alter = et.SubElement(degree, 'degree-alter')
    #     degree_alter.text = '-1'
    #     degree_type = et.SubElement(degree, 'degree-type')
    #     degree_type.text = 'alter'
    #     return musicxml_kind, degree
    # elif chord_kind == 'augmented-major-11th':
    #     musicxml_kind = 'augmented'
    #     '''
    #     <degree>
    #       <degree-value>11</degree-value>
    #       <degree-alter>0</degree-alter>
    #       <degree-type text="add">add</degree-type>
    #     </degree>
    #     '''
    #     degree = et.Element('degree')
    #     degree_value = et.SubElement(degree, 'degree-value')
    #     degree_value.text = '11'
    #     degree_alter = et.SubElement(degree, 'degree-alter')
    #     degree_alter.text = '0'
    #     degree_type = et.SubElement(degree, 'degree-type')
    #     degree_type.text = 'add'
    #     return musicxml_kind, degree
    # elif chord_kind == 'dominant-seventh':
    #     musicxml_kind = 'dominant'
    #     degree = None
    #     return musicxml_kind, degree
    # elif chord_kind == 'half-diminished-minor-ninth':
    #     musicxml_kind = 'half-diminished'
    #     '''
    #     <degree>
    #       <degree-value>9</degree-value>
    #       <degree-alter>-1</degree-alter>
    #       <degree-type>add</degree-type>
    #     </degree>
    #     '''
    #     degree = et.Element('degree')
    #     degree_value = et.SubElement(degree, 'degree-value')
    #     degree_value.text = '9'
    #     degree_alter = et.SubElement(degree, 'degree-alter')
    #     degree_alter.text = '-1'
    #     degree_type = et.SubElement(degree, 'degree-type')
    #     degree_type.text = 'add'
    #     return musicxml_kind, degree
    # elif chord_kind == 'half-diminished-seventh':
    #     musicxml_kind = 'half-diminished'
    #     degree = None
    #     return musicxml_kind, degree
    # elif chord_kind == 'augmented-major-seventh':
    #     musicxml_kind = 'augmented'
    #     '''
    #     <degree>
    #       <degree-value>7</degree-value>
    #       <degree-alter>1</degree-alter>
    #       <degree-type>add</degree-type>
    #     </degree>
    #     '''
    #     degree = et.Element('degree')
    #     degree_value = et.SubElement(degree, 'degree-value')
    #     degree_value.text = '7'
    #     degree_alter = et.SubElement(degree, 'degree-alter')
    #     degree_alter.text = '1'
    #     degree_type = et.SubElement(degree, 'degree-type')
    #     degree_type.text = 'add'
    #     return musicxml_kind, degree
    # else:
    return chord_kind, None


def getMusicxmlPitch(score_name):
    tree = et.parse(score_name)
    root = tree.getroot()
    parts = root.findall('part')

    for p in range(len(len(parts))):
        part_measures = parts[p].findall('measure')
        for i in range(len(part_measures)):
            if part_measures[i].find('attributes').findtext('divisions') is not None:
                divisions = int(part_measures[i].find('attributes').findtext(
                    'divisions'))  # ４分音符を小節内で何分割して数えているかの値、
                # divisionsは新しい値が定義されるまで小節超えて継承される
            note_list = part_measures[i].findall('note')
            # print("{}小節目".format(i+1))
            chord_list = []
            for j in range(len(note_list)):
                rest = note_list[j].find('rest')
                pitch = note_list[j].find('pitch')
                duration = int(note_list[j].findtext('duration'))
                bar = duration/divisions

                if pitch is not None:
                    raw_pitch = pitch.findtext('step')
                    alter = pitch.findtext('alter')
                    octave = pitch.findtext('octave')
                    if alter is not None:
                        pitch_str = pitch_scale(raw_pitch, int(alter)) + octave
                    else:
                        pitch_str = raw_pitch + octave
                    # print("{}が{}拍分".format(pitch_str,bar))
                    chord_list.append([bar, pitch_str])
                if rest is not None:
                    # print("休符が{}拍分".format(bar))
                    chord_list.append([bar, "rest"])
            # print(chord_list)


def getChordMinimumUnit(score_url: str, head: int, tail: int, sameChordPass=1):
    """
    指定された楽譜の一部を抽出し、chord_listを取得する。

    Parameters
    ----------
        score_url (str) : 楽譜のURL。"local"が指定された場合はローカルのファイルパス。
        head (int) : 抽出する先頭小節番号。
        tail (int) : 抽出する末尾小節番号。-1が指定された場合は、全小節を対象にする。
        sameChordPass (int, optional) : 同じ和音が連続した場合はパスする（１）か否か（０）を設定する。デフォルトは１。
    Returns    
    ----------  
        chord_list (list) : 抽出した和音リスト。以下の要素を持つリストである。
            - 小節番号 (int)
            - 拍 (float)
            - 和音名 (str)
            ex)
            [[13, '1', 'B'], [14, '1 1/2', 'Bsus2'], [14, '2 1/2', 'B'], [14, '3 1/2', 'Bsus'],
            [14, '4 1/2', 'B'], [15, '2', 'A#susaddG#,omitE#'], [15, '3', 'A#pedal'], [15, '4 1/2', 'D#susaddC#,omitA#']]
    """
    full_score = converter.parse(score_url) if ENV == "local" else converter.parse(
        urllib.parse.quote(score_url, safe='/:'))

    if tail == -1:
        tail = len(full_score.getElementsByClass(stream.Part)
                   [0].getElementsByClass(stream.Measure))
    excerpt = full_score.measures(head, tail)
    chfy = excerpt.chordify()
    chord_list = []
    for c in chfy.flat.getElementsByClass(chord.Chord):
        # 構成音が3つ未満の場合はスキップする
        if len(c.normalOrder) < 3:
            continue
        chord_name = harmony.chordSymbolFigureFromChord(c, True)
        beat = (frac(c.beat)-1) * c.beatDuration.quarterLength
        if chord_name[0] == 'Chord Symbol Cannot Be Identified':
            continue
        if sameChordPass == 1:
            if not chord_list or chord_list[-1][2] != chord_name:
                chord_list.append([c.measureNumber, beat, chord_name])
        else:
            chord_list.append([c.measureNumber, beat, chord_name])
    return chord_list


def getDivisions(measures, measure_num):
    """
    概要:
        指定された小節から、遡ってdivisionsを特定する。
    引数:
        measures (List[xml.etree.ElementTree.Element]) : 小節のXMLエレメントのリスト。
        measure_num (int) : divisionsを特定する小節の番号。
    戻り値:
        int : divisionsの値。
    """
    divisions = None
    for i in range(measure_num, 0, -1):
        attributes = measures[i - 1].find('attributes')
        if attributes is not None:
            divisions = attributes.findtext('divisions')
        if divisions is None:
            continue
        else:
            break
    return int(divisions) if divisions is not None else None


def createHarmonyElement(chord_name, offset_duration):
    '''
    # print-frame: ギター譜用のフレット表示 yes/no
    # pacement: 表示位置??
    <harmony print-frame="no" placement="above">
        <root>
            <root-step>B</root-step>
        </root>
        <kind>major</kind>
        <staff>1</staff>
    </harmony>
      <harmony default-y="34" font-family="Arial" font-size="10.6">
        <root>
          <root-step>B</root-step>
          <root-alter>-1</root-alter>
        </root>
        <kind halign="center" text="M7">major-seventh</kind>
      </harmony>
    '''
    harmony = et.Element('harmony')

    root = et.SubElement(harmony, 'root')
    root_step = et.SubElement(root, 'root-step')
    root_alter_elem = et.SubElement(root, 'root-alter')
    # root_step.text, root_alter.text = getChordRoot(chord_name[0])
    root_name, root_alter, bass_name, bass_alter = getChordRootAndBass(
        chord_name[0])
    root_step.text = root_name
    root_alter_elem.text = str(root_alter)

    kind = et.SubElement(harmony, 'kind')
    print(chord_name[0])
    musicxml_kind, degree_element, standard_chordname_text = convertChordKind(
        chord_name[0])
    print(musicxml_kind, degree_element, standard_chordname_text)
    # musicxml_kind = "5(add♭7♭9)"
    kind.text = musicxml_kind

    if bass_name is not None:
        bass = et.SubElement(harmony, 'bass')
        bass_step = et.SubElement(bass, 'bass-step')
        bass_step.text = bass_name
        bass_alter_elem = et.SubElement(bass, 'bass-alter')
        bass_alter_elem.text = str(bass_alter)

    offset = et.SubElement(harmony, 'offset')
    offset.text = str(offset_duration)

    if degree_element != None:
        harmony.insert(list(harmony).index(kind)+1, degree_element)
    if standard_chordname_text != None:
        kind.set('text', standard_chordname_text)
    # et.dump(harmony)
    return harmony


def writeChord(score_file, chord_list, head, tail, chordOverwrite=1):
    '''
    xmlファイルにコード情報を記入してかえす。

    Parameters
    ----------
    score_file      str
                    xmlファイルのpath
    chord_list      list
                    getChordMinimumUnit()で取得したchord情報
                    ex)
                    [[13, '1', 'B'], [14, '1 1/2', 'Bsus2'], [14, '2 1/2', 'B'], [14, '3 1/2', 'Bsus'],
                    [14, '4 1/2', 'B'], [15, '2', 'A#susaddG#,omitE#'], [15, '3', 'A#pedal'], [15, '4 1/2', 'D#susaddC#,omitA#']]
    head            int
                    書き込む小節の開始番号
    tail            int
                    書き込む小節の終了番号                
    chordOverwrite  bool
                    すでにxmlにコード情報があった時に上書きする（1）か否か（0）
    Returns    
    ----------     
    str?
                    コード情報を記入されたxmlファイル
    '''
    tree = et.parse(score_file)
    root = tree.getroot()
    first_part = root.find('part')  # 一番最初のpart要素を取得, TTBBならT1
    first_part_measures = first_part.findall('measure')  # 一番最初のmeasure要素を取得

    if chordOverwrite:
        for i in range(head, tail+1):
            for harmony in first_part_measures[i-1].findall('harmony'):
                first_part_measures[i-1].remove(harmony)

    for i in range(len(chord_list)):
        chord_measure = chord_list[i][0]
        chord_bar = frac(chord_list[i][1])
        chord_name = chord_list[i][2]
        total_duration = frac(0)
        divisions = getDivisions(first_part_measures, chord_measure)
        for j, factor_elem in enumerate(first_part_measures[chord_measure-1]):
            factor_tag = factor_elem.tag
            # note, rest, harmony以外のattribute等の属性を無視
            if factor_tag not in ['note', 'rest', 'harmony']:
                continue
            if (chord_bar - total_duration) <= 0:  # chord検出位置に到達
                print(str(chord_measure)+"小節")
                offset_duration = (chord_bar - total_duration) * divisions
                first_part_measures[chord_measure -
                                    1].insert(j, createHarmonyElement(chord_name, offset_duration))
                break
            else:
                if factor_elem.findtext('duration') is not None:
                    factor_duration = frac(
                        factor_elem.findtext('duration')) / divisions
                    total_duration += factor_duration
    f = BytesIO()
    tree.write(f, encoding='UTF-8', xml_declaration=True)
    f.seek(0)
    return f.read().decode('UTF-8')

# getMusicxmlPitch(score_name)


'''
for thisNote in excerpt.recurse().notes:
    print(thisNote)
    thisNote.addLyric("test")
excerpt.show()
'''
