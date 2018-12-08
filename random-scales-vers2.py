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

whatScales = str(input('Choose Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian, or All: ')).lower() 

#^asks user to choose from keys in dict

while whatScales.lower() not in ('minor', 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian', 'all'):
    whatScales = str(input('Sorry, invalid choice. Choose only from Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian, or All: ')).lower()

#if the user chooses an incorrect choice, it reiterates the question/choices

if whatScales in ['major']:
    print(random.choice(scales['major']))
    print('That\'s a nice sounding major scale!')
elif whatScales in ['minor']:
    print(random.choice(scales[whatScales]))
    print('That\'s a nice sounding minor scale!')
elif whatScales in ['dorian']:
    print(random.choice(scales[whatScales]))
    print('That\'s a nice sounding dorian scale!')
elif whatScales in ['phrygian']:
    print(random.choice(scales[whatScales]))
    print('That\'s a nice sounding phrygian scale!')
elif whatScales in ['lydian']:
    print(random.choice(scales[whatScales]))
    print('That\'s a nice sounding lydian scale!')
elif whatScales in ['mixolydian']:
    print(random.choice(scales[whatScales]))
    print('That\'s a nice sounding mixolydian scale!')
elif whatScales in ['aeolian']:
    print(random.choice(scales[whatScales]))
    print('That\'s a nice sounding aeolian scale!')
elif whatScales in ['locrian']:
    print(random.choice(scales[whatScales]))
    print('That\'s a nice sounding locrian scale!')
elif whatScales in ['all']:
    print(random.choice(list(itertools.chain.from_iterable(scales.values()))))
    print('That\'s a nice sounding random scale!')

#an if statement that points the user's answer to the correct key. the final elif statement useres itertools to flatten the dictionary into values to then randomize