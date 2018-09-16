import random

scales = {'Major': ['C, D, E, F, G, A, B', 'G, A, B, C, D, E, F#', 'D, E, F#, G, A, B, C#', 'A, B, C#, D, E, F#, G#', 'E, F#, G#, A, B, C#, D#', 
'B, C#, D#, E, F#, G#, A#', 'F#, G#, A#, B, C#, D#, E#', 'Db, Eb, F, Gb, Ab, Bb, C', 'Ab, Bb, C, Db, Eb, F, G', 'Eb, F, G, Ab, Bb, C, D', 
'Bb, C, D, Eb, F, G, A', 'F, G, A, Bb, C, D, E'], 'Minor': ['C, D, Eb, F, G, Ab, Bb', 'G, A, Bb, C, D, Eb, F', 'D, E, F, G, A, Bb, C', 'A, B, C, D, E, F, G', 'E, F#, G, A, B, C, D', 
'B, C#, D, E, F#, G, A', 'F#, G#, A, B, C#, D, E', 'C#, D#, E, F#, G#, A, B', 'G#, A#, B, C#, D#, E, F#', 'Eb, F, Gb, Ab, Bb, Cb, Db', 'Bb, C, Db, Eb, F, Gb, Ab', 'F, G, Ab, Bb, C, Db, Eb']}

whatScales = str(input('Choose Major or Minor: ')).lower()

while whatScales.lower() not in ('minor', 'major'):
    whatScales = str(input('Choose only from Major or Minor: ')).lower()

if whatScales in ['major']:
    print(random.choice(scales['Major']))
    print('That\'s a nice sounding major scale!')
     
elif whatScales in ['minor']:
    print(random.choice(scales['Minor']))
    print('That\'s a nice sounding minor scale!')
     
