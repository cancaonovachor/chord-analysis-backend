# MusicXML コード分析モジュール

このドキュメントでは、`musicxml_chord_analysis.py`と`main_local.py`の機能と使用方法について説明します。

## 概要

このモジュールは、MusicXMLファイルからコード情報を抽出し、分析し、コード情報を追加したMusicXMLファイルを生成する機能を提供します。主に以下の機能があります：

1. MusicXMLファイルからコード情報を抽出
2. コード名の解析（ルート音、ベース音、コードの種類など）
3. コード情報のMusicXML形式への変換
4. コード情報のMusicXMLファイルへの書き込み

## 主要な機能

### 1. コード情報の抽出

`getChordMinimumUnit`関数は、MusicXMLファイルから指定された小節範囲のコード情報を抽出します。

```python
def getChordMinimumUnit(score_url: str, head: int, tail: int, sameChordPass: int = 1)
```

- **入力**：
  - `score_url`: MusicXMLファイルのパス
  - `head`: 抽出開始小節番号
  - `tail`: 抽出終了小節番号（-1で最後まで）
  - `sameChordPass`: 同じコードが連続する場合の処理方法（1: 最初のみ抽出、0: すべて抽出）

- **出力**：
  - コード情報のリスト（各要素は [小節番号, 拍位置, コード名]）

### 2. コード名の解析

コード名を解析するための複数の関数が提供されています：

- `getChordRoot`: コード名からルート音を抽出
- `getChordKind`: コード名からコードの種類を抽出
- `getChordRootAndBass`: コード名からルート音とベース音を抽出
- `convertChordKind`: コード名からMusicXML形式のコード種類情報を生成

例えば、`getChordRootAndBass`関数は以下のように動作します：

```python
def getChordRootAndBass(chord_name: str)
```

- **入力**：
  - `chord_name`: コード名（例: "G#maj7", "Cm7/E-"）

- **出力**：
  - ルート音の文字, ルート音の変化記号の値, ベース音の文字, ベース音の変化記号の値

### 3. MusicXML形式への変換

`createHarmonyElement`関数は、コード情報からMusicXMLのharmony要素を作成します。

```python
def createHarmonyElement(chord_name: List[str], offset_duration: int)
```

- **入力**：
  - `chord_name`: コード名のリスト
  - `offset_duration`: オフセット（位置）の値

- **出力**：
  - MusicXMLのharmony要素（XMLエレメント）

### 4. MusicXMLファイルへの書き込み

`writeChordsToScore`関数は、コード情報をMusicXMLファイルに書き込みます。

```python
def writeChordsToScore(score_file: str, chord_list: List[List[Union[int, float, str]]], start_measure: int, end_measure: int, overwrite_chords: bool = True)
```

- **入力**：
  - `score_file`: MusicXMLファイルのパス
  - `chord_list`: コード情報のリスト
  - `start_measure`: 書き込み開始小節番号
  - `end_measure`: 書き込み終了小節番号
  - `overwrite_chords`: 既存のコード情報を上書きするかどうか

- **出力**：
  - コード情報が記入されたMusicXMLファイルの内容（文字列）

## 補助機能

### 音程計算

`find_pitch_interval`関数と`pitch_scale`関数は、音程の計算や音名の変換を行います。

```python
def find_pitch_interval(root: str, add_note: str)
def pitch_scale(pitch: str, alter: int)
```

### MusicXMLの解析

`getMusicxmlPitch`関数と`getDivisions`関数は、MusicXMLファイルからピッチ情報やdivisions値を取得します。

```python
def getMusicxmlPitch(score_name: str)
def getDivisions(measures: List[et.Element], measure_num: int)
```

## 使用例

`main_local.py`ファイルは、このモジュールの使用例を示しています。

```python
def main():
    # 入力ファイル名
    score_name = "chordslist.musicxml"
    
    # 分析対象の小節範囲
    head = 1  # 開始小節
    tail = -1  # 終了小節（-1は最後まで）
    
    # コード情報を抽出
    chord_list = getChordMinimumUnit(
        score_name, 
        head=head, 
        tail=tail, 
        sameChordPass=0  # 同じコードが連続しても全て抽出
    )
    
    # コード情報を追加したMusicXMLを生成
    output = StringIO()
    output.write(
        writeChordsToScore(
            score_name, 
            chord_list, 
            start_measure=head, 
            end_measure=tail
        )
    )

    # 出力ディレクトリを作成
    os.makedirs("output/", exist_ok=True)
    
    # 結果を保存
    output_filename = os.path.join("output/", "ChordAdd_" + score_name)
    with open(output_filename, "w") as f:
        f.write(output.getvalue())
```

## 技術的詳細

### コード表現

コードは以下の要素で表現されます：

- **ルート音**: コードの基本となる音（例: C, F#）
- **コードの種類**: メジャー、マイナー、7thなど（例: maj7, m7）
- **ベース音**: 分数コードの場合のベース音（例: C/G のGの部分）
- **追加音**: コードに追加される音（例: add9, add♭7）

### MusicXML表現

MusicXMLでは、コードは以下の要素で表現されます：

```xml
<harmony>
  <root>
    <root-step>C</root-step>
    <root-alter>0</root-alter>
  </root>
  <kind>major</kind>
  <bass>
    <bass-step>G</bass-step>
    <bass-alter>0</bass-alter>
  </bass>
  <offset>0</offset>
</harmony>
```

## 注意点

- このモジュールは、構成音が3つ未満のコードや識別できないコードはスキップします。
- 環境変数`ENV`が"local"の場合、ローカルファイルパスとして扱います。それ以外の場合はURLとして扱います。
