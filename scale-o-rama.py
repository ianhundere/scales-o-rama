import random
import itertools
import re

scales = {
    'major': ['CDEFGAB', 'GABCDEF#', 'DEF#GABC#', 'ABC#DEF#G#', 'EF#G#ABC#D#',
              'BC#D#EF#G#A#', 'F#G#A#BC#D#E#', 'DbEbFGbAbBbC', 'AbBbCDbEbFG',
              'EbFGAbBbCD', 'BbCDEbFGA', 'FGABbCDE'],
    'minor': ['CDEbFGAbBb', 'GABbCDEbF', 'DEFGABbC', 'ABCDEFG', 'EF#GABCD',
              'BC#DEF#GA', 'F#G#ABC#DE', 'C#D#EF#G#AB', 'G#A#BC#D#EF#',
              'EbFGbAbBbCbDb', 'BbCDbEbFGbAb', 'FGAbBbCDbEb'],
    'dorian': ['CDEbFGABb', 'C#D#EF#G#A#B', 'DEFGABC', 'D#FF#G#A#CC#', 'EF#GABC#D',
               'FGAbBbCDEb', 'F#G#ABC#D#E', 'GABbCDEF', 'G#A#BC#D#FF#', 'ABCDEF#G',
               'A#CC#D#FGG#', 'BC#DEF#G#A'],
    'phrygian': ['CDbEbFGAbBb', 'C#DEF#G#AB', 'DEbFGABbC', 'D#EF#G#A#BC#',
                 'EFGABCD', 'FF#G#A#CC#D#', 'F#GABC#DE', 'GG#A#CDD#F',
                 'G#ABC#D#EF#', 'ABbCDEFG', 'A#BC#D#FF#G#', 'BCDEF#GA'],
    'lydian': ['CDEF#GAB', 'C#D#FGG#A#C', 'DEF#G#ABC#', 'D#FGAA#CD', 'EF#G#A#BC#D#', 'FGABCDE', 'F#G#A#CC#D#F', 'GABC#DEF#', 'G#A#CDD#FG',
               'ABC#D#EF#G#', 'BbCDEFGA', 'BC#D#FF#G#A#'],
    'mixolydian': ['CDEFGABb', 'C#D#E#F#G#A#B', 'DEF#GABC', 'D#E#F##G#A#B#C#',
                   'EF#G#ABC#D', 'FGABbCDEb', 'F#G#A#BC#D#E', 'GABCDEF',
                   'G#A#B#C#D#E#F#', 'ABC#DEF#G', 'A#B#C##D#E#F##G#',
                   'BC#D#EF#G#A'],
    'aeolian': ['CDEbFGAbBb', 'C#D#EF#G#AB', 'DEFGABbC', 'EbFGbAbBbCbDb', 'EF#GABCD',
                'FGAbBbCDbEb', 'F#G#ABC#DE', 'GABbCDEbF', 'G#A#BC#D#EF#', 'ABCDEFG',
                'BbCDbEbFGbAb', 'BC#DEF#GA'],
    'locrian': ['CC#D#FF#G#A#', 'C#DEF#GAB', 'DD#FGG#A#C', 'EbEF#G#ABC#', 'EFGABbCD',
                'FF#G#A#BC#D#', 'F#GABCDE', 'GG#A#CC#D#F', 'G#ABC#DEF#', 'AA#CDD#FG',
                'A#BC#D#EF#G#', 'BCDEFGA'],
}

# one note: A-G + optional accidental (#/b/##/bb); current data only reaches ##, bb kept for input symmetry
NOTE_RE = r'[A-G](?:##|#|bb|b)?'

# data tables for the song mode songwriting challenge
TIME_SIGNATURES = ['4/4', '3/4', '6/8', '5/4', '7/8', '12/8']

STRUCTURES = ['AABA', 'ABAB', 'verse-chorus-bridge', 'through-composed', 'AABABCB']

MOODS = ['wistful', 'triumphant', 'melancholy', 'frantic', 'dreamy', 'menacing',
         'playful', 'nostalgic', 'serene', 'restless', 'euphoric', 'somber']

CONSTRAINTS = ['limit yourself to 3 instruments', 'no cymbals',
               'loop one 2-bar idea', 'write it in one take',
               'use no more than 4 chords', 'leave a 4-bar silence somewhere',
               'every section must change dynamics', 'no lyrics allowed',
               'build the whole thing from one motif', 'end on an unresolved chord']


def generate_challenge():
    # pick a mode key first so we keep it, then a scale within that mode
    mode = random.choice(list(scales.keys()))
    scale = random.choice(scales[mode])
    match = re.match(NOTE_RE, scale)
    root = match.group() if match else scale[:1]
    return {
        'scale': scale,
        'root': root,
        'mode': mode,
        'tempo': random.randint(60, 180),
        'time_sig': random.choice(TIME_SIGNATURES),
        'structure': random.choice(STRUCTURES),
        'mood': random.choice(MOODS),
        'constraint': random.choice(CONSTRAINTS),
    }


if __name__ == '__main__':
    whatFunc = input('Choose random, lookup, or song? ').lower()

    while whatFunc not in ('random', 'r', 'lookup', 'l', 'song', 's'):
        whatFunc = input('Please choose only random, lookup, or song. ').lower()

    if whatFunc in ('lookup', 'l'):
        query = re.findall(NOTE_RE, input('Input notes you\'d like to lookup: '))
        if not query:
            print('No valid notes entered.')
        else:
            # match on parsed note tokens so 'C' doesn't accidentally match 'C#'
            matches = []
            for key, group in scales.items():
                for scale in group:
                    if all(note in re.findall(NOTE_RE, scale) for note in query):
                        matches.append((key, scale))
            if matches:
                for key, scale in matches:
                    print('{}: {}'.format(key, scale))
            else:
                print('No scales contain those notes.')

    elif whatFunc in ('random', 'r'):
        whatScales = input(
            'Choose Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian, or All: ').lower()
        # ^asks user to choose from keys in dict

        while whatScales not in ('minor', 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian', 'all'):
            whatScales = input(
                'Sorry, invalid choice. Choose only from Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian, or All: ').lower()
        # if the user chooses an incorrect choice, it reiterates the question/choices

        if whatScales in scales:
            print(random.choice(scales[whatScales]))
            print('That\'s a nice sounding {} scale!'.format(whatScales))
        elif whatScales == 'all':
            # dedupe by note content so enharmonic duplicates (e.g. minor == aeolian) aren't double-weighted
            print(random.choice(list(set(itertools.chain.from_iterable(scales.values())))))
            print('That\'s a nice sounding random scale!')

    elif whatFunc in ('song', 's'):
        # song mode hands back a full songwriting brief, not just a scale
        challenge = generate_challenge()
        print('--- Your Songwriting Challenge ---')
        print('Scale:      {} {} ({})'.format(
            challenge['root'], challenge['mode'].capitalize(), challenge['scale']))
        print('Tempo:      {} BPM'.format(challenge['tempo']))
        print('Time sig:   {}'.format(challenge['time_sig']))
        print('Structure:  {}'.format(challenge['structure']))
        print('Mood:       {}'.format(challenge['mood']))
        print('Constraint: {}'.format(challenge['constraint']))
        print('Now go write something!')
