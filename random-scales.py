import random
import itertools
import re
from pprint import pprint

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
    'lydian': ['CDEF#GAB', 'C#D#FGG#A#C', 'DEF#G#ABC#', 'D#FGAA#CD', 'EF#G#A#BC#D#', 'FGABCDE', 'F#G#A#CC#D#F', 'GABC#DEF#,', 'G#A#CDD#FG',
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

whatFunc = input('Choose random or lookup? ').lower()

while whatFunc not in ('random', 'lookup'):
    whatFunc = input('Please choose only random or lookup. ').lower()

if whatFunc == 'lookup':
    notes = input('Input notes you\'d like to lookup: ')

    notes = re.findall(r'[A-G][#b]?', notes)
    matches = []
    for key in scales.keys():
        for scale in scales[key]:
            for note in notes:
                if note not in scale:
                    break
            else:
                matches.append([key, scale])

    pprint(matches)

elif whatFunc == 'random':
    whatScales = input('Choose Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian, or All: ').lower() 

    #^asks user to choose from keys in dict

    while whatScales.lower() not in ('minor', 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian', 'all'):
        whatScales = input('Sorry, invalid choice. Choose only from Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian, or All: ').lower()

    #if the user chooses an incorrect choice, it reiterates the question/choices

    for key in scales.keys():  # a for loop that looks for the key variable in the scales dictionary to match with the correct key of the scales dictionary.
        if whatScales in key:
            print(random.choice(scales[key]))
            print('That\'s a nice sounding {} scale!'.format(key))
    if whatScales in ['all']:
        print(random.choice(list(itertools.chain.from_iterable(scales.values()))))
        print('That\'s a nice sounding random scale!')

    #^ an if statement that points the user's answer to the correct key. the final elif statement uses itertools to flatten the dictionary into values to then randomize
