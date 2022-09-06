import os
from music21 import *
from xml.etree import ElementTree as et  # mxlは非対応
from fractions import Fraction as frac
from io import BytesIO
import urllib.parse

from typing import NewType

# INITIAL SETUP
# musescore directory : /Applications/MuseScore 3.app/Contents/MacOS/mscore
# us = environment.UserSettings()
# us.create()
# us['musicxmlPath'] = '/Applications/MuseScore 3.app/Contents/MacOS/mscore'
# us['musescoreDirectPNGPath'] = '/Applications/MuseScore 3.app/Contents/MacOS/mscore'

ENV = os.getenv("ENV")

def pitch_scale(pitch, alter):
    pitch_scale = ["C", "C#", "D", "D#", "E",
                   "F", "F#", "G", "G#", "A", "A#", "B"]
    ind = pitch_scale.index(pitch)
    return pitch_scale[ind+alter]


def getChordRoot(chord_name):
    if len(chord_name) == 1:
        return chord_name[0], 0
    elif chord_name[1] == "#":
        return chord_name[0], 1
    elif chord_name[1] == "b":
        return chord_name[0], -1
    else:
        return chord_name[0], 0


def converChordKind(chord_kind):
    if chord_kind == 'seventh-flat-five':
        musicxml_kind = 'dominant'
        '''
        <degree>
          <degree-value>5</degree-value>
          <degree-alter>-1</degree-alter>
          <degree-type>alter</degree-type>
        </degree>    
        '''
        degree = et.Element('degree')
        degree_value = et.SubElement(degree, 'degree-value')
        degree_value.text = '5'
        degree_alter = et.SubElement(degree, 'degree-alter')
        degree_alter.text = '-1'
        degree_type = et.SubElement(degree, 'degree-type')
        degree_type.text = 'alter'
        return musicxml_kind, degree
    elif chord_kind == 'augmented-major-11th':
        musicxml_kind = 'augmented'
        '''
        <degree>
          <degree-value>11</degree-value>
          <degree-alter>0</degree-alter>
          <degree-type text="add">add</degree-type>
        </degree>
        '''
        degree = et.Element('degree')
        degree_value = et.SubElement(degree, 'degree-value')
        degree_value.text = '11'
        degree_alter = et.SubElement(degree, 'degree-alter')
        degree_alter.text = '0'
        degree_type = et.SubElement(degree, 'degree-type')
        degree_type.text = 'add'
        return musicxml_kind, degree
    elif chord_kind == 'dominant-seventh':
        musicxml_kind = 'dominant'
        degree = None
        return musicxml_kind, degree
    elif chord_kind == 'half-diminished-minor-ninth':
        musicxml_kind = 'half-diminished'
        '''
        <degree>
          <degree-value>9</degree-value>
          <degree-alter>-1</degree-alter>
          <degree-type>add</degree-type>
        </degree>
        '''
        degree = et.Element('degree')
        degree_value = et.SubElement(degree, 'degree-value')
        degree_value.text = '9'
        degree_alter = et.SubElement(degree, 'degree-alter')
        degree_alter.text = '-1'
        degree_type = et.SubElement(degree, 'degree-type')
        degree_type.text = 'add'
        return musicxml_kind, degree
    elif chord_kind == 'half-diminished-seventh':
        musicxml_kind = 'half-diminished'
        degree = None
        return musicxml_kind, degree
    elif chord_kind == 'augmented-major-seventh':
        musicxml_kind = 'augmented'
        '''
        <degree>
          <degree-value>7</degree-value>
          <degree-alter>1</degree-alter>
          <degree-type>add</degree-type>
        </degree>
        '''
        degree = et.Element('degree')
        degree_value = et.SubElement(degree, 'degree-value')
        degree_value.text = '7'
        degree_alter = et.SubElement(degree, 'degree-alter')
        degree_alter.text = '1'
        degree_type = et.SubElement(degree, 'degree-type')
        degree_type.text = 'add'
        return musicxml_kind, degree
    else:
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

# 最小単位でコードを切り出して二次元配列化する
MeasureNumber = NewType('MeasureNumber', int)
Beat = NewType('Beat', float)
ChordName = tuple[str, str]
ChordUnit = tuple[MeasureNumber, Beat, ChordName]
def getChordMinimumUnit(score_url: str, head: int, tail: int, sameChordPass=1) -> list[ChordUnit]:
    if ENV == "local":
        full_score = converter.parse(score_url)
    else:
        full_score = converter.parse(urllib.parse.quote(score_url, safe='/:'))

    if tail == -1:
        tail = len(full_score.getElementsByClass(stream.Part)
                   [0].getElementsByClass(stream.Measure))

    excerpt = full_score.measures(head, tail)
    chfy = excerpt.chordify()
    chord_list = []
    for c in chfy.flat.getElementsByClass(chord.Chord):
        chord_name = harmony.chordSymbolFigureFromChord(c, True)
        # frac 分数で表記
        # c.beatの長さはベースとなる拍子（4/4, 6/8等）によって変化があるためquarterLengthを掛けることによって補正している
        # TODO 実際に該当の拍子の楽譜で試す
        beat = (frac(c.beat)-1) * c.beatDuration.quarterLength
        if chord_name[0] == 'Chord Symbol Cannot Be Identified':
            continue
        if sameChordPass == 1:
            # chord_list[-1][2]: １つ前に配列に追加したchord_name
            if len(chord_list) == 0 or chord_list[-1][2] != chord_name:
                chord_list.append([c.measureNumber, beat, chord_name])
        else:
            chord_list.append([c.measureNumber, beat, chord_name])
    # print(chord_list)
    return chord_list

# 今の小節から遡ってdivisionsを特定する
# divisionsが存在しないことはないと考えて良いので、実際はNoneはかえらない
def getDivisions(measures, measure_num):
    for i in range(measure_num, 0, -1):
        attr = measures[i-1].find('attributes')
        if attr != None:
            if attr.findtext('divisions') != None:
                return int(attr.findtext('divisions'))
    return None


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
    offset = et.SubElement(harmony,'offset')
    root_step = et.SubElement(root, 'root-step')
    root_alter = et.SubElement(root, 'root-alter')
    #root_step.text, root_alter.text = getChordRoot(chord_name[0])
    root_name, alter = getChordRoot(chord_name[0])
    root_step.text = root_name
    root_alter.text = str(alter)
    offset.text = str(offset_duration)
    kind = et.SubElement(harmony, 'kind')
    musicxml_kind, degree_element = converChordKind(chord_name[1])
    kind.text = musicxml_kind
    if degree_element != None:
        harmony.insert(list(harmony).index(kind)+1, degree_element)
    # et.dump(harmony)
    return harmony


def writeChord(score_file, chord_list, head, tail, chordOverwrite=1):

    tree = et.parse(score_file)
    root = tree.getroot()
    first_part = root.find('part')  # 一番最初のpartを取得
    first_part_measures = first_part.findall('measure')

    # chord_list
    # [[13, '1', 'B'], [14, '1 1/2', 'Bsus2'], [14, '2 1/2', 'B'], [14, '3 1/2', 'Bsus'],
    # [14, '4 1/2', 'B'], [15, '2', 'A#susaddG#,omitE#'], [15, '3', 'A#pedal'], [15, '4 1/2', 'D#susaddC#,omitA#']]

    if chordOverwrite == 1:
        for i in range(head, tail+1):
            for harmony in first_part_measures[i-1].findall('harmony'):
                first_part_measures[i-1].remove(harmony)

    for i in range(len(chord_list)):
        chord_measure = chord_list[i][0]
        chord_bar = chord_list[i][1]
        chord_name = chord_list[i][2]

        factor_num = len(first_part_measures[chord_measure-1])
        total_duration = 0 # 楽譜のどこまで見たかchord単位で記録
        divisions = getDivisions(first_part_measures, chord_measure)

        for j in range(factor_num):
            factor_tag = first_part_measures[chord_measure-1][j].tag
            # note, rest, harmony以外にもattribute等の属性がある
            if (factor_tag != 'note') & (factor_tag != 'rest') & (factor_tag != 'harmony'):
                continue
            if (chord_bar - total_duration) <= 0:  # chord検出位置に到達
                # print("{} - {} is write position on {}".format(chord_measure, total_duration, chord_name))
                # print("new harmony write")
                offset_duration = (chord_bar - total_duration) * divisions
                harmony_element = createHarmonyElement(chord_name, offset_duration)
                first_part_measures[chord_measure -
                                    1].insert(j, createHarmonyElement(chord_name, offset_duration))
                break
            else:
                if first_part_measures[chord_measure-1][j].findtext('duration') != None:
                    factor_duration = frac(
                        int(first_part_measures[chord_measure-1][j].findtext('duration')), divisions)
                    total_duration += factor_duration
    # return et.tostring(tree.getroot(), encoding='unicode')
    f = BytesIO()
    tree.write(f, encoding='UTF-8', xml_declaration=True)
    f.seek(0)
    return f.read().decode('UTF-8')
    # for i in range(len(measures)):
    # print(measures[i].find('harmony'))

# getMusicxmlPitch(score_name)


'''
for thisNote in excerpt.recurse().notes:
    print(thisNote)
    thisNote.addLyric("test")
excerpt.show()
'''
