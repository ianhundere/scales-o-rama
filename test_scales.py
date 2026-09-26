import importlib.util
import os
import random
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(ROOT, 'scale-o-rama.py')

_spec = importlib.util.spec_from_file_location('scale_o_rama', SCRIPT)
som = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(som)

LETTERS = 'CDEFGAB'
BASE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

NUMERALS = {
    'major': 'I ii iii IV V vi vii°',
    'dorian': 'i ii bIII IV v vi° bVII',
    'phrygian': 'i bII bIII iv v° bVI bvii',
    'lydian': 'I II iii #iv° V vi vii',
    'mixolydian': 'I ii iii° IV v vi bVII',
    'minor': 'i ii° bIII iv v bVI bVII',
    'aeolian': 'i ii° bIII iv v bVI bVII',
    'locrian': 'i° bII biii iv bV bVI bvii',
}


def tokens(scale):
    return re.findall(som.NOTE_RE, scale)


def pitch(note):
    return (BASE[note[0]] + note.count('#') - note.count('b')) % 12


def run_cli(*args, stdin=''):
    return subprocess.run([sys.executable, SCRIPT, *args], input=stdin,
                          capture_output=True, text=True, cwd=ROOT, timeout=30)


class NoteReTests(unittest.TestCase):
    def test_double_sharps(self):
        self.assertEqual(tokens('D#E#F##G##A#B#C##'),
                         ['D#', 'E#', 'F##', 'G##', 'A#', 'B#', 'C##'])

    def test_double_flat(self):
        t = tokens('EbFbGbAbBbbCbDb')
        self.assertEqual(len(t), 7)
        self.assertEqual(t[4], 'Bbb')

    def test_round_trip(self):
        for mode, group in som.scales.items():
            for scale in group:
                self.assertEqual(''.join(tokens(scale)), scale, (mode, scale))


class ScaleDataTests(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(set(som.scales),
                         {'major', 'minor', 'dorian', 'phrygian', 'lydian',
                          'mixolydian', 'aeolian', 'locrian'})
        for mode, group in som.scales.items():
            self.assertEqual(len(group), 12, mode)

    def test_letters_distinct_and_in_order(self):
        for mode, group in som.scales.items():
            for scale in group:
                t = tokens(scale)
                self.assertEqual(len(t), 7, (mode, scale))
                start = LETTERS.index(t[0][0])
                expected = [LETTERS[(start + i) % 7] for i in range(7)]
                self.assertEqual([n[0] for n in t], expected, (mode, scale))

    def test_step_pattern(self):
        for mode, group in som.scales.items():
            off = som.MODE_OFFSETS[mode]
            steps = som.MAJOR_STEPS[off:] + som.MAJOR_STEPS[:off]
            for scale in group:
                p = [pitch(n) for n in tokens(scale)]
                got = [(p[(i + 1) % 7] - p[i]) % 12 for i in range(7)]
                self.assertEqual(got, steps, (mode, scale))

    def test_distinct_tonics(self):
        for mode, group in som.scales.items():
            self.assertEqual(len({pitch(tokens(s)[0]) for s in group}), 12, mode)

    def test_minor_equals_aeolian(self):
        self.assertEqual(set(som.scales['minor']), set(som.scales['aeolian']))


class ChordTests(unittest.TestCase):
    def test_all_scales(self):
        for mode, group in som.scales.items():
            for scale in group:
                chords, numerals = som.mode_chords(scale, mode)
                self.assertEqual(len(chords), 7)
                self.assertEqual(numerals, NUMERALS[mode].split(), (mode, scale))
                for chord, note, num in zip(chords, tokens(scale), numerals):
                    if num.endswith('°'):
                        suffix = '°'
                    elif num.lstrip('b#')[0].islower():
                        suffix = 'm'
                    else:
                        suffix = ''
                    self.assertEqual(chord, note + suffix, (mode, scale))

    def test_d_sharp_dorian(self):
        chords, numerals = som.mode_chords('D#E#F#G#A#B#C#', 'dorian')
        self.assertEqual(chords, 'D#m E#m F# G# A#m B#° C#'.split())
        self.assertEqual(numerals, 'i ii bIII IV v vi° bVII'.split())

    def test_d_sharp_lydian(self):
        chords, numerals = som.mode_chords('D#E#F##G##A#B#C##', 'lydian')
        self.assertEqual(chords, 'D# E# F##m G##° A# B#m C##m'.split())
        self.assertEqual(numerals, 'I II iii #iv° V vi vii'.split())


class ChallengeTests(unittest.TestCase):
    KEYS = {'scale', 'root', 'mode', 'tempo', 'time_sig', 'structure', 'mood',
            'constraint', 'color_note', 'color', 'chords', 'progression',
            'harmonic_rhythm', 'groove', 'arc', 'texture', 'palette',
            'production', 'wildcard', 'first_move', 'title'}

    def test_generate_many(self):
        random.seed(12345)
        for _ in range(200):
            c = som.generate_challenge()
            self.assertEqual(set(c), self.KEYS)
            for k, v in c.items():
                self.assertTrue(v, k)
                leaves = v.values() if isinstance(v, dict) else v if isinstance(v, list) else [v]
                for leaf in leaves:
                    self.assertTrue(leaf, k)
                    self.assertNotRegex(str(leaf), r'[{}]', k)
            t = tokens(c['scale'])
            self.assertIn(c['scale'], som.scales[c['mode']])
            self.assertEqual(c['root'], t[0])
            self.assertIn(c['color_note'], t)
            self.assertEqual(set(c['progression']), {'numerals', 'chords', 'name'})


class CliTests(unittest.TestCase):
    def test_lookup_args(self):
        r = run_cli('lookup', 'D#', 'E#')
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertIn('dorian: D#E#F#G#A#B#C#', lines)
        expected = ['{}: {}'.format(key, scale)
                    for key, group in som.scales.items() for scale in group
                    if {'D#', 'E#'} <= set(tokens(scale))]
        self.assertEqual(lines, expected)

    def test_lookup_stdin(self):
        r = run_cli('lookup', stdin='C E G\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        # the input() prompt has no trailing newline, so strip it off the first line
        out = r.stdout.split("lookup: ", 1)[1]
        self.assertIn('major: CDEFGAB', out.splitlines())

    def test_lookup_no_valid_notes(self):
        r = run_cli('lookup', 'xyz')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), 'No valid notes entered.')

    def test_random_arg(self):
        r = run_cli('random', 'dorian')
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertIn(lines[0], som.scales['dorian'])
        self.assertEqual(lines[1], "That's a nice sounding dorian scale!")

    def test_random_stdin_retry(self):
        r = run_cli('random', stdin='nope\nall\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count('Sorry, invalid choice.'), 1)
        all_scales = {s for g in som.scales.values() for s in g}
        # prompts have no trailing newline, so the scale follows the last prompt
        tail = r.stdout.rsplit(': ', 1)[1].splitlines()
        self.assertIn(tail[0], all_scales)
        self.assertEqual(tail[1], "That's a nice sounding random scale!")

    def test_song(self):
        r = run_cli('song')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith('--- song guide ---'))
        self.assertIn('Title:', r.stdout)


if __name__ == '__main__':
    unittest.main()
