"""
MusicXMLファイルからコード分析を行うパッケージ。
コードの抽出、分析、MusicXMLへの書き込みなどの機能を提供します。
"""

from chord_analysis.core.chord_parser import getChordRoot, getChordKind, getChordRootAndBass, convertChordKind
from chord_analysis.core.pitch_utils import find_pitch_interval, pitch_scale, get_alteration
from chord_analysis.musicxml.reader import getMusicxmlPitch, getDivisions
from chord_analysis.musicxml.elements import createHarmonyElement
from chord_analysis.musicxml.writer import writeChordsToScore, writeChord
from chord_analysis.analysis.chord_extractor import getChordMinimumUnit

__all__ = [
    'getChordRoot',
    'getChordKind',
    'getChordRootAndBass',
    'convertChordKind',
    'find_pitch_interval',
    'pitch_scale',
    'get_alteration',
    'getMusicxmlPitch',
    'getDivisions',
    'createHarmonyElement',
    'writeChordsToScore',
    'writeChord',
    'getChordMinimumUnit',
]
