from musicxml_chord_analysis import getChordMinimumUnit, writeChord
from io import StringIO
import os

def main():
    score_name = 'sample.musicxml'
    head = 1
    tail = -1
    chord_list = getChordMinimumUnit(score_name, head=head, tail=tail, sameChordPass=1)
    output = StringIO()
    output.write(writeChord(score_name, chord_list, head=head, tail=tail))

    os.makedirs("output/", exist_ok=True)
    with open(os.path.join("output/", "ChordAdd_"+score_name), "w") as f:
        f.write(output.getvalue())
    
    output.close()

if __name__ == "__main__":
    main()