import random
import itertools

scales = {'major': ['C, D, E, F, G, A, B', 'G, A, B, C, D, E, F#', 'D, E, F#, G, A, B, C#', 'A, B, C#, D, E, F#, G#', 'E, F#, G#, A, B, C#, D#', 
'B, C#, D#, E, F#, G#, A#', 'F#, G#, A#, B, C#, D#, E#', 'Db, Eb, F, Gb, Ab, Bb, C', 'Ab, Bb, C, Db, Eb, F, G', 'Eb, F, G, Ab, Bb, C, D', 'Bb, C, D, Eb, F, G, A', 'F, G, A, Bb, C, D, E'], 
'minor': ['C, D, Eb, F, G, Ab, Bb', 'G, A, Bb, C, D, Eb, F', 'D, E, F, G, A, Bb, C', 'A, B, C, D, E, F, G', 'E, F#, G, A, B, C, D', 'B, C#, D, E, F#, G, A', 'F#, G#, A, B, C#, D, E', 
'C#, D#, E, F#, G#, A, B', 'G#, A#, B, C#, D#, E, F#', 'Eb, F, Gb, Ab, Bb, Cb, Db', 'Bb, C, Db, Eb, F, Gb, Ab', 'F, G, Ab, Bb, C, Db, Eb'], 'dorian': ['C, D, Eb, F, G, A, Bb', 
'C#, D#, E, F#, G#, A#, B', 'D, E, F, G, A, B, C', 'D#, F, F#, G#, A#, C, C#', 'E, F#, G, A, B, C#, D', 'F, G, Ab, Bb, C, D, Eb', 'F#, G#, A, B, C#, D#, E', 
'G, A, Bb, C, D, E, F', 'G#, A#, B, C#, D#, F, F#', 'A, B, C, D, E, F#, G', 'A#, C, C#, D#, F, G, G#', 'B, C#, D, E, F#, G#, A'], 'phrygian': ['C, Db, Eb, F, G, Ab, Bb', 
'C#, D, E, F#, G#, A, B', 'D, Eb, F, G, A, Bb, C', 'D#, E, F#, G#, A#, B, C#', 'E, F, G, A, B, C, D', 'F, F#, G#, A#, C, C#, D#', 'F#, G, A, B, C#, D, E', 'G, G#, A#, C, D, D#, F', 
'G#, A, B, C#, D#, E, F#', 'A, Bb, C, D, E, F, G', 'A#, B, C#, D#, F, F#, G#', 'B, C, D, E, F#, G, A'], 'lydian': ['C, D, E, F#, G, A, B', 'C#, D#, F, G, G#, A#, C', 'D, E, F#, G#, A, B, C#', 
'D#, F, G, A, A#, C, D', 'E, F#, G#, A#, B, C#, D#', 'F, G, A, B, C, D, E', 'F#, G#, A#, C, C#, D#, F', 'G, A, B, C#, D, E, F#,', 'G#, A#, C, D, D#, F, G', 'A, B, C#, D#, E, F#, G#', 
'Bb, C, D, E, F, G, A', 'B, C#, D#, F, F#, G#, A#'], 'mixolydian': ['C, D, E, F, G, A, Bb', 'C#, D#, E#, F#, G#, A#, B', 'D, E, F#, G, A, B, C', 'D#, E#, F##, G#, A#, B#, C#', 
'E, F#, G#, A, B, C#, D', 'F, G, A, Bb, C, D, Eb', 'F#, G#, A#, B, C#, D#, E', 'G, A, B, C, D, E, F', 'G#, A#, B#, C#, D#, E#, F#', 'A, B, C#, D, E, F#, G', 'A#, B#, C##, D#, E#, F##, G#', 
'B, C#, D#, E, F#, G#, A'], 'aeolian': ['C, D, Eb, F, G, Ab, Bb', 'C#, D#, E, F#, G#, A, B', 'D, E, F, G, A, Bb, C', 'Eb, F, Gb, Ab, Bb, Cb, Db', 'E, F#, G, A, B, C, D', 'F, G, Ab, Bb, C, Db, Eb', 
'F#, G#, A, B, C#, D, E', 'G, A, Bb, C, D, Eb, F', 'G#, A#, B, C#, D#, E, F#', 'A, B, C, D, E, F, G', 'Bb, C, Db, Eb, F, Gb, Ab', 'B, C#, D, E, F#, G, A'], 'locrian': ['C, C#, D#, F, F#, G#, A#', 
'C#, D, E, F#, G, A, B', 'D, D#, F, G, G#, A#, C', 'Eb, E, F#, G#, A, B, C#', 'E, F, G, A, Bb, C, D', 'F, F#, G#, A#, B, C#, D#', 'F#, G, A, B, C, D, E', 'G, G#, A#, C, C#, D#, F', 
'G#, A, B, C#, D, E, F#', 'A, A#, C, D, D#, F, G', 'A#, B, C#, D#, E, F#, G#', 'B, C, D, E, F, G, A']}

whatScales = input('Choose Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian, or All: ').lower() 

#^asks user to choose from keys in dict

while whatScales.lower() not in ('minor', 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian', 'all'):
    whatScales = input('Sorry, invalid choice. Choose only from Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian, or All: ').lower()

#if the user chooses an incorrect choice, it reiterates the question/choices

for key in scales.keys():  # a for loop that looks for the key variable in the scales dictionary to match with the correct key of the scales dictionary.
    if whatScales in key:   # if the user's answer (whatScales) is in the .
        print(random.choice(scales[key]))
        print('That\'s a nice sounding {} scale!'.format(key))
if whatScales in ['all']:
    print(random.choice(list(itertools.chain.from_iterable(scales.values()))))
    print('That\'s a nice sounding random scale!')

#^ an if statement that points the user's answer to the correct key. the final elif statement uses itertools to flatten the dictionary into values to then randomize
