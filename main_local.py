"""
MusicXMLファイルからコード分析を行い、コード情報を追加したファイルを出力するスクリプト。
"""
from chord_analysis import getChordMinimumUnit, writeChordsToScore
from io import StringIO
import os
from typing import List, Union


def main() -> None:
    """
    メイン関数。
    
    MusicXMLファイルからコード情報を抽出し、コード情報を追加したファイルを出力します。
    """
    # 入力ファイル名
    score_name = "sample_akikaze.musicxml"
    
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

    # リソースを解放
    output.close()
    
    print(f"コード分析が完了しました。結果は {output_filename} に保存されました。")


if __name__ == "__main__":
    main()
