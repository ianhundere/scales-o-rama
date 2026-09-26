import re

scales = {
    'major': ['CDEFGAB', 'GABCDEF#', 'DEF#GABC#', 'ABC#DEF#G#', 'EF#G#ABC#D#',
              'BC#D#EF#G#A#', 'F#G#A#BC#D#E#', 'DbEbFGbAbBbC', 'AbBbCDbEbFG',
              'EbFGAbBbCD', 'BbCDEbFGA', 'FGABbCDE'],
    'minor': ['CDEbFGAbBb', 'GABbCDEbF', 'DEFGABbC', 'ABCDEFG', 'EF#GABCD',
              'BC#DEF#GA', 'F#G#ABC#DE', 'C#D#EF#G#AB', 'G#A#BC#D#EF#',
              'EbFGbAbBbCbDb', 'BbCDbEbFGbAb', 'FGAbBbCDbEb'],
    'dorian': ['CDEbFGABb', 'C#D#EF#G#A#B', 'DEFGABC', 'D#E#F#G#A#B#C#', 'EF#GABC#D',
               'FGAbBbCDEb', 'F#G#ABC#D#E', 'GABbCDEF', 'G#A#BC#D#E#F#', 'ABCDEF#G',
               'A#B#C#D#E#F##G#', 'BC#DEF#G#A'],
    'phrygian': ['CDbEbFGAbBb', 'C#DEF#G#AB', 'DEbFGABbC', 'D#EF#G#A#BC#',
                 'EFGABCD', 'FGbAbBbCDbEb', 'F#GABC#DE', 'GAbBbCDEbF',
                 'G#ABC#D#EF#', 'ABbCDEFG', 'A#BC#D#E#F#G#', 'BCDEF#GA'],
    'lydian': ['CDEF#GAB', 'C#D#E#F##G#A#B#', 'DEF#G#ABC#', 'D#E#F##G##A#B#C##',
               'EF#G#A#BC#D#', 'FGABCDE', 'F#G#A#B#C#D#E#', 'GABC#DEF#',
               'G#A#B#C##D#E#F##', 'ABC#D#EF#G#', 'BbCDEFGA', 'BC#D#E#F#G#A#'],
    'mixolydian': ['CDEFGABb', 'C#D#E#F#G#A#B', 'DEF#GABC', 'D#E#F##G#A#B#C#',
                   'EF#G#ABC#D', 'FGABbCDEb', 'F#G#A#BC#D#E', 'GABCDEF',
                   'G#A#B#C#D#E#F#', 'ABC#DEF#G', 'A#B#C##D#E#F##G#',
                   'BC#D#EF#G#A'],
    'aeolian': ['CDEbFGAbBb', 'C#D#EF#G#AB', 'DEFGABbC', 'EbFGbAbBbCbDb', 'EF#GABCD',
                'FGAbBbCDbEb', 'F#G#ABC#DE', 'GABbCDEbF', 'G#A#BC#D#EF#', 'ABCDEFG',
                'BbCDbEbFGbAb', 'BC#DEF#GA'],
    'locrian': ['CDbEbFGbAbBb', 'C#DEF#GAB', 'DEbFGAbBbC', 'EbFbGbAbBbbCbDb', 'EFGABbCD',
                'FGbAbBbCbDbEb', 'F#GABCDE', 'GAbBbCDbEbF', 'G#ABC#DEF#', 'ABbCDEbFG',
                'A#BC#D#EF#G#', 'BCDEFGA'],
}

# one note: A-G + optional accidental (#/b/##/bb); scale data uses all four
NOTE_RE = r'[A-G](?:##|#|bb|b)?'

# harmony: each mode is a rotation of the major-scale step pattern
MAJOR_STEPS = [2, 2, 1, 2, 2, 2, 1]
MODE_OFFSETS = {'major': 0, 'dorian': 1, 'phrygian': 2, 'lydian': 3,
                'mixolydian': 4, 'minor': 5, 'aeolian': 5, 'locrian': 6}

# the note that makes each mode sound like itself: (scale degree index, name, how to use it)
COLOR_NOTES = {
    'major': (6, 'the 7th', 'bright and settled; let it pull you home to the root'),
    'minor': (5, 'the b6', 'the ache; sit on it, then fall to the 5th'),
    'aeolian': (5, 'the b6', 'the ache; sit on it, then fall to the 5th'),
    'dorian': (5, 'the natural 6', 'bittersweet lift; minor with a window open'),
    'phrygian': (1, 'the b2', 'the dark half-step; lean on it over the root'),
    'lydian': (3, 'the #4', 'the float; hold it over the tonic and let it hang'),
    'mixolydian': (6, 'the b7', 'bluesy swagger; major that refuses to resolve'),
    'locrian': (4, 'the b5', 'the tritone; dread, resolve nothing'),
}

# characteristic chord movements per mode, as 0-based scale degrees + a nickname
MOVEMENTS = {
    'major': [((0, 4, 5, 3), 'the open road'), ((0, 3, 0, 4), 'hymn and home'),
              ((0, 5, 3, 4), 'doo-wop wheel'), ((3, 0, 4, 5), 'lift-off, soft landing'),
              ((0, 2, 3, 0), 'sunlit side-step')],
    'aeolian': [((0, 5, 2, 6), 'epic minor climb'), ((0, 3, 4, 0), 'the old lament'),
                ((0, 6, 5, 6), 'descending shuffle'), ((0, 5, 3, 4), 'brooding pull'),
                ((0, 3, 6, 2), 'night drive')],
    'dorian': [((0, 3), 'the dorian vamp'), ((0, 1, 0, 1), 'soul shimmer'),
               ((0, 6, 3, 0), 'folk-rock swagger'), ((0, 2, 3, 0), 'jazz-funk walk')],
    'phrygian': [((0, 1), 'the phrygian lean'), ((0, 1, 2, 1), 'desert heat'),
                 ((0, 6, 5, 1), 'flamenco fall'), ((0, 1, 0, 6), 'doom creep')],
    'lydian': [((0, 1), 'the floating lift'), ((0, 1, 6, 0), 'film-score wonder'),
               ((0, 4, 1, 0), 'starlight sway'), ((0, 1, 2, 1), 'weightless climb')],
    'mixolydian': [((0, 6, 3, 0), 'backyard anthem'), ((0, 4, 3, 0), 'loose-limbed rock'),
                   ((0, 6, 0), 'two-chord swagger'), ((0, 3, 6, 3), 'jam-band roll')],
    'locrian': [((0, 1), 'the cliff edge'), ((0, 1, 2, 1), 'unresolved dread'),
                ((0, 4, 1, 0), 'broken tritone'), ((0, 5, 6, 0), 'fog descending')],
}
MOVEMENTS['minor'] = MOVEMENTS['aeolian']

ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']


def mode_chords(scale, mode):
    # diatonic triads for a scale, named with the scale's own spelling
    notes = re.findall(NOTE_RE, scale)
    offset = MODE_OFFSETS[mode]
    steps = MAJOR_STEPS[offset:] + MAJOR_STEPS[:offset]
    semis = [sum(steps[:i]) for i in range(7)]
    major_semis = [sum(MAJOR_STEPS[:i]) for i in range(7)]
    chords, numerals = [], []
    for i in range(7):
        third = (semis[(i + 2) % 7] - semis[i]) % 12
        fifth = (semis[(i + 4) % 7] - semis[i]) % 12
        suffix = '' if third == 4 else ('m' if fifth == 7 else '°')
        accidental = {-1: 'b', 1: '#'}.get(semis[i] - major_semis[i], '')
        numeral = ROMAN[i] if suffix == '' else ROMAN[i].lower()
        chords.append(notes[i] + suffix)
        numerals.append(accidental + numeral + ('°' if suffix == '°' else ''))
    return chords, numerals


LETTER_PITCH = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def pitch_class(note):
    # 0-11, so enharmonic spellings (Gb / F#) compare equal
    return (LETTER_PITCH[note[0]] + note.count('#') - note.count('b')) % 12
