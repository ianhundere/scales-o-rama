import argparse
import itertools
import random
import re
import sys

from generator import (
    ejb_snippet,
    format_challenge,
    generate_challenge,
    reroll,
    save_sketch,
)
from scales_data import NOTE_RE, scales


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

        while whatScales not in (*scales, 'all'):
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
