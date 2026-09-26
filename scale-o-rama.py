import argparse
import datetime
import json
import os
import random
import itertools
import re
import sys

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
    'lydian': ['CDEF#GAB', 'C#D#E#F##G#A#B#', 'DEF#G#ABC#', 'D#E#F##G##A#B#C##', 'EF#G#A#BC#D#', 'FGABCDE', 'F#G#A#B#C#D#E#', 'GABC#DEF#', 'G#A#B#C##D#E#F##',
               'ABC#D#EF#G#', 'BbCDEFGA', 'BC#D#E#F#G#A#'],
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

# data tables for the song mode songwriting challenge
TIME_SIGNATURES = ['4/4', '3/4', '6/8', '5/4', '7/8', '12/8']

STRUCTURES = ['AABA', 'ABAB', 'verse-chorus-bridge', 'through-composed', 'AABABCB']

MOODS = ['wistful', 'triumphant', 'melancholy', 'frantic', 'dreamy', 'menacing',
         'playful', 'nostalgic', 'serene', 'restless', 'euphoric', 'somber']

CONSTRAINTS = ['limit yourself to 3 instruments', 'no cymbals',
               'loop one 2-bar idea', 'write it in one take',
               'use no more than 4 chords', 'leave a 4-bar silence somewhere',
               'every section must change dynamics', 'no lyrics allowed',
               'build the whole thing from one motif', 'end on an unresolved chord',
               'the melody may only use 5 notes of the scale', 'no chord lasts less than 2 bars',
               'nothing louder than the vocal (or lead)', 'finish a rough sketch in 30 minutes']

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

HARMONIC_RHYTHMS = ['one chord per bar', 'two bars per chord',
                    'change chords on the and-of-4, ahead of the bar',
                    'hold the root as a pedal under every chord',
                    'stay on the first chord until it hurts, then move',
                    'chords only change when the melody rests']

GROOVES = ['lazy swing, everything slightly behind the beat', 'half-time feel',
           'four-on-the-floor, but the kick drops out every 8 bars',
           'syncopated 3-3-2 pulse', 'no kick drum; the bass carries the pulse',
           'shuffle', 'a 3-against-4 polyrhythm somewhere', 'rubato intro, then a locked groove',
           'the rhythm lives only in an arpeggio', 'push every downbeat a 16th early',
           'chopped breakbeat under slow chords', 'straight 8ths, dead simple, hypnotic']

TEXTURES = ['tape-saturated and warm', 'glassy FM bells', 'bitcrushed dust',
            'huge reverb wash', 'dry and close, no reverb at all', 'granular shimmer',
            'detuned chorus haze', 'lo-fi cassette wobble', 'bright transients, dark tails',
            'a field recording bed under everything', 'everything through a guitar amp',
            'mono and narrow, like an old radio', 'breathy and airy', 'metallic and cold']

ARCS = ['slow build, sudden drop, sparse outro',
        'start at full energy and strip away one element per section',
        'first half acoustic, second half electronic', 'one long crescendo, no breakdown',
        'false ending, then the real hook', 'a loop that mutates every 8 bars, no repeats',
        'build, collapse, rebuild bigger', 'begin with the ending',
        'the intro comes back as the bridge', 'quiet-loud-quiet']

INSTRUMENTS = ['upright piano', 'analog mono synth', 'nylon guitar', 'drum machine',
               'tape-looped voice', 'something bowed', 'toy keyboard', 'hand percussion',
               'Rhodes', 'modular bleeps', 'string section', 'found-object percussion',
               'sub bass', 'vocoder', 'clean electric guitar', 'mellotron flute',
               'brass stabs', 'music box', 'fuzz bass', 'choir pad']

PRODUCTION = ['one reverb bus for everything', 'mix in mono until the very end',
              'sidechain something unexpected to the kick',
              'resample the whole loop and build part two from the audio',
              'no EQ; fix it with arrangement', 'automate one filter across the whole song',
              'print every effect, no undo', 'bounce each part to audio after one take',
              'pitch one element down an octave and make it the lead',
              'every sound must come from one source recording']

# original oblique-style cards, for when you get stuck
WILDCARDS = ['mute the part you love most and see what is left',
             'what would this sound like from the next room?',
             'turn the chorus idea into the intro', 'reverse the most important sound',
             'make the quietest sound the hook', 'let the bass write the melody',
             'sing it before you play it', 'record the room, not the instrument',
             'the mistake you keep hearing is the idea', 'halve the tempo of one part only',
             'give the drums a melody', 'what if it had to be played by a child?',
             'take the busiest bar and delete half of it', 'repeat it until it changes meaning']

FIRST_MOVES = ['loop {movement} on the {instrument} for ten minutes; keep the best pass',
               'hum a melody over a {root} drone that keeps landing on {color_note}',
               'program the groove first, then find a bass line using only {root} and {color_note}',
               'play {first_chord} for one full minute and let a melody come out of it',
               'record 8 bars of the {instrument} with your eyes closed, then build around it',
               'write the hook around {color_note} before anything else exists']

TITLE_WORDS = (['paper', 'velvet', 'broken', 'slow', 'neon', 'hollow', 'salt', 'quiet',
                'copper', 'midnight', 'golden', 'feral', 'glass', 'borrowed'],
               ['lanterns', 'weather', 'satellites', 'harbor', 'orchard', 'signals',
                'afterglow', 'machines', 'tides', 'cathedral', 'static', 'ghosts',
                'motel', 'engines'])

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


def _pick_scale(mode=None, key=None):
    # mode is random unless pinned; key matches a scale root by pitch class
    mode = mode or random.choice(list(scales.keys()))
    group = scales[mode]
    if key:
        group = [s for s in group if pitch_class(re.match(NOTE_RE, s).group()) == pitch_class(key)]
    return mode, random.choice(group)


def _roll_progression(c):
    degrees, nickname = random.choice(MOVEMENTS[c['mode']])
    _, numerals = mode_chords(c['scale'], c['mode'])
    c['progression'] = {'numerals': ' - '.join(numerals[d] for d in degrees),
                        'chords': ' '.join(c['chords'][d] for d in degrees), 'name': nickname}
    c['harmonic_rhythm'] = random.choice(HARMONIC_RHYTHMS)


def _roll_scale(c, mode=None, key=None):
    # scale & harmony group: mode, scale, root, chords, color note, progression
    mode, scale = _pick_scale(mode, key)
    notes = re.findall(NOTE_RE, scale)
    color_index, color_name, color_use = COLOR_NOTES[mode]
    c['mode'], c['scale'], c['root'] = mode, scale, notes[0]
    c['chords'] = mode_chords(scale, mode)[0]
    c['color_note'] = notes[color_index]
    c['color'] = '{} ({}): {}'.format(notes[color_index], color_name, color_use)
    _roll_progression(c)


def _roll_palette(c):
    # palette, production & constraints group
    c['palette'] = random.sample(INSTRUMENTS, 3)
    c['texture'] = random.choice(TEXTURES)
    c['production'] = random.choice(PRODUCTION)
    c['constraint'] = random.choice(CONSTRAINTS)
    c['wildcard'] = random.choice(WILDCARDS)


def _roll_first_move(c):
    # refilled after every reroll so it only names what is in the brief
    c['first_move'] = random.choice(FIRST_MOVES).format(
        movement=c['progression']['chords'], instrument=c['palette'][0], root=c['root'],
        color_note=c['color_note'], first_chord=c['progression']['chords'].split()[0])


def generate_challenge(mode=None, key=None, mood=None, tempo=None):
    # any filter given is pinned; everything else is rolled at random
    c = {
        'tempo': tempo if tempo is not None else random.randint(60, 180),
        'time_sig': random.choice(TIME_SIGNATURES),
        'structure': random.choice(STRUCTURES),
        'mood': mood if mood is not None else random.choice(MOODS),
        'groove': random.choice(GROOVES),
        'arc': random.choice(ARCS),
        'title': '{} {}'.format(*(random.choice(words) for words in TITLE_WORDS)),
    }
    _roll_scale(c, mode, key)
    _roll_palette(c)
    _roll_first_move(c)
    return c


def reroll(c, part, mode=None, key=None, mood=None, tempo=None):
    # 'all' is a fresh brief; 's'/'c'/'p' reroll one group of a copy, plus first_move
    if part == 'all':
        return generate_challenge(mode=mode, key=key, mood=mood, tempo=tempo)
    c = dict(c)
    if part == 's':
        _roll_scale(c, mode, key)
    elif part == 'c':
        _roll_progression(c)
    elif part == 'p':
        _roll_palette(c)
    else:
        raise ValueError('unknown reroll part: {!r}'.format(part))
    _roll_first_move(c)
    return c


def format_challenge(c):
    line = '{:<12}{}'.format
    prog = c['progression']
    return '\n'.join([
        '--- song guide ---',
        line('Scale:', '{} {} ({})'.format(c['root'], c['mode'].capitalize(), c['scale'])),
        line('Color note:', c['color']),
        line('Chords:', '  '.join(c['chords'])),
        line('Movement:', '{}  ->  {}  ("{}")'.format(prog['numerals'], prog['chords'], prog['name'])),
        line('Harmony:', c['harmonic_rhythm']),
        '',
        line('Tempo:', '{} BPM'.format(c['tempo'])),
        line('Time sig:', c['time_sig']),
        line('Groove:', c['groove']),
        '',
        line('Structure:', c['structure']),
        line('Arc:', c['arc']),
        line('Mood:', c['mood']),
        line('Texture:', c['texture']),
        '',
        line('Palette:', ', '.join(c['palette'])),
        line('Production:', c['production']),
        line('Constraint:', c['constraint']),
        line('Wildcard:', c['wildcard']),
        '',
        line('First move:', c['first_move']),
        line('Title:', '"{}"'.format(c['title'])),
    ])


# EJB rig's harmony.mode enum has no 'major'/'minor'; map them to the modal names
EJB_MODES = {'major': 'ionian', 'minor': 'aeolian'}


def ejb_snippet(c):
    # SuperCollider seed for the EJB rig, using its real state API
    num, denom = c['time_sig'].split('/')
    prog = c['progression']
    return '\n'.join([
        '// EJB piece seed generated by scales-o-rama: {}'.format(json.dumps(c['title'])),
        '~stateSet.([\\harmony, \\root], {});  // {}'.format(pitch_class(c['root']), c['root']),
        '~stateSet.([\\harmony, \\mode], "{}");'.format(EJB_MODES.get(c['mode'], c['mode'])),
        '~composeSetMeter.({}, {});'.format(int(num), int(denom)),
        '~clockSetTempo.({});'.format(c['tempo']),
        '// Progression: {} -> {}'.format(prog['numerals'], prog['chords']),
    ])


def format_sketch(c, date, ejb=False):
    # markdown sketch: frontmatter, the brief, optional EJB seed, then room for notes
    q = json.dumps
    lines = ['---',
             'date: {}'.format(date.isoformat()),
             'title: {}'.format(q(c['title'])),
             'scale: {}'.format(q(c['scale'])),
             'root: {}'.format(q(c['root'])),
             'mode: {}'.format(q(c['mode'])),
             'tempo: {}'.format(int(c['tempo'])),
             'time_sig: {}'.format(q(c['time_sig'])),
             '---', '',
             '# {}'.format(c['title']), '',
             '## Brief', '', '```', format_challenge(c), '```', '']
    if ejb:
        lines += ['## EJB seed', '', '```supercollider', ejb_snippet(c), '```', '']
    lines += ['## Notes / lyrics', '', '']
    return '\n'.join(lines)


def save_sketch(c, directory='sketches', ejb=False, today=None):
    # writes sketches/YYYY-MM-DD-<slug>.md, never overwriting (-2, -3, ...); returns the path
    today = today or datetime.date.today()
    slug = re.sub(r'[^a-z0-9]+', '-', c['title'].lower()).strip('-') or 'sketch'
    base = os.path.join(directory, '{}-{}'.format(today.isoformat(), slug))
    os.makedirs(directory, exist_ok=True)
    text = format_sketch(c, today, ejb=ejb)
    n = 1
    while True:
        path = base + ('.md' if n == 1 else '-{}.md'.format(n))
        try:
            with open(path, 'x', encoding='utf-8') as f:
                f.write(text)
            return path
        except FileExistsError:
            n += 1


def _mode_arg(value):
    mode = value.lower()
    if mode not in scales:
        raise argparse.ArgumentTypeError('invalid mode {!r} (choose from {})'.format(
            value, ', '.join(scales)))
    return mode


def _key_arg(value):
    key = value[:1].upper() + value[1:].lower()
    if not re.fullmatch(NOTE_RE, key):
        raise argparse.ArgumentTypeError('invalid key {!r} (e.g. C, F#, Bb)'.format(value))
    return key


def _tempo_arg(value):
    try:
        tempo = int(value)
    except ValueError:
        tempo = 0
    if tempo <= 0:
        raise argparse.ArgumentTypeError('invalid tempo {!r} (a positive whole BPM)'.format(value))
    return tempo


def _mood_arg(value):
    if not value.strip():
        raise argparse.ArgumentTypeError('mood cannot be empty')
    return value.strip()


REROLL_PROMPT = '[enter/r] reroll all  [s] scale  [c] chords  [p] palette  [w] write  [q] quit: '
REROLL_KEYS = {'': 'all', 'r': 'all', 's': 's', 'c': 'c', 'p': 'p'}


def run_song(argv):
    parser = argparse.ArgumentParser(prog='som song', description='Roll a songwriting brief.')
    parser.add_argument('--mode', type=_mode_arg, help='pin the mode, e.g. dorian')
    parser.add_argument('--key', '--root', dest='key', type=_key_arg, help='pin the root, e.g. F# or Bb')
    parser.add_argument('--mood', type=_mood_arg, help='pin the mood (any text)')
    parser.add_argument('--tempo', type=_tempo_arg, help='pin the tempo in BPM')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='show the reroll prompt even when not in a terminal')
    parser.add_argument('--save', '--export', dest='save', action='store_true',
                        help='write the brief to sketches/YYYY-MM-DD-<title>.md')
    parser.add_argument('--ejb', action='store_true',
                        help='print a SuperCollider seed for the EJB rig (and add it to sketches)')
    args = parser.parse_args(argv)
    filters = {'mode': args.mode, 'key': args.key, 'mood': args.mood, 'tempo': args.tempo}

    def show(c):
        print(format_challenge(c))
        if args.ejb:
            print()
            print(ejb_snippet(c))

    def write(c):
        # returns False (after reporting) instead of raising, so no traceback
        try:
            path = save_sketch(c, ejb=args.ejb)
        except OSError as e:
            print('could not save sketch: {}'.format(e), file=sys.stderr)
            return False
        print('saved sketch: {}'.format(path))
        return True

    challenge = generate_challenge(**filters)
    show(challenge)
    if args.save and not write(challenge):
        sys.exit(1)
    if not (args.interactive or (sys.stdin.isatty() and sys.stdout.isatty())):
        return
    while True:
        try:
            choice = input('\n' + REROLL_PROMPT).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if choice == 'q':
            return
        if choice in ('w', 'write'):
            write(challenge)
            continue
        part = REROLL_KEYS.get(choice)
        if part is None:
            print('unknown choice: {!r}'.format(choice))
            continue
        challenge = reroll(challenge, part, **filters)
        show(challenge)


if __name__ == '__main__':
    # optional first arg skips the selector prompt, e.g. `som song`
    whatFunc = sys.argv[1].lower() if len(sys.argv) > 1 else input('Choose random, lookup, or song? ').lower()

    while whatFunc not in ('random', 'r', 'lookup', 'l', 'song', 's'):
        whatFunc = input('Please choose only random, lookup, or song. ').lower()

    if whatFunc in ('lookup', 'l'):
        notes_in = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else input('Input notes you\'d like to lookup: ')
        query = re.findall(NOTE_RE, notes_in)
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
        whatScales = sys.argv[2].lower() if len(sys.argv) > 2 else input(
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
        run_song(sys.argv[2:])
